import asyncio
import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("lead-notifier")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
ADMIN_PHONE = os.getenv("ADMIN_PHONE") # Tu número configurado en el .env global

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Credenciales de Supabase no encontradas.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def process_queue():
    """Revisa notificaciones pendientes y las envía al administrador."""
    logger.info("🚀 Iniciando despacho de notificaciones de sistema...")
    
    while True:
        try:
            # Buscar notificaciones pendientes del sistema
            res = supabase.table("conector_notifications")\
                .select("*")\
                .eq("estado", "pending")\
                .eq("tipo", "whatsapp")\
                .execute()
            
            for note in res.data:
                # Aquí se integraría la llamada real al servidor MCP de WhatsApp
                logger.info(f"Enviando reporte a {ADMIN_PHONE}: {note['mensaje'][:50]}...")
                
                supabase.table("conector_notifications").update({
                    "estado": "sent",
                    "updated_at": "now()"
                }).eq("id", note["id"]).execute()
                
        except Exception as e:
            logger.error(f"Error en el worker: {e}")
        
        await asyncio.sleep(60) # Revisar cada minuto

if __name__ == "__main__":
    asyncio.run(process_queue())