# Conector Meta Ads - Instrucciones para Claude

## Configuración del MCP Server

Este proyecto usa el MCP server oficial de Meta Ads para integrar con Claude.

### URL del MCP Server
```
https://mcp.facebook.com/ads
```

### Configuración en Claude Desktop
1. Abre Settings → Conectores → Conectores personalizados (Remote MCP)
2. Pega la URL: `https://mcp.facebook.com/ads`
3. Guarda la configuración

## App ID de Facebook
```
1650307639342860
```

## Comandos Disponibles vía MCP

El MCP server de Meta Ads expone las siguientes capacidades:

### Gestión de Campañas
- `meta ads campaign create` - Crear nueva campaña
- `meta ads campaign list` - Listar campañas
- `meta ads campaign update` - Actualizar campaña
- `meta ads campaign delete` - Eliminar campaña

### Gestión de Conjuntos de Anuncios (Ad Sets)
- `meta ads adset create` - Crear conjunto de anuncios
- `meta ads adset list` - Listar conjuntos de anuncios
- `meta ads adset update` - Actualizar conjunto de anuncios

### Gestión de Anuncios (Ads)
- `meta ads ad create` - Crear anuncio
- `meta ads ad list` - Listar anuncios
- `meta ads ad update` - Actualizar anuncio

### Insights y Reportes
- `meta ads insights get` - Obtener métricas de rendimiento

### Auditoría
- `meta ads pixel validate` - Validar configuración de pixel
- `meta ads catalog list` - Listar catálogos

## Reglas de Seguridad CRÍTICAS

### 🚨 NUNCA hagas esto:
1. **NUNCA actives campañas automáticamente** - Siempre crea campañas en estado `PAUSED`
2. **NUNCA modifiques campañas activas sin confirmación explícita**
3. **NUNCA compartas tokens de acceso o credenciales**

### ✅ Siempre haz esto:
1. **Crea campañas en PAUSED** - El usuario debe activarlas manualmente
2. **Confirma antes de hacer cambios** - Especialmente en campañas activas
3. **Usa una llamada al CLI a la vez** - Para evitar condiciones de carrera
4. **Valida los IDs** - Antes de realizar operaciones

## Flujo de Trabajo Recomendado

### Para crear una campaña:
1. El usuario proporciona el brief completo
2. Claude usa el MCP para crear campaña en PAUSED
3. Claude crea ad sets con audiencias para A/B testing
4. Claude crea creativos con diferentes ángulos
5. Claude une creativos con ad sets para crear anuncios
6. Claude lista todos los IDs creados
7. **El usuario revisa y activa manualmente las campañas**

### Para reportes:
1. El usuario solicita un reporte (semanal, mensual, etc.)
2. Claude usa `meta ads insights get` con los parámetros adecuados
3. Claude analiza los datos y genera insights accionables
4. Claude proporciona recomendaciones

### Para auditorías:
1. El usuario solicita auditoría de pixel/dataset
2. Claude valida la configuración sin modificar nada
3. Claude reporta el estado y recomienda acciones

## Plantillas de Prompts Disponibles

Las plantillas completas están en la carpeta `prompts/`:

- `prompt-meta-campaign-paused.md` - Crear campaña en PAUSED
- `prompt-meta-report-semanal.md` - Reporte semanal de desempeño
- `prompt-meta-auditoria-pixel.md` - Auditoría de pixel/dataset

## Variables de Entorno

El MCP server usa estas variables de entorno (configuradas en `.env`):

```
META_APP_ID=1650307639342860
META_ACCESS_TOKEN=<tu_token>
META_AD_ACCOUNT_ID=act_<tu_ad_account_id>
```

## Solución de Problemas

### Error: "Authentication failed"
- Verifica que el token de acceso sea válido
- Confirma que la app tenga los permisos necesarios

### Error: "Permission denied"
- La app necesita permisos: `ads_management`, `ads_read`, `business_management`
- Verifica que el usuario tenga rol de administrador en la cuenta de anuncios

### Error: "MCP server not responding"
- Verifica la conexión a internet
- Confirma que la URL del MCP server sea correcta
- Revisa que el token no haya expirado

## Recursos Adicionales

- Documentación oficial de Meta Ads API: https://developers.facebook.com/docs/marketing-apis
- Guía del CLI oficial: https://www.tododeia.com/community/meta-ads-cli-oficial
- Meta for Developers: https://developers.facebook.com/