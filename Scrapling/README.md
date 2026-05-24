# Scrapling — Generador de Prospectos (Abogados Ecuador)

Proyecto para generar listas de prospectos (abogados) desde Google Maps usando **Scrapling MCP** integrado con Claude.

## 🎯 Objetivo

Generar un **CSV** con datos de contacto de **abogados por provincia** en **Ecuador**:
- **Imbabura**
- **Pichincha**
- **Cotopaxi**

Estos prospectos se usarán en **Conector** para crear audiencias personalizadas en Meta Ads.

## 📁 Estructura del Proyecto

```
Scrapling/
├── README.md                    # Este archivo
├── RUNBOOK.md                   # Guía operativa detallada
├── .gitignore                   # Archivos ignorados
├── prompts/
│   └── prompt-extraccion-abogados.md  # Prompt maestro optimizado
└── scripts/
    ├── extraer_emails.py        # NUEVO: Crawler para buscar emails en sitios web
    ├── limpiar_csv.py           # Script de limpieza y normalización
    └── requirements.txt         # Dependencias Python
```

## 🚀 Inicio Rápido

### Paso 1: Configurar Scrapling MCP
1. Instala Scrapling según la guía de [tododeia](https://www.tododeia.com/community/scrapling-clientes-gratis)
2. Conecta el MCP en Claude Desktop/Code

### Paso 2: Ejecutar extracción
1. Abre Claude Desktop/Code
2. Copia y pega el prompt desde `prompts/prompt-extraccion-abogados.md`
3. Espera a que Scrapling genere el CSV

### Paso 3: Limpiar el CSV
```bash
# Instalar dependencias
pip install -r scripts/requirements.txt

# Limpiar CSV
python scripts/limpiar_csv.py abogados-ecuador.csv
```

### Paso 4: Enriquecer con IA (Gemini)
Este paso opcional ejecuta `scripts/enrich_leads_ia.py` para:
- Clasificar el prospecto (alto/medio/bajo) según relevancia para SORSABSA.
- Detectar una especialidad (ej. Penal, Civil, Corporativo).
- Generar una justificación breve.

El script consume el CSV limpio y genera un nuevo CSV con columnas adicionales (con prefijo `interes_sorsabsa`, `especialidad_detectada`, `justificacion`).

> Usa **la misma configuración que RRHH**: requiere `GOOGLE_API_KEY` (y opcional `GEMINI_MODEL`).

```bash
python scripts/enrich_leads_ia.py
```

### Paso 5: Usar en Conector
El CSV enriquecido (o el limpio si no ejecutaste IA) está listo para usarse en **Conector** para crear Custom Audiences en Meta Ads.

## 📊 Campos del CSV

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `nombre` | Nombre del abogado o bufete | "Dr. Juan Pérez" |
| `telefono` | Número de contacto | "+593999123456" |
| `direccion_completa` | Dirección completa | "Av. Amazonas 123, Quito" |
| `sitio_web` | URL del sitio web | "https://juanperez.com" |
| `rating_google_maps` | Calificación (0-5) | 4.5 |
| `numero_reseñas_google_maps` | Cantidad de reseñas | 120 |
| `categoria` | Categoría principal | "Abogado" |
| `link_google_maps` | URL al perfil | "https://maps.google.com/..." |
| `provincia` | Provincia | "Pichincha" |
| `email` | Correo electrónico (opcional) | "juan@juanperez.com" |

## 🧹 Limpieza del CSV

El script `limpiar_csv.py` realiza:

1. **Eliminación de duplicados** (por teléfono o nombre+dirección)
2. **Normalización de teléfonos** al formato ecuatoriano (+593XXXXXXXXX)
3. **Cálculo de calidad** del lead (Baja, Media, Alta, Premium, VIP)
4. **Ordenamiento** por provincia y calidad

### Criterios de Calidad

| Score | Nivel | Criterios |
|-------|-------|-----------|
| 0 | Baja | Sin teléfono, email, sitio web ni buen rating |
| 1 | Media | Solo teléfono |
| 2 | Alta | Teléfono + email o sitio web |
| 3 | Premium | Teléfono + email + sitio web |
| 4 | VIP | Todo lo anterior + rating ≥ 4.0 |

## 🔗 Integración con el Ecosistema

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Scrapling  │────▶│  CSV Limpio  │────▶│  Conector   │
│ (extracción)│     │ (normalizado)│     │ (Meta Ads)  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ MemoryPalace │
                    │  (registro)  │
                    └──────────────┘
```

### Flujo Completo

1. **Scrapling** extrae abogados de Google Maps → `abogados-ecuador.csv`
2. **Limpieza**: `limpiar_csv.py` normaliza y califica leads.
3. **Notificación**: Al terminar, el script dispara un mensaje vía **Conector Hub** informando al administrador.
4. **Meta Ads**: Claude usa la App aprobada 1650307639342860 para crear la audiencia oficial.
5. **MemoryPalace**: Se registra el hallazgo en la base de conocimiento global.

## 📝 Prompts Disponibles

### 1. Extracción Estándar
Usa `prompts/prompt-extraccion-abogados.md` para la extracción completa.

### 2. Extracción Rápida (solo teléfonos)
```text
Usa Scrapling para extraer SOLO abogados con teléfono visible en Google Maps.
Provincias: Imbabura, Pichincha, Cotopaxi.
Campos: nombre, telefono, provincia, link_google_maps.
Máximo 100 por provincia. Filtra los que no tengan teléfono.
```

### 3. Extracción Premium (con email)
```text
Extrae abogados con sitio web visible. Para cada uno:
1. Extrae datos de Google Maps
2. Visita el sitio web (si existe)
3. Busca email de contacto en la página
4. Agrega campo "email" al CSV
```

### 4. Extracción por Especialidad
```text
Busca abogados especializados en:
- "derecho informático"
- "propiedad intelectual"
- "derecho digital"
- "delitos informáticos"
Provincias: Imbabura, Pichincha, Cotopaxi.
```

## 🛠️ Comandos Útiles

```bash
# Instalar dependencias
pip install -r scripts/requirements.txt

# Limpiar CSV
python scripts/limpiar_csv.py abogados-ecuador.csv

# Limpiar CSV con nombre de salida personalizado
python scripts/limpiar_csv.py abogados-ecuador.csv output/abogados-limpio.csv

# Ver estructura del CSV
head -n 5 abogados-ecuador.csv
```

## 🔍 Solución de Problemas

### Scrapling no encuentra suficientes resultados
- Reduce el límite por provincia
- Prueba con términos de búsqueda más amplios ("legal", "leyes", "justicia")
- Verifica que el MCP de Scrapling esté conectado correctamente

### CSV con muchos campos vacíos
- Ejecuta una segunda pasada enfocada solo en perfiles con sitio web
- Usa la variante "Extracción Premium" para obtener emails

### Errores en el script de limpieza
- Verifica que pandas esté instalado: `pip install pandas`
- Asegúrate de que el CSV tenga las columnas esperadas

## 📊 Métricas de Éxito

| Métrica | Objetivo | Notas |
|---------|----------|-------|
| Total registros | 150-600 | 50-200 por provincia |
| Teléfonos válidos | >80% | Formato +593XXXXXXXXX |
| Emails | >20% | Para Custom Audience |
| Duplicados | <5% | Después de limpieza |

## 🔒 Seguridad

- **NUNCA** subas el CSV a GitHub (está en `.gitignore`)
- Los datos son para uso interno de SORSABSA
- Respeta las políticas de Google Maps y leyes de protección de datos

## 📚 Referencias

- [Guía Scrapling - tododeia](https://www.tododeia.com/community/scrapling-clientes-gratis)
- [Documentación Scrapling MCP](https://github.com/ scrapling/mcp)
- [Conector - Meta Ads](../Conector/)

---

> **Nota**: Este proyecto es independiente pero se integra con Conector y MemoryPalace.
> Construye y prueba por separado, integra después.