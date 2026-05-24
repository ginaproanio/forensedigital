#!/usr/bin/env python3
"""Scrapling — Método 3 (respaldo): Scraping con navegador (Playwright) contra Google Maps.

AVISO LEGAL/TÉCNICO:
- Google Maps puede bloquear automatización y/o cambiar selectores.
- Este script usa selectores actualizados para la UI moderna de Google Maps.
- NO intenta evadir de forma agresiva mecanismos anti-bot; solo automatiza navegación.

Salida esperada (CSV bruto) compatible con `scripts/limpiar_csv.py`:
- nombre
- telefono
- rating_google_maps
- numero_reseñas_google_maps
- categoria
- link_google_maps
- provincia
- email (opcional)

Uso (ejemplo):
  # Local:
  python scripts/extractors_m3_playwright_google_maps.py \
    --output Scrapling/output/abogados-ecuador-abogados.csv \
    --province "Pichincha" \
    --limit 50

  # Docker:
  docker compose run --rm scrapling \
    --output output/abogados.csv \
    --province "Pichincha" \
    --limit 50

Requiere:
- playwright
- navegador instalado: `playwright install chromium`
"""

from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from playwright.sync_api import sync_playwright, Page, ElementHandle

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scrapling")


# ── Modelo de datos ──────────────────────────────────────────────────────
@dataclass
class Lead:
    nombre: str = ""
    telefono: str = ""
    sitio_web: str = ""
    rating_google_maps: str = ""
    numero_reseñas_google_maps: str = ""
    categoria: str = ""
    link_google_maps: str = ""
    provincia: str = ""
    email: str = ""


# ── Utilidades ──────────────────────────────────────────────────────────
def clean_text(s: str | None) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def parse_phone(raw: str) -> str:
    """Extrae solo dígitos y '+' de un texto. Normaliza a +593XXXXXXXXX."""
    if not raw:
        return ""
    # Limpiar todo excepto dígitos y el signo +
    digits = re.sub(r"[^0-9+]", "", raw)
    
    # Si tiene 10 dígitos y empieza por 09 (celular)
    if digits.startswith("09") and len(digits) == 10:
        digits = "+593" + digits[1:]
    # Si tiene 9 dígitos y empieza por 0 (fijo)
    elif digits.startswith("0") and len(digits) == 9:
        digits = "+593" + digits[1:]
    # Si ya tiene el código de país sin el +
    elif digits.startswith("593") and len(digits) >= 11:
        digits = "+" + digits
    # Si tiene 9 dígitos pero no empieza por 0 (celular sin 0)
    elif len(digits) == 9 and digits.startswith("9"):
        digits = "+593" + digits
        
    return digits


def safe_float(text: str) -> str:
    """Extrae el primer número flotante de un texto (ej: 4.5)."""
    t = clean_text(text)
    m = re.search(r"(\d+(?:[.,]\d+)?)", t)
    return m.group(1).replace(",", ".") if m else ""


def safe_int(text: str) -> str:
    """Extrae el primer entero de un texto (sin puntos de miles)."""
    t = clean_text(text)
    m = re.search(r"(\d{1,3}(?:[.,]\d{3})*|\d+)", t)
    if m:
        return m.group(1).replace(".", "").replace(",", "")
    return ""


def build_search_url(province: str) -> str:
    """Construye URL de búsqueda en Google Maps para abogados en una provincia."""
    query = f"abogados en {province}"
    encoded = query.replace(" ", "+")
    return f"https://www.google.com/maps/search/{encoded}/?q={encoded}"


# ── Selectores actualizados para Google Maps (junio 2025) ───────────────
# Estos selectores están basados en la UI actual de Google Maps.
# Si Google cambia su DOM, habrá que actualizarlos.

SELECTORS = {
    # Tarjetas de resultados en la lista lateral
    "result_card": 'a[href*="/maps/place/"]',
    # Título/nombre del lugar en el panel lateral (sidebar)
    "title_h1": "h1",
    # Botón de teléfono
    "phone_button": (
        'button[data-item-id*="phone"], '
        'div[role="button"][data-item-id*="phone"], '
        'a[href^="tel:"], ' # Los enlaces directos tel: son muy fiables
        'button[aria-label*="teléfono"], button[aria-label*="phone"], button[aria-label*="llamar"], button[aria-label*="Llamar"], '
        'div[role="button"][aria-label*="teléfono"], div[role="button"][aria-label*="phone"], div[role="button"][aria-label*="llamar"], div[role="button"][aria-label*="Llamar"], '
        'span[aria-label*="teléfono"], span[aria-label*="phone"], span[aria-label*="llamar"], span[aria-label*="09"], ' # A veces es un span con aria-label o prefijo 09
        'div[data-tooltip*="Llamar"], div[data-tooltip*="Call"], ' # A veces se usa data-tooltip
        'div[jsaction*="phone:"]' # Otro patrón común para números de teléfono
    ),
    # Botón de sitio web
    "website_button": 'a[data-item-id*="authority"], a[href*="http"][data-item-id]',
    # Contenedor de rating (estrella)
    "rating_container": 'div[role="img"][aria-label*="estrella"], div[role="img"][aria-label*="star"]',
    # Botón de reseñas
    "reviews_button": 'button[aria-label*="reseña"], button[aria-label*="review"]',
    # Categoría (a veces está como span dentro de un botón)
    "category_element": 'button[jsaction*="category"] span, div[aria-label*="categoría"]',
}


