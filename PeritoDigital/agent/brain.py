import os
import logging
from anthropic import AsyncAnthropic
from .tools import buscar_en_knowledge
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("peritodigital")

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """
Eres el asistente oficial de SORSABSA, especializado en Peritaje Informático Forense en Ecuador.
Tu objetivo es asesorar a clientes (abogados o personas naturales) sobre servicios periciales.

REGLAS DE ORO:
1. Tu base legal principal es la RESOLUCIÓN 216-2024 del Consejo de la Judicatura.
2. Si te preguntan por honorarios, explica que se basan en el Salario Básico Unificado (SBU) según el Art. 48.
3. NO des precios finales exactos; invita siempre a una consulta gratuita.
4. Si un mensaje es técnico o legalmente complejo, indica que la Ing. Gina Proaño (Perito Principal) revisará el caso.
5. Mantén un tono pericial: serio, objetivo y servicial.

INFORMACIÓN DEL NEGOCIO:
- SORSABSA: Peritaje en computadoras, celulares, nubes y redes sociales.
- Horario: Lun-Vie 8-18h, Sab 9-13h.
"""

async def generar_respuesta(historial: list[dict], mensaje_nuevo: str, telefono: str):
    """
    Genera una respuesta inteligente usando Claude 3.7 y RAG simple.
    """
    try:
        # 1. Búsqueda de conocimiento (RAG)
        contexto_legal = buscar_en_knowledge(mensaje_nuevo)
        
        # 2. Construcción del contexto para Claude
        mensajes_para_ia = []
        # Agregar historial (limitado a los últimos 5 para eficiencia)
        for msg in historial[-5:]:
            mensajes_para_ia.append({"role": msg["role"], "content": msg["content"]})
        
        # Agregar el mensaje actual con el contexto recuperado
        prompt_con_contexto = f"""
        CONTEXTO RECUPERADO DE REGLAMENTOS/MATRIZ:
        {contexto_legal}

        MENSAJE DEL CLIENTE:
        {mensaje_nuevo}
        """
        
        mensajes_para_ia.append({"role": "user", "content": prompt_con_contexto})

        # 3. Llamada a la API de Anthropic
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=mensajes_para_ia
        )

        respuesta_texto = response.content[0].text
        
        # 4. Lógica de "Requiere Humano"
        # Si el cliente pide hablar con alguien o está frustrado
        palabras_alerta = ["humano", "gina", "urgente", "denuncia", "pagar", "costo"]
        requiere_humano = any(p in mensaje_nuevo.lower() for p in palabras_alerta)
        
        # Si la IA misma sugiere que alguien revise
        if "especialista" in respuesta_texto.lower() or "gina" in respuesta_texto.lower():
            requiere_humano = True

        return respuesta_texto, requiere_humano

    except Exception as e:
        logger.error(f"❌ Error en el cerebro de PeritoDigital: {e}")
        return "Lo siento, estoy procesando mucha información legal en este momento. ¿Podrías repetirme tu duda?", False