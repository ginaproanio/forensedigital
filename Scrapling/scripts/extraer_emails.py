import asyncio
import re
import pandas as pd
import logging
from playwright.async_api import async_playwright
from pathlib import Path
from datetime import datetime
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("scrapling-crawler")

# Regex para emails (básico pero efectivo para scraping inicial)
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

async def find_emails_in_site(page, url):
    """Usa la página ya abierta para extraer emails únicos."""
    if not url or pd.isna(url) or not url.startswith('http'):
        return ""

    try:
        logger.info(f"🌐 Visitando: {url}")
        # Cargamos solo lo esencial para velocidad
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        
        content = await page.content()
        emails = set(re.findall(EMAIL_REGEX, content))
        
        # Limpieza de falsos positivos (extensiones de archivos)
        emails = {e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.pdf', '.css', '.js'))}
        
        if emails:
            logger.info(f"✅ Encontrados: {', '.join(emails)}")
            return ", ".join(emails)
        return ""
    except Exception as e:
        logger.warning(f"❌ Error en {url}: {str(e)}")
        return ""

def sync_to_supabase(row):
    """Sincroniza un lead enriquecido con el esquema v2.0."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not all([url, key]) or pd.isna(row.get('email')) or row['email'] == "": return

    try:
        supabase: Client = create_client(url, key)
        supabase.schema("sorsabsa_scrapling").table("prospects").upsert({
            "nombre_estudio": row.get('nombre', 'Desconocido'),
            "email": row['email'].split(',')[0].strip(), # Tomamos el primero
            "telefono": row.get('telefono'),
            "direccion": row.get('direccion_completa'),
            "fuente": "extraer_emails_script"
        }, on_conflict="email").execute() # Eliminado await para entorno Docker
    except Exception as e:
        logger.warning(f"⚠️ Error sincronizando lead: {e}")

async def enrich_csv(input_file):
    """Lee el CSV, busca emails para cada sitio web y guarda el resultado."""
    path = Path(input_file)
    if not path.exists():
        logger.error(f"El archivo {input_file} no existe.")
        return

    df = pd.read_csv(input_file)
    
    if 'sitio_web' not in df.columns:
        logger.error("El CSV no tiene la columna 'sitio_web'.")
        return

    logger.info(f"🚀 Iniciando enriquecimiento de {len(df)} registros...")
    
    # Solo procesamos si no tiene email ya capturado
    if 'email' not in df.columns:
        df['email'] = ""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_output = input_file.replace('.csv', f'_progreso_{timestamp}.csv')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for index, row in df.iterrows():
            if pd.notna(row['sitio_web']) and (pd.isna(row['email']) or row['email'] == ""):
                emails = await find_emails_in_site(page, row['sitio_web'])
                df.at[index, 'email'] = emails

                # Sincronización v2.0 opcional si hay email
                sync_to_supabase(df.iloc[index])

                # Guardado incremental para no perder progreso
                if index % 5 == 0:
                    df.to_csv(temp_output, index=False)

        await browser.close()

    output_file = input_file.replace('.csv', f'_enriquecido_{timestamp}.csv')
    df.to_csv(output_file, index=False)
    if Path(temp_output).exists(): Path(temp_output).unlink() # Borrar temporal
    logger.info(f"✨ Proceso terminado. Archivo guardado como: {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python extraer_emails.py ruta_al_archivo.csv")
    else:
        asyncio.run(enrich_csv(sys.argv[1]))