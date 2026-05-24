import os
import logging
import httpx
from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("conector")

app = FastAPI(title="Sorsabsa Conector Hub")

# Este es el token que definimos en PROYECTO.md
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "sorsabsa-conector-webhook")
PERITODIGITAL_URL = os.getenv("PERITODIGITAL_URL")
META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_ID = os.getenv("META_WHATSAPP_ID")

@app.get("/webhook")
async def webhook_verification(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """Endpoint para que Meta valide tu servidor (GET)."""
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("✅ Webhook verificado por Meta correctamente.")
        return PlainTextResponse(content=challenge)
    
    logger.error("❌ El token de verificación no coincide.")
    return PlainTextResponse(content="Error de verificación", status_code=403)

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Aquí es donde Meta enviará los mensajes de WhatsApp (POST)."""
    data = await request.json()
    logger.info("📩 Nuevo evento recibido en Conector Hub")

    # Si PeritoDigital está configurado, le reenviamos el mensaje
    if PERITODIGITAL_URL:
        try:
            async with httpx.AsyncClient() as client:
                # Reenviamos el payload completo para que PeritoDigital lo procese
                target_url = f"{PERITODIGITAL_URL.rstrip('/')}/webhook"
                await client.post(target_url, json=data, timeout=10)
                logger.info(f"➡️ Evento reenviado a PeritoDigital en {target_url}")
        except Exception as e:
            logger.error(f"❌ Error al reenviar a PeritoDigital: {e}")

    return {"status": "ok"}

@app.post("/send")
async def send_message(request: Request):
    """Endpoint para que los agentes envíen mensajes a través de Meta."""
    try:
        body = await request.json()
        to = body.get("to")
        message = body.get("message")

        if not to or not message:
            return {"status": "error", "message": "Faltan campos 'to' o 'message'"}

        url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {META_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers)
            return resp.json()
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje via Meta: {e}")
        return {"status": "error", "message": str(e)}