# WhatsApp (Meta Cloud API) - Mensajería

Este directorio contiene una base para enviar mensajes y recibir webhooks usando la **API de la nube de WhatsApp** (Meta).

> **OFICIAL**: Este módulo ahora está sincronizado con **Conector (App ID: 1650307639342860)**. Toda la mensajería enviada desde aquí utiliza la infraestructura aprobada por Meta para evitar bloqueos.

## Estructura
- `readme.md`: guía traducida (pasos Meta)
- `whatsapp_campaign_service.py`: servicio de envío masivo conectado al Hub Central.

## Requisitos
Variables de entorno (Sincronizadas con `.env` global):
- `META_ACCESS_TOKEN`: Token de sistema verificado.
- `META_WHATSAPP_ID`: Identificador del número aprobado.
- `META_GRAPH_API_VERSION`: `v22.0` (Versión actual estable).
- `WHATSAPP_VERIFY_TOKEN` (opcional, para verificación de webhook si aplica)

## Ejecutar (por consola)
Ejemplo de envío SIN plantilla:

```bash
./.docker_global/run.sh mensajeria python mensajeria/whatsapp_campaign_service.py send \
  --to "<WHATSAPP_USER_PHONE_NUMBER>" \
  --body "Hola, te contactamos por una oferta"
```

Levantar servidor webhook (para recibir eventos):

```bash
./.docker_global/run.sh mensajeria python mensajeria/whatsapp_campaign_service.py serve --port 8080
```

## Nota importante (publicidad)
Si quieres mensajes tipo “anuncio”/“publicitarios”, normalmente debes:
1. Enviar mensajes **con plantilla** (aprobadas)
2. Mantener un flujo correcto de **opt-in/consentimiento**
3. Implementar el manejo de webhooks para confirmar delivery/read

---

Si lo que necesitas es una **campaña con plantillas**, dime y armamos el módulo para:
- Plantillas (name + language)
- Variables dinámicas
- Endpoint de `/campaign/send`
- Lectura de destinatarios desde Supabase/archivo
