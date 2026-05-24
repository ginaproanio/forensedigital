import logging
import csv
import random
import os
import asyncio
import httpx
from dotenv import load_dotenv
from datetime import datetime, timedelta
from supabase import create_client, Client

# Busca el archivo .env en la raíz para cargar las credenciales automáticamente
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Configuración de logs para visualización clara en el contenedor Docker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mensajeria")

# Configuración de Credenciales (Se recomienda usar variables de entorno)
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN")
META_TOKEN = os.getenv("META_TOKEN")
META_PHONE_ID = os.getenv("META_PHONE_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None

def obtener_mensaje_personalizado(nombre):
    """Lee el mensaje de un archivo txt y reemplaza el marcador de nombre."""
    try:
        if not os.path.exists(MESSAGE_FILE_PATH):
            # Si no existe el archivo, creamos uno por defecto
            with open(MESSAGE_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write("Hola {nombre}, te saludamos de Sorsabsa.")
        
        with open(MESSAGE_FILE_PATH, 'r', encoding='utf-8') as file:
            template = file.read()
            return template.format(nombre=nombre)
    except Exception as e:
        logger.error(f"Error leyendo mensaje.txt: {e}")
        return f"Hola {nombre}, te contactamos de Sorsabsa."

async def notificar_error_critico(mensaje):
    """Envía una alerta al Hub de Conector via Supabase REST API"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("No se puede notificar error crítico: Credenciales de Supabase faltantes.")
        return

    url = f"{SUPABASE_URL}/rest/v1/conector_notifications"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {
        "tipo": "error_sistema",
        "mensaje": f"🚨 *MENSAJERÍA SORSABSA* 🚨\n{mensaje}",
        "estado": "pending"
    }
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, headers=headers)
        except Exception as e:
            logger.error(f"Fallo al alertar al Hub de Conector: {e}")

async def enviar_via_whapi(telefono, nombre, mensaje):
    """Intenta enviar mensaje usando Whapi.cloud"""
    url = "https://gate.whapi.cloud/messages/text"
    headers = {"Authorization": f"Bearer {WHAPI_TOKEN}"}
    payload = {
        "typing_time": 0,
        "to": f"{telefono}@s.whatsapp.net",
        "body": mensaje
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                return True
            if response.status_code == 401:
                await notificar_error_critico("Token de Whapi inválido o expirado. Se requiere revisión manual.")
            logger.warning(f"Whapi falló (Saldo?): {response.status_code} - {response.text}")
            return False
        except Exception as e:
            logger.error(f"Error de conexión con Whapi: {type(e).__name__} - {str(e)}")
            return False

async def enviar_via_meta(telefono, nombre, mensaje):
    """Intenta enviar mensaje usando la API Oficial de Meta"""
    url = f"https://graph.facebook.com/v21.0/{META_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {META_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {"body": mensaje}
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return True
            if response.status_code == 401:
                await notificar_error_critico("Token de Meta (Facebook API) inválido o rechazado.")
            logger.warning(f"Meta falló (Verificación?): {response.status_code} - {response.text}")
            return False
        except Exception as e:
            logger.error(f"Error de conexión con Meta: {type(e).__name__} - {str(e)}")
            return False

async def enviar_mensaje_whatsapp(telefono, nombre):
    """
    Lógica de envío con Fallback: Primero intenta Whapi, si falla intenta Meta.
    """
    mensaje = obtener_mensaje_personalizado(nombre)
    # Intentamos con Whapi primero
    logger.info(f"Intentando enviar a {nombre} via Whapi...")
    if await enviar_via_whapi(telefono, nombre, mensaje):
        return True
    
    # Si Whapi falla (por falta de plata o error), intentamos Meta
    logger.info(f"Whapi no disponible, intentando via Meta para {telefono}...")
    return await enviar_via_meta(telefono, nombre, mensaje)

def get_backoff_delay(intentos):
    """Calcula el retraso exponencial (10min, 20min, 40min, 80min, 160min)"""
    return 600 * (2 ** (intentos - 1))

async def realizar_prueba_de_humo(numero):
    logger.info(f"--- INICIANDO PRUEBA DE HUMO AL NÚMERO: {numero} ---")
    exito = await enviar_mensaje_whatsapp(numero, "Usuario de Prueba")
    if exito:
        logger.info("Prueba de humo EXITOSA")
    else:
        logger.error("Prueba de humo FALLIDA")

async def cargar_leads_desde_csv(csv_path, session):
    """Lee el CSV e inserta en la cola si no existen los registros."""
    if not os.path.exists(csv_path):
        logger.error(f"Archivo CSV no encontrado: {csv_path}")
        return

    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            telefono = row.get('telefono')
            nombre = row.get('nombre')
            
            # Deduplicación básica por teléfono
            existente = session.query(RegistroEnvio).filter_by(telefono=telefono).first()
            if not existente:
                session.add(RegistroEnvio(telefono=telefono, nombre=nombre, estado='pendiente'))
        session.commit()

async def procesar_envio_masivo(csv_path, session):
    try:
        # 1. Poblar la cola desde el CSV
        await cargar_leads_desde_csv(csv_path, session)

        # 2. Worker Loop: Procesa hasta que no queden pendientes por ejecutar
        while True:
            # Busca el primer elemento que esté pendiente o fallido, que no haya excedido reintentos 
            # y cuya fecha de próximo intento sea menor o igual a ahora.
            item = session.query(RegistroEnvio).filter(
                RegistroEnvio.estado.in_(['pendiente', 'fallido']),
                RegistroEnvio.intentos < 5,
                RegistroEnvio.proximo_intento <= datetime.utcnow()
            ).first()

            if not item:
                logger.info("No hay más mensajes pendientes o programados en la cola.")
                break

            logger.info(f"📨 Procesando {item.nombre} ({item.telefono}). Intento: {item.intentos + 1}")
            
            if await enviar_mensaje_whatsapp(item.telefono, item.nombre):
                item.estado = 'enviado'
                item.fecha_envio = datetime.utcnow()
                logger.info(f"✅ Notificación enviada con éxito a {item.telefono}")
            else:
                item.intentos += 1
                item.estado = 'fallido'
                delay = get_backoff_delay(item.intentos)
                item.proximo_intento = datetime.utcnow() + timedelta(seconds=delay)
                logger.warning(f"❌ Error al enviar a {item.telefono}. Reintento programado en {delay}s")
                
                # Alerta si superó el límite de intentos (Fallo permanente)
                if item.intentos >= 5:
                    msg = f"Notificación a {item.nombre} ({item.telefono}) falló permanentemente tras 5 intentos."
                    await notificar_error_critico(msg)
            
            session.commit()

            # Anti-Spam: Random sleep de seguridad entre solicitudes
            await asyncio.sleep(random.uniform(15, 35))

    except Exception as e:
        logger.error(f"Error procesando CSV: {e}")

if __name__ == "__main__":
    # Configuración de ejecución
    ES_PRUEBA_DE_HUMO = True
    NUMERO_PRUEBA = os.getenv("TEST_PHONE_NUMBER")
    CSV_PATH = os.path.join(BASE_DIR, "mensajeria", "data", "abogados-ecuador-final.csv")

    async def run_smoke_test(num):
        logger.info(f"--- INICIANDO PRUEBA DE HUMO AL NÚMERO: {num} ---")
        if await enviar_mensaje_whatsapp(num, "Usuario de Prueba"):
            logger.info("Prueba de humo EXITOSA")
        else:
            logger.error("Prueba de humo FALLIDA")

    if ES_PRUEBA_DE_HUMO:
        asyncio.run(run_smoke_test(NUMERO_PRUEBA))
    else:
        asyncio.run(procesar_envio_masivo(CSV_PATH))
