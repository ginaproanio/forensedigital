import os
import logging
import asyncio
import httpx
from contextlib import asynccontextmanager
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
from .providers import obtener_proveedor

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("peritodigital")

# Inicializar proveedor de WhatsApp
proveedor = obtener_proveedor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la base de datos al arrancar el servidor."""
    await init_db()
    logger.info("🚀 Base de Datos inicializada y Proveedor Meta configurado")
    yield

app = FastAPI(title="PeritoDigital Agent API", lifespan=lifespan)

@app.get("/")
async def root():
    """Mensaje de bienvenida para confirmar que el servidor está activo."""
    return {"status": "online", "agent": "PeritoDigital", "version": "1.0.0", "message": "SORSABSA API operativa"}

ADMIN_PHONE = os.getenv("ADMIN_PHONE_NUMBER") # Tu número para recibir alertas

@app.get("/webhook")
async def webhook_verification(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Maneja la verificación oficial de Meta (WhatsApp/Instagram)."""
    resultado = await proveedor.validar_webhook(Request(scope={"type": "http", "query_string": b""})) # Dummy request for logic
    # Usar lógica directa para simplificar la verificación de Meta
    if hub_mode == "subscribe" and hub_verify_token == os.getenv("META_VERIFY_TOKEN"):
        logger.info("✅ Webhook verificado exitosamente por Meta")
        return Response(content=hub_challenge, media_type="text/plain")
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
        mensajes = await proveedor.parsear_webhook(request)

        if not mensajes:
            return {"status": "ok"}

        for msg_info in mensajes:
            # Verificar si el mensaje ya fue procesado
            if await is_message_processed(msg_info.mensaje_id):
                logger.info(f"⏭️ Mensaje duplicado detectado ({msg_info.mensaje_id}).")
                continue

            await save_processed_message(msg_info.mensaje_id)
            logger.info(f"📩 Webhook recibido de {msg_info.telefono}: Iniciando procesamiento")
            
            # Procesar en segundo plano para responder rápido a Meta
            asyncio.create_task(procesar_mensaje_ia(msg_info))
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"❌ Error en el receptor de PeritoDigital: {e}")
        return {"status": "error", "detail": str(e)}

async def procesar_mensaje_ia(msg_info):
    """Extrae el mensaje, consulta la memoria y genera respuesta."""
    try:
        # 1. Persistir mensaje del usuario en el historial
        await guardar_mensaje(msg_info.telefono, "user", msg_info.texto)
        
        # 2. Cargar historial persistente (Memoria)
        historial = await obtener_historial(msg_info.telefono)
        
        # 3. Generar respuesta con contexto completo y consulta a MemoryPalace
        respuesta, requiere_humano = await generar_respuesta(historial=historial, mensaje_nuevo=msg_info.texto, telefono=msg_info.telefono)
        
        # 4. Persistir respuesta del asistente
        await guardar_mensaje(msg_info.telefono, "assistant", respuesta)

        # 5. Si requiere humano, alertar a la Perito Gina Proaño
        if requiere_humano and ADMIN_PHONE:
            alerta = f"🚨 *ALERTA:* El cliente {msg_info.telefono} solicita atención humana urgente. Revisa el Meta Business Suite."
            await proveedor.enviar_mensaje(ADMIN_PHONE, alerta)

        # 6. Enviar respuesta de vuelta al cliente
        await proveedor.enviar_mensaje(msg_info.telefono, respuesta)
        logger.info(f"📤 Respuesta entregada vía Meta para {msg_info.telefono}")
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje con IA: {e}")