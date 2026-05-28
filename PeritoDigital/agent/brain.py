"""Conexión a Anthropic Claude — el cerebro del agente Perito Digital."""
import os
import json
import logging
import re
from datetime import datetime
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from .knowledge import cargar_conocimiento
from .calendar import crear_evento_consulta, calendario_autorizado

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-3-7-sonnet-latest"  # Versión más reciente y estable de Claude 3.7

SYSTEM_PROMPT = """Eres "Perito Digital", el Secretario Técnico y asistente especializado de SORSABSA. 
Sorsabsa es una firma ecuatoriana liderada por la perito Gina Proaño, con dos líneas de negocio:
1. Peritaje Informático Forense y Ciberseguridad.
2. Mediación Especializada en Tecnología (Conflictos de software, audio, video, datos y propiedad intelectual).

Tu misión es actuar como el "Front-Desk": atender clientes, orientarlos sobre en qué consiste cada servicio,
realizar la toma de requerimientos iniciales y AGENDAR la cita para que la Perito Gina Proaño desarrolle el trabajo.

REGLAS:
- Usa un tono formal y profesional en todo momento
- Responde siempre en español
- Sé conciso: máximo 3 párrafos por respuesta
- ROL CRÍTICO: Tú NO ejecutas la pericia ni la mediación. Tu labor es la orientación técnica previa y el agendamiento.
- Si no sabes algo, di: "Permítame consultarlo con nuestro equipo y le respondo a la brevedad"
- Nunca inventes precios exactos — invita a una consulta gratuita
- Si el abogado tiene un caso específico, pregunta: tipo de caso, jurisdicción y urgencia
- SERVICIO DE MEDIACIÓN: Informa que Sorsabsa resuelve disputas sobre derechos de autor, contratos tecnológicos y seguridad de la información mediante mediación legal.

ATENCIÓN HUMANA (CONTINGENCIA):
- Si el cliente solicita explícitamente hablar con una persona, con Gina Proaño, o muestra alta frustración ("eres un bot", "no entiendes"), responde:
  "Entiendo perfectamente. He solicitado a la Perito Gina Proaño que revise personalmente nuestra conversación. Ella se pondrá en contacto con usted a la brevedad."
- En este caso, añade al FINAL de tu respuesta el bloque: SOLICITUD_HUMANO

ESTRATEGIA DE AGENDAMIENTO:
- Para concretar, ofrece agendar una consulta gratuita de 15 min.

AGENDAMIENTO DE CITAS:
- Cuando el cliente quiera agendar, pregunta: nombre completo, fecha y hora preferida
- Una vez que tengas nombre + fecha + hora confirmados, incluye al FINAL de tu respuesta 
  un bloque JSON exactamente así (sin texto adicional después del JSON):

CITA_CONFIRMADA:
{
  "nombre": "Nombre del cliente",
  "fecha": "YYYY-MM-DD",
  "hora": "HH:MM",
  "descripcion": "Breve descripción del caso o motivo de consulta"
}

- Solo incluye el bloque CITA_CONFIRMADA cuando tengas los 3 datos confirmados por el cliente
- Después de confirmar la cita, dile al cliente que recibirá una confirmación

CONOCIMIENTO DE SORSABSA:
{conocimiento}
""".format(conocimiento=cargar_conocimiento())


def detectar_humano(respuesta: str) -> bool:
    """Detecta si la IA determinó que se requiere intervención humana."""
    return "SOLICITUD_HUMANO" in respuesta

def limpiar_respuesta_humano(respuesta: str) -> str:
    """Limpia el tag de solicitud humana de la respuesta final."""
    return respuesta.replace("SOLICITUD_HUMANO", "").strip()


def extraer_cita(respuesta: str) -> dict | None:
    """
    Extrae los datos de la cita del bloque CITA_CONFIRMADA si existe.
    Retorna None si no hay cita en la respuesta.
    """
    try:
        if "CITA_CONFIRMADA:" not in respuesta:
            return None
        
        # Extraer el JSON después del marcador
        partes = respuesta.split("CITA_CONFIRMADA:")
        if len(partes) < 2:
            return None
        
        json_str = partes[1].strip()
        # Buscar el bloque JSON
        match = re.search(r'\{.*?\}', json_str, re.DOTALL)
        if not match:
            return None
        
        datos = json.loads(match.group())
        
        # Validar campos requeridos
        if not all(k in datos for k in ["nombre", "fecha", "hora"]):
            return None
        
        return datos
    except Exception as e:
        logger.error(f"Error extrayendo cita: {e}")
        return None


def limpiar_respuesta(respuesta: str) -> str:
    """Elimina el bloque CITA_CONFIRMADA de la respuesta antes de enviarla al cliente."""
    if "CITA_CONFIRMADA:" not in respuesta:
        return respuesta
    return respuesta.split("CITA_CONFIRMADA:")[0].strip()


async def procesar_cita(datos_cita: dict, telefono: str):
    """Crea el evento en Google Calendar con los datos de la cita."""
    try:
        if not await calendario_autorizado():
            logger.warning("⚠️ Google Calendar no autorizado — cita no agendada en calendario")
            return
        
        fecha_hora = datetime.strptime(
            f"{datos_cita['fecha']} {datos_cita['hora']}",
            "%Y-%m-%d %H:%M"
        )
        
        resultado = await crear_evento_consulta(
            nombre_cliente=datos_cita.get("nombre", "Cliente"),
            telefono=telefono,
            fecha_hora=fecha_hora,
            descripcion=datos_cita.get("descripcion", "Consulta agendada por Perito Digital"),
        )
        
        if resultado:
            logger.info(f"✅ Cita agendada en Google Calendar para {datos_cita['nombre']} — {datos_cita['fecha']} {datos_cita['hora']}")
        else:
            logger.error(f"❌ Falló la creación del evento para {datos_cita['nombre']}")
            
    except ValueError as e:
        logger.error(f"Error parseando fecha/hora de la cita: {e}")
    except Exception as e:
        logger.error(f"Error procesando cita: {e}")


async def generar_respuesta(historial: list[dict], mensaje_nuevo: str, telefono: str = "") -> tuple[str, bool]:
    """
    Genera respuesta con Anthropic Claude y procesa citas si el bot las agenda.
    Retorna solo el texto limpio para enviar al cliente.
    """
    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    
    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=historial + [{"role": "user", "content": mensaje_nuevo}],
            temperature=0.3,
        )
        texto_completo = response.content[0].text
        
        # Verificar si el bot agendó una cita
        datos_cita = extraer_cita(texto_completo)
        if datos_cita and telefono:
            await procesar_cita(datos_cita, telefono)

        # Limpiar tags internos antes de enviar
        texto_limpio = limpiar_respuesta(texto_completo)
        texto_limpio = limpiar_respuesta_humano(texto_limpio)
        
        return texto_limpio, detectar_humano(texto_completo)
        
    except Exception as e:
        error_msg = f"❌ Fallo crítico en el cerebro de la IA: {str(e)}"
        logger.error(error_msg)
        return ("Estimado cliente, SORSABSA está experimentando un alto volumen de consultas. "
                "Un asesor técnico revisará su mensaje a la brevedad.", True) # Activamos alerta humana por seguridad