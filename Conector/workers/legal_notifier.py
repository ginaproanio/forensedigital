import asyncio
import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("legal-notifier")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Credenciales de Supabase no encontradas.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def notify_lawyers(law_title: str):
    """Busca abogados y envía notificaciones sobre la nueva ley."""
    # Obtener abogados registrados en LegalConnect
    abogados = supabase.table("legalconnect_users").select("full_name, metadata").eq("role", "abogado").execute()
    
    for abogado in abogados.data:
        phone = abogado.get("metadata", {}).get("phone")
        if phone:
            message = f"⚖️ *LegalConnect Ecuador*\n\nHola {abogado['full_name']}, se ha publicado una nueva normativa: *{law_title}*.\n\nAccede a tu panel para revisarla."
            logger.info(f"Notificando a {phone}...")
            
            # Registrar en la cola de notificaciones de Conector para que el Hub lo procese
            supabase.table("conector_notifications").insert({
                "tenant_id": "00000000-0000-0000-0000-000000000000", # System/Global
                "tipo": "whatsapp",
                "destinatario": phone,
                "mensaje": message,
                "estado": "pending"
            }).execute()

async def monitor_biblioteca():
    """Monitorea la tabla legalconnect_biblioteca en busca de nuevas entradas."""
    logger.info("Iniciando vigilancia de Biblioteca Legal...")
    last_id = None
    
    while True:
        # Consultar la ley más reciente
        res = supabase.table("legalconnect_biblioteca").select("id, titulo").order("created_at", desc=True).limit(1).execute()
        
        if res.data and res.data[0]['id'] != last_id:
            if last_id is not None: # Evitar notificar la última al arrancar
                await notify_lawyers(res.data[0]['titulo'])
            last_id = res.data[0]['id']
        
        await asyncio.sleep(300) # Revisar cada 5 minutos

if __name__ == "__main__":
    asyncio.run(monitor_biblioteca())