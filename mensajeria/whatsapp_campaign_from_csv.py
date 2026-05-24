"""Enviar campañas WhatsApp a una lista (CSV) usando Meta Cloud API.

Lee un CSV (generado por Scrapling/limpiar_csv.py) y envía mensajes por WhatsApp.

Campos esperados (por defecto):
- telefono_normalizado (mejor)
- telefono (fallback)

Para mensajes con plantilla:
- template_name
- language_code
- params_json (opcional) o usar mapeo básico para variables

Uso:

1) Mensaje sin plantilla (NO recomendado para publicidad):
./.docker_global/run.sh mensajeria \
  python mensajeria/whatsapp_campaign_from_csv.py send-text \
  --csv "abogados-ecuador-limpio.csv" \
  --text "Hola" \
  --phone-col telefono_normalizado \
  --limit 10

2) Mensaje con plantilla (RECOMENDADO):
./.docker_global/run.sh mensajeria \
  python mensajeria/whatsapp_campaign_from_csv.py send-template \
  --csv "abogados-ecuador-limpio.csv" \
  --template "hello_world" \
  --language "es_ES" \
  --phone-col telefono_normalizado \
  --limit 10

Variables de entorno:
- WHATSAPP_PHONE_NUMBER_ID
- SYSTEM_USER_ACCESS_TOKEN
- META_GRAPH_API_VERSION (opcional)

Nota: Meta exige que el mensaje cumpla políticas. Los anuncios normalmente deben ir con plantillas.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd
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


def send_text(cfg: WhatsAppConfig, to_wa_phone: str, body: str) -> Dict[str, Any]:
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
        "text": {"body": body},
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
    if r.status_code >= 400:
        raise RuntimeError(f"send_text failed ({r.status_code}): {data}")
    return data


def send_template(
    cfg: WhatsAppConfig,
    to_wa_phone: str,
    template_name: str,
    language_code: str,
    components_body_parameters: Optional[list[dict[str, Any]]] = None,
) -> Dict[str, Any]:
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

    if components_body_parameters:
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": components_body_parameters,
            }
        ]

    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
    if r.status_code >= 400:
        raise RuntimeError(f"send_template failed ({r.status_code}): {data}")
    return data


def load_cfg() -> WhatsAppConfig:
    api_version = _env("META_GRAPH_API_VERSION", "v23.0")
    phone_number_id = _env("WHATSAPP_PHONE_NUMBER_ID")
    access_token = _env("SYSTEM_USER_ACCESS_TOKEN")
    return WhatsAppConfig(api_version=api_version, phone_number_id=phone_number_id, access_token=access_token)


def read_phone_column(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        raise RuntimeError(f"CSV no tiene la columna '{col}'. Columnas: {list(df.columns)}")
    return df[col].fillna("").astype(str).str.strip()


def parse_components_params(params_json: Optional[str]) -> Optional[list[dict[str, Any]]]:
    if not params_json:
        return None
    arr = json.loads(params_json)
    if not isinstance(arr, list):
        raise RuntimeError("--params debe ser un JSON array")
    return arr


def main() -> None:
    cfg = load_cfg()

    p = argparse.ArgumentParser(description="WhatsApp Campaign from CSV (Meta Cloud API)")
    sub = p.add_subparsers(dest="cmd", required=True)

    send_text_p = sub.add_parser("send-text", help="Enviar mensaje sin plantilla (restricciones WhatsApp)")
    send_text_p.add_argument("--csv", required=True)
    send_text_p.add_argument("--text", required=True)
    send_text_p.add_argument("--phone-col", default="telefono_normalizado")
    send_text_p.add_argument("--limit", type=int, default=0, help="0 = sin limite")
    send_text_p.add_argument("--sleep", type=float, default=0.25, help="segundos entre envíos")

    send_tpl_p = sub.add_parser("send-template", help="Enviar mensaje con plantilla (recomendado)")
    send_tpl_p.add_argument("--csv", required=True)
    send_tpl_p.add_argument("--template", required=True)
    send_tpl_p.add_argument("--language", required=True, help="ej: es_ES")
    send_tpl_p.add_argument("--phone-col", default="telefono_normalizado")
    send_tpl_p.add_argument("--limit", type=int, default=0)
    send_tpl_p.add_argument("--sleep", type=float, default=0.25)
    send_tpl_p.add_argument(
        "--params",
        default=None,
        help="JSON array para body parameters. Ej: '[{"type":"text","text":"Gina"}]'",
    )

    args = p.parse_args()

    df = pd.read_csv(args.csv)
    phones = read_phone_column(df, args.phone_col)

    # filtrar vacíos
    valid_rows = df[phones != ""].copy()
    valid_rows["__phone"] = phones[phones != ""].values

    if args.limit and args.limit > 0:
        valid_rows = valid_rows.head(args.limit)

    total = len(valid_rows)
    print(f"📨 Enviando a {total} contactos desde {args.csv}...")

    ok = 0
    fail = 0

    if args.cmd == "send-text":
        for i, row in enumerate(valid_rows.itertuples(index=False), start=1):
            to_phone = getattr(row, "__phone")
            try:
                send_text(cfg, to_phone, args.text)
                ok += 1
                print(f"[{i}/{total}] ✅ {to_phone}")
            except Exception as e:
                fail += 1
                print(f"[{i}/{total}] ❌ {to_phone} -> {e}")
            time.sleep(args.sleep)
        print(f"Listo. OK={ok} FAIL={fail}")
        return

    if args.cmd == "send-template":
        params = parse_components_params(args.params)
        for i, row in enumerate(valid_rows.itertuples(index=False), start=1):
            to_phone = getattr(row, "__phone")
            try:
                send_template(cfg, to_phone, args.template, args.language, components_body_parameters=params)
                ok += 1
                print(f"[{i}/{total}] ✅ {to_phone}")
            except Exception as e:
                fail += 1
                print(f"[{i}/{total}] ❌ {to_phone} -> {e}")
            time.sleep(args.sleep)
        print(f"Listo. OK={ok} FAIL={fail}")
        return

    raise RuntimeError("Comando no soportado")


if __name__ == "__main__":
    main()

