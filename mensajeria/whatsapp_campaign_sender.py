"""WhatsApp Campaign Sender (Meta Cloud API)

Servicio simple para enviar mensajes publicitarios (recomendado con plantillas) y/o
mensajes sin plantilla.

NOTA:
- Mensajes SIN plantilla tienen restricciones (ventana 24h desde interacción del usuario).
- Mensajes CON plantillas suelen ser la vía recomendada para campañas publicitarias.

Este módulo ofrece:
- send_text_sans_template (ejemplo)
- send_template (plantilla aprobada en Meta)

Requiere variables de entorno:
- WHATSAPP_PHONE_NUMBER_ID
- SYSTEM_USER_ACCESS_TOKEN
- META_GRAPH_API_VERSION (opcional, default v23.0)

Uso:
  python mensajeria/whatsapp_campaign_sender.py send-template \
    --to "+593..." \
    --template "hello_world" \
    --language "es_ES" \
    --param "[{'key':'name','value':'Gina'}]"  (opcional)

  python mensajeria/whatsapp_campaign_sender.py send-text \
    --to "+593..." \
    --body "Hola" 
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


def _env(name: str, default: Optional[str] = None) -> str:
    v = os.getenv(name, default)
    if v is None or str(v).strip() == "":
        raise RuntimeError(f"Missing env var: {name}")
    return str(v)


@dataclass(frozen=True)
class WhatsAppConfig:
    api_version: str
    phone_number_id: str
    access_token: str

    @property
    def base_url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}"


def send_text_sans_template(cfg: WhatsAppConfig, to_wa_phone: str, body: str, preview_url: bool = False) -> Dict[str, Any]:
    url = f"{cfg.base_url}/{cfg.phone_number_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg.access_token}",
    }

    payload = {
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
        raise RuntimeError(f"WhatsApp send_text failed ({r.status_code}): {data}")

    return data


def send_template(
    cfg: WhatsAppConfig,
    to_wa_phone: str,
    template_name: str,
    language_code: str,
    parameters: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Send a template message.

    parameters format (list):
    [ {"type":"text","text":"..."} ] OR using Meta expected schema.

    Meta Cloud API typical payload:
    {
      "messaging_product":"whatsapp",
      "recipient_type":"individual",
      "to":"<phone>",
      "type":"template",
      "template":{
        "name":"<template_name>",
        "language":{"code":"<lang>"},
        "components":[{"type":"body","parameters":[{"type":"text","text":"..."}]}]
      }
    }
    """

    url = f"{cfg.base_url}/{cfg.phone_number_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg.access_token}",
    }

    payload: Dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_wa_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
        },
    }

    # Si vienen parámetros, asumimos que pertenecen al BODY.
    if parameters:
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": parameters,
            }
        ]

    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    if r.status_code >= 400:
        raise RuntimeError(f"WhatsApp send_template failed ({r.status_code}): {data}")

    return data


def load_cfg() -> WhatsAppConfig:
    api_version = _env("META_GRAPH_API_VERSION", "v23.0")
    phone_number_id = _env("WHATSAPP_PHONE_NUMBER_ID")
    access_token = _env("SYSTEM_USER_ACCESS_TOKEN")
    return WhatsAppConfig(
        api_version=api_version,
        phone_number_id=phone_number_id,
        access_token=access_token,
    )


def main() -> None:
    cfg = load_cfg()

    p = argparse.ArgumentParser(description="WhatsApp Campaign Sender (Meta Cloud API)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("send-text", help="Enviar mensaje texto (sin plantilla)")
    s1.add_argument("--to", required=True)
    s1.add_argument("--body", required=True)
    s1.add_argument("--preview-url", action="store_true")

    s2 = sub.add_parser("send-template", help="Enviar mensaje con plantilla")
    s2.add_argument("--to", required=True)
    s2.add_argument("--template", required=True, help="Nombre de la plantilla aprobada en Meta")
    s2.add_argument("--language", required=True, help="Código de idioma (ej: es_ES)")
    s2.add_argument(
        "--params",
        default=None,
        help="JSON array de parámetros para BODY. Ej: '[{"type":"text","text":"Gina"}]'",
    )

    args = p.parse_args()

    if args.cmd == "send-text":
        out = send_text_sans_template(cfg, args.to, args.body, preview_url=bool(args.preview_url))
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    if args.cmd == "send-template":
        params = None
        if args.params:
            params = json.loads(args.params)
        out = send_template(cfg, args.to, args.template, args.language, parameters=params)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    raise RuntimeError("Comando no soportado")


if __name__ == "__main__":
    main()

