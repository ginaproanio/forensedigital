"""
Integración con Google Calendar para PeritoDigital.
Crea eventos automáticamente cuando el bot agenda una consulta.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Ruta al archivo de credenciales OAuth (en la raíz del proyecto)
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), "..", "client_secret.json")

# Token guardado (se genera tras la primera autorización)
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "token.json")

REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "https://peritodigital-production.up.railway.app/oauth/callback"
)


def get_flow() -> Flow:
    """Crea el flujo OAuth con las credenciales del archivo JSON."""
    if not os.path.exists(CLIENT_SECRET_FILE):
        logger.error(f"❌ No se encuentra {CLIENT_SECRET_FILE}. Descarga las credenciales de Google Cloud.")
        raise FileNotFoundError(f"Archivo de credenciales no encontrado: {CLIENT_SECRET_FILE}")
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    return flow


def get_credentials() -> Credentials | None:
    """Carga las credenciales guardadas del token."""
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        creds = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=SCOPES,
        )
        # Refresh si es necesario
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds
    except Exception as e:
        logger.error(f"Error cargando token: {e}")
        return None


def save_credentials(creds: Credentials):
    """Guarda las credenciales en token.json."""
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    logger.info("✅ Token de Google Calendar guardado")


def get_calendar_url() -> str:
    """Genera la URL de autorización OAuth para Google Calendar."""
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return authorization_url


def autorizar_calendar(code: str):
    """
    Completa el flujo OAuth con el código de autorización.
    Guarda las credenciales en token.json.
    """
    flow = get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    save_credentials(creds)
    logger.info("✅ Google Calendar autorizado exitosamente")
    return creds


async def crear_evento_consulta(
    nombre_cliente: str,
    telefono: str,
    fecha_hora: datetime,
    descripcion: str = "",
    duracion_minutos: int = 60,
) -> dict | None:
    """
    Crea un evento en Google Calendar para una consulta agendada.
    
    Args:
        nombre_cliente: Nombre del cliente o abogado
        telefono: Número de teléfono del cliente
        fecha_hora: Fecha y hora de la consulta (datetime)
        descripcion: Detalles del caso o consulta
        duracion_minutos: Duración en minutos (default: 60)
    
    Returns:
        dict con los datos del evento creado, o None si falló
    """
    creds = get_credentials()
    if not creds:
        logger.error("❌ No hay credenciales de Google Calendar. Ejecuta /oauth/start primero.")
        return None

    try:
        service = build("calendar", "v3", credentials=creds)

        fecha_fin = fecha_hora + timedelta(minutes=duracion_minutos)

        evento = {
            "summary": f"Consulta SORSABSA - {nombre_cliente}",
            "description": (
                f"Cliente: {nombre_cliente}\n"
                f"Teléfono: {telefono}\n"
                f"Agendado por: Perito Digital (Bot)\n\n"
                f"Detalles:\n{descripcion}"
            ),
            "start": {
                "dateTime": fecha_hora.isoformat(),
                "timeZone": "America/Guayaquil",
            },
            "end": {
                "dateTime": fecha_fin.isoformat(),
                "timeZone": "America/Guayaquil",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 60},   # 1 hora antes
                    {"method": "popup", "minutes": 15},   # 15 min antes
                ],
            },
            "attendees": [
                {"email": f"{telefono}@g.us"}  # Intentar agregar al cliente (puede no funcionar)
            ],
        }

        resultado = service.events().insert(calendarId="primary", body=evento).execute()
        logger.info(f"✅ Evento creado: {resultado.get('htmlLink')}")
        return resultado

    except HttpError as e:
        logger.error(f"Error Google Calendar API: {e}")
        return None
    except Exception as e:
        logger.error(f"Error creando evento: {e}")
        return None


def calendario_autorizado() -> bool:
    """Verifica si ya hay credenciales válidas."""
    creds = get_credentials()
    return creds is not None and creds.valid


def listar_proximas_citas(dias: int = 7) -> list[dict]:
    """
    Lista las citas próximas en el calendario.
    
    Args:
        dias: Número de días hacia adelante para buscar
    
    Returns:
        Lista de eventos próximos
    """
    creds = get_credentials()
    if not creds:
        return []
    
    try:
        service = build("calendar", "v3", credentials=creds)
        
        ahora = datetime.utcnow()
        fin = ahora + timedelta(days=dias)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=ahora.isoformat() + 'Z',
            timeMax=fin.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime',
        ).execute()
        
        events = events_result.get('items', [])
        return events
        
    except Exception as e:
        logger.error(f"Error listando citas: {e}")
        return []