import os
import logging

logger = logging.getLogger(__name__)

def cargar_conocimiento() -> str:
    """
    Carga el contenido de los archivos de conocimiento desde la carpeta knowledge.
    Esta carpeta está mapeada vía Docker desde MemoryPalace.
    """
    ruta_conocimiento = os.getenv("MEMORY_PALACE_PATH", "knowledge/")
    contenido_total = ""
    
    if not os.path.exists(ruta_conocimiento) or not os.path.isdir(ruta_conocimiento):
        logger.error(f"❌ No se encontró la carpeta de conocimiento en: {ruta_conocimiento}")
        return "Información básica de SORSABSA no disponible."

    # Lista de archivos críticos para el agente
    archivos = ["sorsabsa.txt", "reglamentos/216-2024.txt"]
    
    for rel_path in archivos:
        full_path = os.path.join(ruta_conocimiento, rel_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    contenido_total += f"\n--- {rel_path} ---\n"
                    contenido_total += f.read()
            except Exception as e:
                logger.error(f"Error leyendo {full_path}: {e}")
        else:
            logger.warning(f"⚠️ Archivo no encontrado: {full_path}")

    return contenido_total