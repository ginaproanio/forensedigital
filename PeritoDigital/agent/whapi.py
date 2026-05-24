"""Conexión a Whapi.cloud para enviar y recibir mensajes de WhatsApp."""
import os
import httpx

WHAPI_TOKEN = os.getenv("WHAPI_TOKEN")
WHAPI_URL   = os.getenv("WHAPI_URL", "https://gate.whapi.cloud")

async def enviar_mensaje(telefono: str, texto: str) -> bool:
    """Envía un mensaje de texto por WhatsApp vía Whapi."""
    url = f"{WHAPI_URL}/messages/text"
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": telefono,
        "body": texto,
    }
    try:
        # Timeout de 8s para evitar bloqueos por demora excesiva
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return True
    except Exception as e:
        print(f"Error Whapi al enviar a {telefono}: {e}")
        return False

def extraer_mensaje(data: dict) -> tuple[str, str] | None:
    """
    Extrae (telefono, texto) del webhook de Whapi.
    Retorna None si no es un mensaje de texto válido.
    """
    try:
        mensajes = data.get("messages", [])
        if not mensajes:
            return None
        msg = mensajes[0]
        # Solo procesar mensajes entrantes de texto
        if msg.get("from_me"):
            return None
        tipo = msg.get("type", "")
        if tipo != "text":
            return None
        telefono = msg.get("chat_id") or msg.get("from", "")
        texto    = msg.get("text", {}).get("body", "").strip()
        if not telefono or not texto:
            return None
        return telefono, texto
    except Exception as e:
        print(f"Error parseando webhook: {e}")
        return None
