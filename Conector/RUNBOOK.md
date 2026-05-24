# Conector (Meta Ads) — RUNBOOK (MCP + CLI)

## Objetivo
Operar Meta Ads desde Claude con seguridad:
- Campañas **se crean en PAUSED**.
- Activación (ACTIVE) solo la hace el usuario.

## Configuración de la App Meta

**App ID de Facebook:** `1650307639342860`

### Permisos requeridos en la App
- `ads_management` - Para crear y gestionar campañas
- `ads_read` - Para leer insights y reportes
- `business_management` - Para gestionar recursos de Business Manager

### Variables de entorno (.env)
```bash
META_APP_ID=1650307639342860
META_ACCESS_TOKEN=tu_token_de_acceso
META_AD_ACCOUNT_ID=act_tu_ad_account_id
```

## Conexión (MCP)

### 1. URL oficial MCP server
- https://mcp.facebook.com/ads

### 2. Configuración en Claude
- Claude: Settings → Conectores → Remote MCP (Conectores personalizados) → pegar URL.

### 3. Verificación de conexión
Una vez configurado, prueba con un comando simple:
```text
Lista mis campañas activas usando meta ads campaign list
```

## Prompts listos

### A) Crear campaña en PAUSED
Copiar/pegar:

```text
Eres mi media buyer. Tienes acceso al CLI oficial de Meta Ads (Ads CLI).

Brief de la campaña:
- Producto: [QUÉ ESTOY VENDIENDO]
- Oferta concreta: [PRECIO O DESCUENTO]
- Audiencia ideal: [EDAD, GÉNERO, CIUDAD/PAÍS, INTERESES]
- Presupuesto diario: $[X] USD
- Objetivo del negocio: [VENTAS / LEADS / TRÁFICO]
- Landing: [URL DE DESTINO]
- Page ID de Facebook: [PAGE_ID]

Por favor:
1. Crea una campaña nueva con `meta ads campaign create`.
2. Crea 2 ad sets con audiencias distintas para A/B.
3. Crea 3 creativos diferentes (ángulos: beneficio, prueba social, urgencia) con copy completo y CTA.
4. Crea 3 anuncios uniendo creativos con ad sets.
5. Al final lista TODO lo que creaste con sus IDs.

Reglas:
- NO prendas campañas: todo debe quedar en PAUSED.
- Una llamada al CLI a la vez.
```

### B) Reporte semanal (solo lectura)
```text
Eres mi analista de Meta Ads. Tienes acceso al CLI oficial (Ads CLI).

Cuenta de Meta: act_[ID_DE_MI_AD_ACCOUNT]
Periodo: últimos 7 días

Por favor:
1) Corre `meta ads insights get` con `--date-preset last_7d` para campañas activas.
2) Campos: spend, impressions, clicks, ctr, cpc, conversions, cost_per_action_type.
3) Hazme un reporte de 1 página con: (a) lo bueno, (b) lo malo, (c) diagnóstico, (d) plan próximo.
4) Semáforo final.

Reglas:
- Solo lectura.
- Una llamada al CLI a la vez.
```

### C) Auditoría de pixel/dataset (solo lectura)
```text
Eres mi auditor de tracking de Meta. Acceso al CLI oficial (Ads CLI).

Cuenta: act_[ID_DE_MI_AD_ACCOUNT]
Dataset/Pixel ID: [DATASET_ID]
Catálogo conectado: [CATALOG_ID o "ninguno"]

Por favor:
1) Lista campañas activas con `meta ads campaign list`.
2) Valida que el dataset [DATASET_ID] esté conectado a la cuenta (sin modificar): si necesitas, usa validate/consulta.
3) Confirma si hay conversiones/eventos en insights.
4) Devuélveme reporte: (a) estado del pixel (verde/amarillo/rojo), (b) campañas que no aprovechan pixel, (c) eventos faltantes, (d) qué arreglo debo hacer.

Reglas:
- NO crees/modifiques/borras.
- Una llamada al CLI a la vez.
```

## Entregables
- ID/estructura de campaña creada (PAUSED)
- Reporte semanal en texto
- Reporte de auditoría de pixel