# ── Estrategias de extracción ──────────────────────────────────────────

def extract_name(page: Page) -> str:
    """Extrae el nombre del lugar desde el panel lateral.
    
    Google Maps tiene múltiples h1. El primero suele ser "Resultados"
    (título de búsqueda). El nombre del lugar está en el panel lateral
    como un h1 más específico o dentro de la sección de detalles.
    """
    # Estrategia 1: buscar h1 que NO sea "Resultados" 
    try:
        h1_elements = page.locator("h1")
        count = h1_elements.count()
        for i in range(count):
            text = clean_text(h1_elements.nth(i).inner_text(timeout=1000))
            # Ignorar títulos genéricos de Google Maps
            if text and text.lower() not in ("resultados", "search results", "", " "):
                return text
    except Exception:
        pass

    # Estrategia 2: esperar un h1 en el panel lateral (el segundo h1)
    try:
        el = page.locator("h1").last
        if el.count() > 0:
            text = clean_text(el.inner_text(timeout=3000))
            if text:
                return text
    except Exception:
        pass

    # Estrategia 3: buscar en el contenedor del panel de detalles
    try:
        # En la UI actual de GMaps, el nombre suele estar en un heading
        # dentro de div[role="main"] o similar
        el = page.locator('div[role="main"] h1, div[role="main"] h2').first
        if el.count() > 0:
            text = clean_text(el.inner_text(timeout=2000))
            if text and text.lower() != "resultados":
                return text
    except Exception:
        pass

    return ""


def extract_phone(page: Page, card_text: str = "") -> str:
    """Extrae el teléfono usando múltiples estrategias."""
    # Google Maps tiene 2 paneles 'main': el listado y el detalle.
    # Apuntamos al último (last) que es el detalle recién abierto.
    main_panels = page.locator('div[role="main"]')
    container = main_panels.last if main_panels.count() > 1 else main_panels.first

    # Estrategia 1: buscar en elementos interactivos (botones, enlaces) dentro del panel activo
    try:
        buttons = container.locator(SELECTORS["phone_button"])
        for i in range(buttons.count()):
            el = buttons.nth(i)
            # Priorizar href para enlaces tel:
            href = el.get_attribute("href")
            if href and href.startswith("tel:"):
                val = parse_phone(href)
                if val: return val

            # Verificar aria-label
            aria = el.get_attribute("aria-label")
            if aria and any(x in aria.lower() for x in ("teléfono", "phone", "llamar", "593", "09")):
                val = parse_phone(aria)
                if val: return val
            
            # Verificar texto interno
            text = el.inner_text(timeout=1000)
            if text and any(d.isdigit() for d in text):
                val = parse_phone(text)
                if val: return val
    except Exception:
        pass

    # Estrategia 2: escanear el texto del panel con regex
    try:
        detail_panel_content = container.inner_text(timeout=2000)
        
        # Buscar celular 09XXXXXXXX
        m = re.search(r"\b(0\s*9(?:\s*\d){8})\b", detail_panel_content)
        if m:
            return parse_phone(m.group())
        # Buscar números fijos o móviles que empiezan con 0X (ej. 02, 03, 04, 09)
        # y tienen 9 o 10 dígitos en total (ej. 02 382-9670, 093 916 1015)
        m = re.search(r"\b(0\s*\d(?:\s*\d){7,8})\b", detail_panel_content)
        if m:
            return parse_phone(m.group())
        # Buscar patrones ecuatorianos +593...
        m = re.search(r"\+?\s*5\s*9\s*3\s*\d[\d\s\-\(\)]{7,}", detail_panel_content)
        if m:
            return parse_phone(m.group())
        # Buscar 9 dígitos consecutivos
        m = re.search(r"\b(\d{9})\b", detail_panel_content)
        if m:
            return parse_phone(m.group())
    except Exception:
        pass

    # Estrategia 3: Fallback al texto de la tarjeta (muy útil si el panel no cargó o info está en la lista)
    if card_text:
        m = re.search(r"\b(0\s*[2-9](?:\s*\d){7,8})\b", card_text)
        if m:
            return parse_phone(m.group())

    return ""


