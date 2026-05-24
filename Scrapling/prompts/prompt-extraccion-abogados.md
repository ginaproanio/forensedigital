# Prompt Maestro — Extracción de Abogados Ecuador

## Contexto
Este prompt está optimizado para usar con **Scrapling MCP** en Claude Desktop/Code. Extrae contactos de abogados de Google Maps en 3 provincias de Ecuador.

## Prompt para Copiar/Pegar

```text
Eres un especialista en extracción de datos con Scrapling. Tu tarea es generar una lista de prospectos (abogados) para campañas de marketing de SORSABSA (empresa de peritaje informático forense).

## Objetivo
Extraer abogados de Google Maps en Ecuador, provincias: Imbabura, Pichincha, Cotopaxi.

## Campos requeridos en el CSV
- nombre: Nombre del abogado o bufete
- telefono: Número de contacto (si existe)
- direccion_completa: Dirección completa tal como aparece
- sitio_web: URL del sitio web (si existe, si no dejar vacío)
- rating_google_maps: Calificación numérica (ej: 4.5)
- numero_reseñas_google_maps: Cantidad de reseñas
- categoria: Categoría principal (ej: "Abogado", "Bufete", etc.)
- link_google_maps: URL directa al perfil de Google Maps
- provincia: Provincia correspondiente (Imbabura, Pichincha, Cotopaxi)
- email: Correo electrónico (si se puede inferir del sitio web, opcional)

## Reglas de extracción
1. **Búsqueda**: Usa términos como "abogado", "attorney", "bufete", "estudio jurídico" + nombre de la provincia
2. **Deduplicación**: 
   - Por teléfono (si existe)
   - Por nombre + dirección (si no hay teléfono)
3. **Calidad**: Prioriza perfiles con:
   - Teléfono visible
   - Al menos 5 reseñas
   - Sitio web (indica profesionalismo)
4. **Limpieza**:
   - No inventes teléfonos ni emails
   - Si un campo no existe, déjalo vacío
   - Normaliza teléfonos al formato: +593XXXXXXXXX

## Formato de salida
- **Único CSV** llamado: `abogados-ecuador-[FECHA].csv`
- **Orden**: Por provincia (alfabético) y luego por número_de_reseñas (descendente)
- **Codificación**: UTF-8

## Límite por provincia
- **Mínimo**: 50 abogados por provincia
- **Máximo**: 200 abogados por provincia
- **Total esperado**: 150-600 registros

## Validación
Antes de exportar, verifica:
- [ ] Todas las provincias están representadas
- [ ] No hay duplicados por teléfono
- [ ] Los teléfonos tienen formato ecuatoriano (+593...)
- [ ] Las direcciones son completas
- [ ] Los ratings son numéricos (0-5)

## Instrucciones especiales para SORSABSA
Estos abogados son prospectos para:
1. **Campañas de Meta Ads** (Conector) → Necesitamos emails y teléfonos
2. **Contacto directo** → Teléfonos válidos son críticos
3. **Segmentación por provincia** → Importante para campañas locales

Prioriza calidad sobre cantidad. Mejor 150 registros con teléfonos válidos que 600 sin teléfonos.

## Ejecución
1. Inicia la extracción provincia por provincia
2. Muestra progreso: "Extrayendo Pichincha... 45/200 encontrados"
3. Al finalizar, reporta:
   - Total por provincia
   - Registros con teléfono válido
   - Registros con email
   - Duplicados eliminados
4. Exporta el CSV

¡Comienza la extracción!
```

---

## Variantes del Prompt

### 1. Extracción Rápida (solo teléfonos)
```text
Usa Scrapling para extraer SOLO abogados con teléfono visible en Google Maps.
Provincias: Imbabura, Pichincha, Cotopaxi.
Campos: nombre, telefono, provincia, link_google_maps.
Máximo 100 por provincia. Filtra los que no tengan teléfono.
```

### 2. Extracción Premium (con email)
```text
Extrae abogados con sitio web visible. Para cada uno:
1. Extrae datos de Google Maps
2. Visita el sitio web (si existe)
3. Busca email de contacto en la página
4. Agrega campo "email" al CSV
Nota: Esto tomará más tiempo pero la calidad es mayor.
```

### 3. Extracción por Especialidad
```text
Busca abogados especializados en:
- "derecho informático"
- "propiedad intelectual"
- "derecho digital"
- "delitos informáticos"
Provincias: Imbabura, Pichincha, Cotopaxi.
Estos son los prospectos más calificados para SORSABSA.
```

---

## Notas para el Usuario

1. **Tiempo estimado**: 10-30 minutos dependiendo del límite
2. **Requisitos**: Scrapling MCP configurado en Claude
3. **Salida**: CSV en la carpeta que especifiques
4. **Integración**: Este CSV se usará en Conector para crear audiencias personalizadas

## Solución de Problemas

### Scrapling no encuentra suficientes resultados
- Reduce el límite por provincia
- Prueba con términos de búsqueda más amplios ("legal", "leyes", "justicia")
- Verifica que el MCP de Scrapling esté conectado correctamente

### CSV con muchos campos vacíos
- Ejecuta una segunda pasada enfocada solo en perfiles con sitio web
- Usa la variante "Extracción Premium" para obtener emails

### Duplicados después de la extracción
- Ejecuta este comando Python para limpiar:
```python
import pandas as pd
df = pd.read_csv('abogados-ecuador.csv')
df = df.drop_duplicates(subset=['telefono', 'nombre+direccion'])
df.to_csv('abogados-ecuador-limpio.csv', index=False)
```

## Próximos Pasos (Integración)

1. **CSV generado** → `output/abogados-ecuador-[FECHA].csv`
2. **Conector** → Usa este CSV para crear Custom Audience en Meta Ads
3. **MemoryPalace** → Registra resultados en `memory/research.md`
4. **PeritoDigital** → Usa la lista para campañas de WhatsApp (si aplica)