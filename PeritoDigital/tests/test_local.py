"""
Prueba el agente en la terminal sin necesitar WhatsApp.
Ejecutar: python tests/test_local.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from agent.brain import generar_respuesta
from agent.database import init_db, guardar_mensaje, obtener_historial

TELEFONO_TEST = "test_terminal"

async def chat():
    await init_db()
    print("\n" + "="*55)
    print("  SORSABSA — Perito Digital (modo prueba terminal)")
    print("  Escribe 'salir' para terminar")
    print("="*55 + "\n")

    while True:
        try:
            entrada = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Sesión terminada.")
            break

        if entrada.lower() in ("salir", "exit", "quit"):
            print("👋 Hasta pronto.")
            break
        if not entrada:
            continue

        await guardar_mensaje(TELEFONO_TEST, "user", entrada)
        historial = await obtener_historial(TELEFONO_TEST)

        print("Perito Digital: pensando...", end="\r")
        respuesta = await generar_respuesta(historial[:-1], entrada)
        await guardar_mensaje(TELEFONO_TEST, "assistant", respuesta)

        print(f"Perito Digital: {respuesta}\n")

if __name__ == "__main__":
    asyncio.run(chat())
