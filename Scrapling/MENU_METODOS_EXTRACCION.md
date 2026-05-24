# Scrapling — Menú de métodos de extracción (CSV bruto)

## Objetivo
Generar un **CSV bruto** con contactos de **abogados** por provincia (Ecuador). Luego, el pipeline del repo lo convierte en **CSV limpio** con:
- `Scrapling/scripts/limpiar_csv.py`

> Este menú es 100% del módulo **Scrapling** (extracción). La parte de WhatsApp/Meta se hace después en `mensajeria/`.

---

## Pipeline del proyecto (completo)
1. **Extracción (Scrapling)** → Obtención de Teléfono y Sitio Web.
2. **Enriquecimiento (Scrapling Crawler)** → Visita al Sitio Web para extraer correos electrónicos.
2. **Limpieza/normalización (Scrapling)** → CSV limpio
3. **Campañas (mensajeria)** → envío por WhatsApp / Meta Ads

---

## Método 1 — MCP Claude + Scrapling (avanzado)
**Qué hace:** Claude usa Scrapling MCP para navegar y extraer desde Google Maps.

**Ventajas**
- Mayor flexibilidad de extracción (datos más ricos si funciona).
- **Prioridad**: Búsqueda activa de correos electrónicos en sitios web enlazados.
- Menos trabajo manual.

**Desventajas**
- Depende de disponibilidad/costo de Claude/MCP.
- Puede fallar por bloqueos de Google Maps.

**Cuándo usarlo**
- Cuando tengas saldo/disponibilidad.

---

## Método 2 — API oficial (Places API)
**Qué hace:** usa Google Places API (oficial) para buscar lugares por provincia + categoría, y recuperar datos.

**Ventajas**
- Estable/robusto.
- Legal y mantenible.

**Desventajas**
- Tiene costo.
- Teléfono/dirección pueden no estar siempre presentes.

**Cuándo usarlo**
- Cuando hay presupuesto y quieres confiabilidad.

---

## Método 3 — Scraping con navegador (respaldo)
**Qué hace:** automatiza un navegador (p.ej. Playwright/Selenium) para visitar páginas públicas/dir. y extraer.

**Ventajas**
- No requiere costo tipo API (si la fuente es pública).

**Desventajas**
- Frágil: cambios de UI, bloqueos, mantenimiento.
- Puede requerir iterar prompts/estrategia.

**Cuándo usarlo**
- Cuando no hay saldo para MCP ni presupuesto de API.

---

## Cómo escoger (regla simple)
- **Tienes saldo MCP** → Método 1
- **Tienes presupuesto** → Método 2
- **Sin saldo/presupuesto** → Método 3

---

## Contrato del CSV (para que `limpiar_csv.py` funcione)
Independientemente del método, el CSV bruto debe incluir (o ser mapeable a):
- `nombre`
- `telefono`
- `direccion_completa`
- `sitio_web`
- `rating_google_maps`
- `numero_reseñas_google_maps`
- `categoria`
- `link_google_maps`
- `provincia`
- `email` (Prioridad Alta para Meta Ads matching)

Si el método 2/3 genera encabezados distintos, creamos un **adapter** antes de limpiar.