def extract_website(page: Page) -> str:
    """Extrae el sitio web."""
    # Estrategia 1: botón con data-item-id
    try:
        el = page.locator(SELECTORS["website_button"]).first
        if el.count() > 0:
            href = el.get_attribute("href")
            if href and href.startswith("http"):
                return clean_text(href)
            text = el.inner_text(timeout=1000)
            if text and "http" in text.lower():
                return clean_text(text)
    except Exception:
        pass

    # Estrategia 2: buscar http en body
    try:
        body = page.inner_text("body", timeout=2000)
        m = re.search(r"https?://[^\s\)\]\}<>\"']+", body)
        if m:
            return clean_text(m.group())
    except Exception:
        pass

    return ""


def extract_rating(page: Page) -> tuple[str, str]:
    """Extrae rating y número de reseñas. Retorna (rating, reseñas)."""
    rating = ""
    reviews = ""

    # Estrategia 1: contenedor de rating con aria-label
    try:
        el = page.locator(SELECTORS["rating_container"]).first
        if el.count() > 0:
            aria = el.get_attribute("aria-label")
            if aria:
                # aria-label suele ser "4.5 de 5 estrellas"
                m = re.search(r"(\d+(?:[.,]\d+)?)", aria)
                if m:
                    rating = m.group(1).replace(",", ".")
    except Exception:
        pass

    # Estrategia 2: botón de reseñas
    try:
        el = page.locator(SELECTORS["reviews_button"]).first
        if el.count() > 0:
            aria = el.get_attribute("aria-label")
            if aria:
                m = re.search(r"(\d[\d.,]*)", aria)
                if m:
                    reviews = m.group(1).replace(",", "").replace(".", "")
            else:
                text = el.inner_text(timeout=1000)
                if text:
                    m = re.search(r"\((\d[\d.,]*)\)", text)
                    if m:
                        reviews = m.group(1).replace(",", "").replace(".", "")
                    else:
                        m = re.search(r"(\d[\d.,]*)", text)
                        if m:
                            reviews = m.group(1).replace(",", "").replace(".", "")
    except Exception:
        pass

    # Estrategia 3: fallback desde body (muy conservador)
    if not rating or not reviews:
        try:
            body = page.inner_text("body", timeout=2000)
            if not rating:
                m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:de\s*\d+\s*estrellas|stars|puntos)", body, flags=re.IGNORECASE)
                if m:
                    rating = m.group(1).replace(",", ".")
            if not reviews:
                m = re.search(r"\((\d[\d.,]*)\)", body)
                if m:
                    reviews = m.group(1).replace(",", "").replace(".", "")
        except Exception:
            pass

    return rating, reviews


def extract_category(page: Page, nombre: str = "") -> str:
    """Extrae la categoría del lugar."""
    # Estrategia 1: elemento de categoría
    try:
        el = page.locator(SELECTORS["category_element"]).first
        if el.count() > 0:
            text = clean_text(el.inner_text(timeout=2000))
            if text:
                return text
    except Exception:
        pass

    # Estrategia 2: inferir del nombre
    if nombre and re.search(r"abogad|bufete|estudio\s*juríd|legal|attorney", nombre, flags=re.IGNORECASE):
        return "Abogado"

    # Estrategia 3: buscar en body
    try:
        body = page.inner_text("body", timeout=2000)
        m = re.search(r"Categor[íi]a\s*:?\s*(.+)", body, flags=re.IGNORECASE)
        if m:
            return clean_text(m.group(1))
    except Exception:
        pass

    return ""


def wait_for_sidebar(page: Page, timeout: int = 8000) -> bool:
    """Espera a que el panel lateral cargue después de hacer clic en un resultado."""
    try:
        page.wait_for_selector(SELECTORS["title_h1"], timeout=timeout)
        return True
    except Exception:
        return False


# ── Extracción principal ─────────────────────────────────────────────────

