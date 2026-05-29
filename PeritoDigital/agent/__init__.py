import os
from .base import ProveedorWhatsApp
from .meta import ProveedorMeta

def obtener_proveedor() -> ProveedorWhatsApp:
    """Retorna el proveedor configurado (Meta por defecto ahora)."""
    # Forzamos Meta para evitar el problema de Whapi
    return ProveedorMeta()