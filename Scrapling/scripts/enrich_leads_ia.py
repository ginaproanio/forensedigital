import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import pathlib
import json

load_dotenv()

# Configuración de Gemini (Reutilizando la config de RRHH)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
model = genai.GenerativeModel(MODEL_NAME)

def enrich_lead_with_ai(row):
    """Usa IA para evaluar la calidad del prospecto."""
    prompt = f"""
    Actúa como un experto en desarrollo de negocios para una empresa de servicios legales y tecnológicos (SORSABSA).
    Analiza el siguiente prospecto extraído de Google Maps:
    
    Nombre: {row['nombre']}
    Categoría: {row['categoria']}
    Sitio Web: {row['sitio_web']}
    Dirección: {row['direccion_completa']}
    
    OBJETIVO:
    Determina si este prospecto es un cliente potencial de alto valor para servicios de peritaje digital y derecho informático.
    
    RESPUESTA:
    Responde estrictamente en formato JSON plano:
    {{
        "interes_sorsabsa": "Alto/Medio/Bajo",
        "especialidad_detectada": "Ej: Penal, Civil, Corporativo",
        "justificacion": "Breve razón del interés"
    }}
    """
    try:
        response = model.generate_content(prompt)
        # Extraer JSON de la respuesta
        raw_text = response.text
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        return json.loads(raw_text[start:end])
    except Exception:
        return {"interes_sorsabsa": "Error", "especialidad_detectada": "N/A", "justificacion": "Fallo en API"}

def process_csv(input_path):
    path = pathlib.Path(input_path)
    if not path.exists():
        print(f"❌ No existe el archivo: {input_path}")
        return

    print(f"🤖 Leyendo datos y enriqueciendo con {MODEL_NAME}...")
    df = pd.read_csv(path)
    
    # Para no gastar cuota innecesariamente, solo procesamos los que tienen sitio web o categoría ambigua
    # O puedes procesar una muestra primero:
    # df = df.head(10) 

    results = []
    for index, row in df.iterrows():
        print(f"  - Analizando: {row['nombre']}...")
        ai_data = enrich_lead_with_ai(row)
        results.append(ai_data)

    # Combinar resultados
    df_ai = pd.DataFrame(results)
    df_final = pd.concat([df, df_ai], axis=1)

    output_file = path.parent / f"prospectos_ia_{path.name}"
    df_final.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✨ Enriquecimiento terminado. Guardado en: {output_file}")

if __name__ == "__main__":
    # Ejemplo de uso con un CSV ya limpio
    process_csv("c:/Sorsabsa/Scrapling/abogados-ecuador-limpio.csv")