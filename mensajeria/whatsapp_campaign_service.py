"""WhatsApp Business campaign service (Meta Cloud API)

Este servicio está pensado para enviar mensajes publicitarios (campañas) a clientes
usando la API de la nube de WhatsApp.

ALERTA: Para enviar publicidad normalmente se recomienda usar MENSAJES CON PLANTILLA.
Los mensajes SIN plantilla tienen restricciones (ventanas de atención al cliente).

Requiere variables de entorno:
- META_GRAPH_API_VERSION (opcional, default: v23.0)
- WHATSAPP_PHONE_NUMBER_ID
- SYSTEM_USER_ACCESS_TOKEN

Ejemplo de uso (CLI):
python mensajeria/whatsapp_campaign_service.py send --to +5939XXXXXXXX --body "Hola"

Para webhooks (recepción de eventos) hay endpoints indicados en el archivo.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from flask import Flask, jsonify, request


def _env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Falta variable de entorno: {name}")
    return value


@dataclass
class WhatsAppConfig:
    phone_number_id: str
    access_token: str
    api_version: str

    @property
    def base_url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}"  # e.g. v23.0


def whatsapp_send_text(cfg: WhatsAppConfig, to_wa_phone: str, body: str, preview_url: bool = False) -> Dict[str, Any]:
    url = f"{cfg.base_url}/{cfg.phone_number_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg.access_token}",
    }
    payload: Dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_wa_phone,
        "type": "text",
        "text": {
            "body": body,
            "preview_url": preview_url,
        },
    }

    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    if r.status_code >= 400:
        raise RuntimeError(f"Error enviando mensaje ({r.status_code}): {data}")
    return data


def create_app(cfg: WhatsAppConfig) -> Flask:
    app = Flask(__name__)

    # GET healthcheck
    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    # Meta Webhook verify endpoint (si lo configuras así)
    # Nota: la verificación real requiere hub.mode / hub.verify_token / hub.challenge.
    # Aquí solo lo dejamos como guía.
    @app.get("/webhook")
    def webhook_verify():
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if not mode or not token or not challenge:
            return jsonify({"error": "missing hub.* params"}), 400

        # TODO: agrega lógica con un VERIFY_TOKEN si lo usas.
        # Por ahora permitimos solo que exista.
        if token != os.getenv("WHATSAPP_VERIFY_TOKEN", token):
            return jsonify({"error": "verify_token mismatch"}), 403
        return challenge, 200

    # POST webhook events
    @app.post("/webhook")
    def webhook_events():
        body = request.get_json(silent=True) or {}

        # Ejemplo de payload: [{object: whatsapp_business_account, entry:[...]}]
        # Los campos clave suelen estar en entry[].changes[].value.messages
        # Mantenemos el endpoint genérico.
        return jsonify({"received": True, "echo": body}), 200

    return app


def load_cfg() -> WhatsAppConfig:
    api_version = os.getenv("META_GRAPH_API_VERSION", "v23.0")
    phone_number_id = _env("WHATSAPP_PHONE_NUMBER_ID")
    access_token = _env("SYSTEM_USER_ACCESS_TOKEN")
    return WhatsAppConfig(
        phone_number_id=phone_number_id,
        access_token=access_token,
        api_version=api_version,
    )


def main() -> None:
    cfg = load_cfg()

    parser = argparse.ArgumentParser(description="WhatsApp Campaign Service")
    sub = parser.add_subparsers(dest="cmd", required=True)

    send = sub.add_parser("send", help="Enviar mensaje de texto (sin plantilla) a un usuario")
    send.add_argument("--to", required=True, help="Número destino en formato internacional (ej: +5939... o sin +, según Meta/tu WA ID)")
    send.add_argument("--body", required=True, help="Texto del mensaje")
    send.add_argument("--preview-url", action="store_true", help="Habilita preview_url")

    serve = sub.add_parser("serve", help="Levantar servidor Flask para webhook")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")))
    
    args = parser.parse_args()

    if args.cmd == "send":
        result = whatsapp_send_text(cfg, args.to, args.body, preview_url=bool(args.preview_url))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "serve":
        app = create_app(cfg)
        # debug desactivado por defecto
        app.run(host=args.host, port=args.port, debug=False)
        return

    raise RuntimeError("Comando no soportado")


if __name__ == "__main__":
    main()

