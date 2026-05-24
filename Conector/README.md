# 🚀 SORSABSA - Conector (Nervio Central)

Este componente es el **Sistema Nervioso Central** del ecosistema. Actúa como un Hub dual:
1. **MCP Hub**: Permite que Claude y otros agentes de IA ejecuten acciones en el mundo real (Meta Ads, Gmail, WhatsApp).
2. **Gateway Oficial Meta**: Única aplicación aprobada (ID: 1650307639342860) para comunicación oficial sin intermediarios.
3. **API de Notificaciones**: Provee una cola centralizada (`conector_notifications`) para que cualquier producto (LegalConnect, CondoManager) dispare comunicaciones proactivas.

## 🧠 Filosofía "IA con Manos"
A diferencia de una API tradicional, Conector expone **Herramientas (Tools)**. La IA no solo consulta datos, sino que decide qué herramienta usar basándose en el contexto del negocio (ej: crear una audiencia en Meta Ads tras una limpieza exitosa de Scrapling).

## 📂 Estructura del Hub

- **`main.py`**: Servidor FastAPI que orquesta las peticiones y maneja la base de datos de marketing.
- **`servers/meta-ads/`**: Gestión de campañas, reportes y catálogos de Meta Ads.
- **`servers/gmail/`**: Automatización de lectura, búsqueda y envío de correos electrónicos.
- **`servers/whatsapp/`**: Integración OFICIAL con Meta Cloud API (Eliminado soporte para terceros/Whapi).
- **`shared/`**: Utilidades compartidas para validación de tokens y manejo de errores.

## 🤖 Automatizaciones (Workers)

- **`workers/legal_notifier.py`**: Vigila la tabla `legalconnect_biblioteca` y dispara notificaciones vía WhatsApp a los abogados cuando se detecta normativa nueva insertada por LexScraper.
- **`workers/lead_notifier.py`**: Procesa la cola de notificaciones generales (reportes de limpieza, alertas de sistema) para avisar al administrador vía WhatsApp.

## 📊 Esquema de Datos
Sigue el estándar de `SORSABSA_ARQUITECTURA.md`:
- `conector_campaigns`: Registro de campañas publicitarias.
- `conector_notifications`: Cola de mensajes (WhatsApp/Email) pendientes y enviados.
- `conector_audit_log`: Trazabilidad obligatoria de acciones realizadas por la IA.

## 🛠️ Configuración de Claude Desktop

Para que Claude pueda ver estos servidores, añade lo siguiente a tu archivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sorsabsa-meta": {
      "command": "docker",
      "args": ["exec", "-i", "conector", "node", "/app/servers/meta-ads/index.js"]
    },
    "sorsabsa-gmail": {
      "command": "docker",
      "args": ["exec", "-i", "conector", "node", "/app/servers/gmail/index.js"]
    },
    "sorsabsa-whatsapp": {
      "command": "docker",
      "args": ["exec", "-i", "conector", "node", "/app/servers/whatsapp/index.js"]
    }
  }
}
```

## 🚀 Instalación

1. Ejecuta `./setup.sh` para crear la estructura y el archivo `.env`.
2. Configura tus tokens en el archivo `.env`.
3. Asegúrate de que el contenedor `conector` esté levantado (`up.sh conector`).
4. Configura Claude Desktop y reinícialo.

## 🛡️ Seguridad

- Cada servidor lee sus propias credenciales desde la carpeta `config/`.
- Los tokens de acceso nunca se suben al repositorio.

---
**Última actualización**: Mayo 2026