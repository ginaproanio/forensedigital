import pandas as pd
import sys
import os
import re
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def registrar_ejecucion(stats, output_path):
    """Registra la actividad en el esquema sorsabsa_scrapling."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not all([url, key]): return

    try:
        supabase: Client = create_client(url, key)
        # Registrar el trabajo de extracción en el esquema correcto
        supabase.schema("sorsabsa_scrapling").table("extraction_jobs").insert({
            "target_query": f"Limpieza: {os.path.basename(output_path)}",
            "status": "completed",
            "leads_found": stats['finales']
        }).execute()

        msg = (
            f"📊 SORSABSA - Limpieza: {stats['finales']} leads procesados. "
            f"Duplicados eliminados: {stats['duplicados']}."
        )
        print(f"✅ Auditoría registrada: {msg}")
    except Exception as e:
        print(f"⚠️ Error en registro de auditoría: {e}")

def normalizar_telefono(tel):
    if pd.isna(tel) or tel == "": return ""
    # Extraer solo números
    nums = re.sub(r'\D', '', str(tel))
    if len(nums) == 9 and nums.startswith('9'): # Formato celular local 09...
        return f"+593{nums}"
    if len(nums) == 12 and nums.startswith('593'):
        return f"+{nums}"
    return str(tel)

def calcular_calidad(row):
    score = 0
    if pd.notna(row.get('telefono')) and row['telefono'] != "": score += 1
    if pd.notna(row.get('email')) and row['email'] != "": score += 1
    if pd.notna(row.get('sitio_web')) and row['sitio_web'] != "": score += 1
    if pd.to_numeric(row.get('rating_google_maps'), errors='coerce') >= 4.0: score += 1
    
    niveles = {0: "Baja", 1: "Media", 2: "Alta", 3: "Premium", 4: "VIP"}
    return niveles.get(score, "Baja")

def limpiar_archivo(input_path):
    if not os.path.exists(input_path):
        print(f"❌ Error: El archivo {input_path} no existe.")
        return

    # Validación de entorno
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
        print("⚠️ Advertencia: Variables de Supabase no detectadas. No se enviarán notificaciones.")
    else:
        print("🔗 Conexión con Supabase configurada.")

    print(f"📖 Leyendo {input_path}...")
    df = pd.read_csv(input_path)
    total_inicial = len(df)

    # 1. Eliminar duplicados
    # Si hay teléfono, mandatorio deduplicar por ahí. Si no, por nombre + dirección.
    df['telefono_clean'] = df['telefono'].apply(lambda x: re.sub(r'\D', '', str(x)) if pd.notna(x) else "")
    
    df_con_tel = df[df['telefono_clean'] != ""].drop_duplicates(subset=['telefono_clean'])
    df_sin_tel = df[df['telefono_clean'] == ""].drop_duplicates(subset=['nombre', 'direccion_completa'])
    
    df = pd.concat([df_con_tel, df_sin_tel])
    df.drop(columns=['telefono_clean'], inplace=True)

    # 2. Normalizar teléfonos
    df['telefono'] = df['telefono'].apply(normalizar_telefono)

    # 3. Calcular Calidad
    df['calidad'] = df.apply(calcular_calidad, axis=1)

    # 4. Ordenar
    df.sort_values(by=['provincia', 'calidad'], ascending=[True, False], inplace=True)

    # Generar nombre de salida con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = input_path.replace('.csv', f'_limpio_{timestamp}.csv')
    
    df.to_csv(output_path, index=False)

    # Estadísticas
    duplicados = total_inicial - len(df)
    vips = len(df[df['calidad'] == 'VIP'])
    
    registrar_ejecucion({
        'finales': len(df),
        'duplicados': duplicados,
        'vip': vips
    }, output_path)

    print(f"\n✅ Limpieza completada:")
    print(f"   - Registros iniciales: {total_inicial}")
    print(f"   - Registros finales: {len(df)}")
    print(f"   - Duplicados eliminados: {duplicados}")
    print(f"\n📊 Calidad de leads:")
    print(df['calidad'].value_counts())
    print(f"\n💾 Guardado en: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python limpiar_csv.py archivo.csv")
    else:
        limpiar_archivo(sys.argv[1])