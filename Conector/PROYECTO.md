# Conector Meta Ads - Resumen del Proyecto

## Estado del Proyecto
✅ **Fase 3: Simulación y Validación de Flujo Pericial Completada**

## App ID de Facebook
```
1650307639342860
```

## Estructura del Proyecto

```
Conector/
├── README.md                      # Documentación principal
├── RUNBOOK.md                     # Guía operativa detallada
├── CLAUDE.md                      # Instrucciones específicas para Claude
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore                     # Archivos ignorados por git
├── mcp-config.json               # Configuración del MCP server
├── setup.sh                       # Script de configuración (Linux/macOS)
├── setup.ps1                      # Script de configuración (Windows)
└── prompts/
    ├── prompt-meta-campaign-paused.md    # Plantilla: Crear campaña
    ├── prompt-meta-report-semanal.md     # Plantilla: Reporte semanal
    └── prompt-meta-auditoria-pixel.md    # Plantilla: Auditoría de pixel
```

## Archivos Clave

### 1. README.md
- Visión general del proyecto
- Instrucciones de instalación del CLI
- Configuración del MCP server
- Plantillas de prompts básicas

### 2. RUNBOOK.md
- Guía operativa paso a paso
- Configuración de la app Meta
- Permisos requeridos
- Prompts listos para copiar/pegar

### 3. CLAUDE.md
- Instrucciones específicas para Claude
- Comandos disponibles vía MCP
- Reglas de seguridad críticas
- Flujo de trabajo recomendado
- Solución de problemas

### 4. .env.example
- Plantilla para configurar variables de entorno
- Incluye el App ID (1650307639342860)
- Campos para token, ad account, pixel, catálogo, page ID

### 5. Scripts de Setup
- `setup.sh` - Configuración automática para Linux/macOS
- `setup.ps1` - Configuración automática para Windows
- Ambos scripts:
  - Verifican Node.js y npm
  - Crean .env desde .env.example
  - Ofrecen instalar Meta Ads CLI
  - Proporcionan próximos pasos

## Configuración Requerida

### 1. Meta for Developers
- App ID: `1650307639342860`
- Producto: Meta Ads
- Permisos: ads_management, ads_read, business_management, whatsapp_business_messaging, whatsapp_business_management
- Token de sistema generado

### 2. Variables de Entorno (.env)
```bash
META_APP_ID=1650307639342860
META_ACCESS_TOKEN=<tu_token>
META_AD_ACCOUNT_ID=act_<tu_ad_account_id>
META_WHATSAPP_ID=<tu_id_de_telefono> # Sincronizado con main.py e index.js
META_VERIFY_TOKEN=sorsabsa-conector-webhook # Este es el token que definimos para la verificación de Meta
PERITODIGITAL_URL=https://peritodigital-production.up.railway.app # URL de tu servicio PeritoDigital en Railway
MEMORY_PALACE_PATH=./knowledge/ # Fuente de verdad para respuestas de IA
AUDIT_NODE_SERVERS=✅ WhatsApp (v22.0) | ⏳ Meta Ads (Pendiente) | ⏳ Gmail (Pendiente)
```

### 4. Flujo de Datos e Inteligencia
Para garantizar respuestas coherentes y basadas en peritajes reales, el flujo es:
1. **Ingreso**: Meta Cloud API envía Webhook a `Conector`.
2. **Gateway**: `Conector` valida y reenvía a `PeritoDigital`.
3. **Inteligencia**: `PeritoDigital` consulta `MemoryPalace` para obtener contexto técnico/legal.
4. **Respuesta**: `PeritoDigital` devuelve la respuesta procesada a `Conector` para su entrega final vía Meta.
```

### 3. MCP Server en Claude
- URL: `https://mcp.facebook.com/ads`
- Configuración: Settings → Conectores → Remote MCP

## Casos de Uso Principales

### 1. Crear Campañas (en PAUSED)
- Brief completo → Campaña creada en estado PAUSED
- A/B testing con 2 ad sets
- 3 creativos con diferentes ángulos
- Usuario activa manualmente

### 2. Reportes de Desempeño
- Reportes semanales/mensuales
- Métricas clave: spend, impressions, clicks, ctr, cpc, conversions
- Análisis accionable con semáforo

### 3. Auditoría de Pixel
- Validación de configuración
- Detección de eventos faltantes
- Recomendaciones de reparación

## Reglas de Seguridad

### 🚨 CRÍTICO
- **NUNCA** activar campañas automáticamente
- **NUNCA** modificar campañas activas sin confirmación
- **NUNCA** compartir tokens o credenciales

### ✅ SIEMPRE
- Crear campañas en PAUSED
- Confirmar antes de hacer cambios
- Una llamada al CLI a la vez
- Validar IDs antes de operar

## Próximos Pasos para el Usuario

1. **Configurar la App en Meta for Developers**
   - Ir a developers.facebook.com
   - Seleccionar app 1650307639342860
   - Configurar permisos y generar token

2. **Ejecutar script de setup**
   - Linux/macOS: `./setup.sh`
   - Windows: `.\setup.ps1`

3. **Completar configuración .env**
   - Agregar META_ACCESS_TOKEN
   - Agregar META_AD_ACCOUNT_ID

4. **Configurar MCP en Claude**
   - Settings → Conectores → Remote MCP
   - URL: https://mcp.facebook.com/ads

5. **Probar conexión**
   - Usar prompt de prueba o comando CLI
   - Verificar que funciona

6. **Empezar a usar**
   - Usar plantillas de prompts en `prompts/`
   - Seguir reglas de seguridad
   - Mantener campañas en PAUSED hasta revisión

## Recursos Adicionales

- Documentación oficial Meta Ads API: https://developers.facebook.com/docs/marketing-apis
- Guía del CLI oficial: https://www.tododeia.com/community/meta-ads-cli-oficial
- Meta for Developers: https://developers.facebook.com/

## Soporte

Para problemas o preguntas:
1. Revisar CLAUDE.md (sección Solución de Problemas)
2. Verificar configuración en RUNBOOK.md
3. Consultar documentación oficial de Meta