# Prompt: Reporte Semanal Meta Ads (Solo Lectura)

Copiar/pegar:

```text
Eres mi analista de Meta Ads. Tienes acceso al CLI oficial de Meta Ads (Ads CLI).

Cuenta de Meta: act_[ID_DE_MI_AD_ACCOUNT]
Periodo a analizar: últimos 7 días

Tareas:
1) Corre `meta ads insights get` con `--date-preset last_7d` para campañas activas.
2) Campos solicitados: spend, impressions, clicks, ctr, cpc, conversions, cost_per_action_type.
3) Genera un reporte de 1 página con:
   - (a) Lo bueno (qué funcionó)
   - (b) Lo malo (qué no funcionó)
   - (c) Diagnóstico (análisis de causa raíz)
   - (d) Plan próximo (acciones recomendadas)
4) Incluye semáforo final (verde/amarillo/rojo) según desempeño general.

Reglas:
- Solo lectura (no modificar nada).
- Una llamada al CLI a la vez.
- Enfócate en métricas accionables.
```

## Campos disponibles para insights

- `spend` - Dinero gastado
- `impressions` - Impresiones
- `clicks` - Clics
- `ctr` - Tasa de clics
- `cpc` - Costo por clic
- `conversions` - Conversiones
- `cost_per_action_type` - Costo por acción
- `reach` - Alcance
- `frequency` - Frecuencia
- `cpm` - Costo por mil impresiones

## Ejemplo de uso con fecha personalizada

```bash
meta ads insights get --start-time 2024-01-01 --end-time 2024-01-07