def run_extraction(
    output_csv: str,
    provinces: List[str],
    limit: int,
    headless: bool = True,
) -> str:
    """Ejecuta la extracción para una o varias provincias."""
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    all_leads: List[Lead] = []
    total_found = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        for province in provinces:
            log.info("=== Extrayendo %s ===", province)
            url = build_search_url(province)
            log.info("Abriendo: %s", url)

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                log.error("Error al cargar %s: %s", province, e)
                continue

            # Esperar que aparezcan resultados
            try:
                page.wait_for_selector(SELECTORS["result_card"], timeout=15000)
                log.info("Resultados cargados")
            except Exception:
                log.warning("No se detectaron resultados en %s", province)
                continue

            # Pequeña pausa para que termine de renderizar
            time.sleep(2)

            # ── Scroll infinito: cargar más resultados ──────────────
            # Google Maps carga resultados con scroll. Hay que scrollear
            # el panel de resultados (left panel) para activar lazy loading.
            cards = page.locator(SELECTORS["result_card"])
            total_cards = cards.count()
            scroll_attempts = 0
            max_scroll_attempts = 20  # máx 20 scrolls (~200+ tarjetas)

            while total_cards < limit and scroll_attempts < max_scroll_attempts:
                # Scrollear el último resultado visible para cargar más
                try:
                    last_card = cards.nth(total_cards - 1)
                    last_card.scroll_into_view_if_needed()
                    time.sleep(1.5)  # esperar a que carguen nuevos
                    new_count = page.locator(SELECTORS["result_card"]).count()
                    if new_count > total_cards:
                        log.info("  Scroll %d: %d → %d tarjetas", scroll_attempts + 1, total_cards, new_count)
                        total_cards = new_count
                    else:
                        break  # no hay más resultados
                except Exception:
                    break
                scroll_attempts += 1

            log.info("Tarjetas encontradas: %d", total_cards)
            cards = page.locator(SELECTORS["result_card"])
            total_cards = cards.count()
            log.info("Tarjetas confirmadas: %d", total_cards)

            to_take = min(limit, total_cards)
            province_leads = 0

            for i in range(to_take):
                try:
                    card = cards.nth(i)
                    card_text = card.inner_text()
                    card.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    card.click(timeout=10000)

                    # Esperar panel lateral
                    sidebar_loaded = wait_for_sidebar(page, timeout=8000)
                    if not sidebar_loaded:
                        log.warning("  [!] No cargó panel lateral en índice %d", i)
                        continue

                    # Esperar que termine render (breve)
                    time.sleep(1.5)

                    # Extraer datos
                    nombre = extract_name(page)
                    telefono = extract_phone(page, card_text)
                    sitio_web = extract_website(page)
                    rating, reviews = extract_rating(page)
                    categoria = extract_category(page, nombre)

                    # Saltar si no hay nombre ni teléfono
                    if not nombre and not telefono:
                        continue

                    lead = Lead(
                        nombre=nombre,
                        telefono=telefono,
                        sitio_web=sitio_web,
                        rating_google_maps=rating,
                        numero_reseñas_google_maps=reviews,
                        categoria=categoria,
                        link_google_maps=page.url,
                        provincia=province,
                    )
                    all_leads.append(lead)
                    province_leads += 1
                    log.info("  [+] (%d/%d) %s | tel:%s", province_leads, limit, nombre, telefono or "—")

                except Exception as e:
                    log.warning("  [!] Error en índice %d: %s", i, e)
                    continue

        browser.close()

    # ── Guardar CSV ──────────────────────────────────────────────────────────
    headers = [
        "nombre",
        "telefono",
        "sitio_web",
        "rating_google_maps",
        "numero_reseñas_google_maps",
        "categoria",
        "link_google_maps",
        "provincia",
        "email",
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for lead in all_leads:
            writer.writerow(asdict(lead))

    log.info("=" * 50)
    log.info("✅ CSV bruto guardado: %s", output_path)
    log.info("   Registros totales:  %d", len(all_leads))

    # Estadísticas rápidas
    from collections import Counter
    prov_counts = Counter(l.provincia for l in all_leads)
    with_phone = sum(1 for l in all_leads if l.telefono)
    log.info("   Con teléfono:       %d/%d", with_phone, len(all_leads))
    for prov, cnt in sorted(prov_counts.items()):
        log.info("   %s: %d registros", prov, cnt)

    return str(output_path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extrae abogados de Google Maps por provincia (Método 3 - Playwright)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Ruta del CSV bruto a escribir (ej: output/abogados.csv)",
    )
    parser.add_argument(
        "--province",
        action="append",
        dest="provinces",
        required=True,
        help="Provincia(s) a extraer. Usar múltiples veces: --province Pichincha --province Imbabura",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Máximo de leads por provincia (default: 50)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar sin UI (headless). Requerido en Docker.",
    )

    args = parser.parse_args(argv)

    if args.limit <= 0:
        log.error("limit debe ser > 0")
        return 2

    log.info("=" * 50)
    log.info("Scrapling — Método 3 (Playwright)")
    log.info("Provincias: %s", ", ".join(args.provinces))
    log.info("Límite/prov: %d", args.limit)
    log.info("Headless: %s", args.headless)
    log.info("=" * 50)

    run_extraction(
        output_csv=args.output,
        provinces=args.provinces,
        limit=args.limit,
        headless=args.headless,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
