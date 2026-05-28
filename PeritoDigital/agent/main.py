import os
import logging
import asyncio
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Query, Response, HTTPException # Importamos HTTPException
from .brain import generar_respuesta
from .database import (
    init_db,
    is_message_processed,
    save_processed_message,
    obtener_historial,
    guardar_mensaje
)
from .calendar import get_calendar_url, autorizar_calendar, calendario_autorizado # Importamos calendario_autorizado

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("peritodigital")

app = FastAPI(title="PeritoDigital Agent API")

ADMIN_PHONE = os.getenv("ADMIN_PHONE_NUMBER") # Tu número para recibir alertas

@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos al arrancar el contenedor."""
    await init_db() # init_db ahora también creará la tabla google_tokens
    logger.info("🚀 Base de Datos (PostgreSQL/Supabase) inicializada correctamente")

@app.get("/webhook")
async def webhook_verification(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Maneja el 'handshake' inicial de Meta para validar el webhook."""
    verify_token = os.getenv("META_VERIFY_TOKEN")
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("✅ Webhook verificado exitosamente por Meta")
        return Response(content=str(hub_challenge), media_type="text/plain")
    return Response(content="Token de verificación inválido", status_code=403)

@app.get("/oauth/start")
async def oauth_start():
    """Inicia el proceso de vinculación con Google Calendar."""
    return {"url": get_calendar_url()}

@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    """Recibe el código de Google y activa el calendario."""
    code = request.query_params.get("code")
    if not code:
        return {"error": "No se proporcionó el código de autorización"}
    
    try:
        await autorizar_calendar(code) # Ahora es awaitable
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al autorizar Google Calendar: {e}")
    return {"status": "ok", "message": "Google Calendar de SORSABSA activado correctamente"}

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Recibe eventos reenviados por el Conector."""
    try:
        data = await request.json()
        
        # Extraer ID del mensaje para deduplicación (crucial para evitar bloqueos)
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return {"status": "ok"}

        message_id = messages[0].get("id")
        
        # Verificar si el mensaje ya fue procesado
        if await is_message_processed(message_id):
            logger.info(f"⏭️ Mensaje duplicado detectado ({message_id}). Ignorando para evitar spam.")
            return {"status": "ok"}

        await save_processed_message(message_id)
        logger.info(f"📩 Webhook recibido ({message_id}): Iniciando procesamiento en segundo plano")
        
        asyncio.create_task(procesar_mensaje_ia(data))
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"❌ Error en el receptor de PeritoDigital: {e}")
        return {"status": "error", "detail": str(e)}

async def procesar_mensaje_ia(data: dict):
    """Extrae el mensaje, consulta la memoria y genera respuesta."""
    try:
        # Estructura simplificada del JSON de Meta/Conector
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return
            
        msg = messages[0]
        telefono = msg.get("from")
        texto = msg.get("text", {}).get("body")
        
        # 1. Persistir mensaje del usuario en el historial
        await guardar_mensaje(telefono, "user", texto)
        
        # 2. Cargar historial persistente (Memoria)
        historial = await obtener_historial(telefono)
        
        # 3. Generar respuesta con contexto completo y consulta a MemoryPalace
        respuesta, requiere_humano = await generar_respuesta(historial=historial, mensaje_nuevo=texto, telefono=telefono)
        
        # 4. Persistir respuesta del asistente
        await guardar_mensaje(telefono, "assistant", respuesta)
        
        conector_url = os.getenv("CONECTOR_URL", "http://conector:8000")

        # 5. Si requiere humano, alertar a la Perito Gina Proaño
        if requiere_humano and ADMIN_PHONE:
            async with httpx.AsyncClient() as client:
                try:
                    alerta = f"🚨 *ALERTA:* El cliente {telefono} solicita atención humana urgente. Revisa el chat en Meta Business Suite."
                    await client.post(f"{conector_url}/send", json={
                        "to": ADMIN_PHONE,
                        "message": alerta
                    }, timeout=5.0)
                    logger.warning(f"⚠️ Alerta de intervención humana enviada a Gina ({ADMIN_PHONE})")
                except Exception as e:
                    logger.error(f"❌ No se pudo enviar la alerta de administrador: {e}")

        # 6. Enviar respuesta de vuelta al cliente
        async with httpx.AsyncClient() as client:
            try:
                await client.post(f"{conector_url}/send", json={
                    "to": telefono,
                    "message": respuesta
                }, timeout=10)
                logger.info(f"📤 Respuesta entregada al Conector para {telefono}")
            except Exception as e:
                logger.error(f"❌ Falló la entrega al Conector: {e}")

    except Exception as e:
        logger.error(f"❌ Error procesando mensaje con IA: {e}")