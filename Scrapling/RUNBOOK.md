# Scrapling — RUNBOOK (Abogados Ecuador → CSV)

## Objetivo
Extraer y exportar un **CSV** con contactos de **abogados** por provincia en **Ecuador**:
- Imbabura
- Pichincha
- Cotopaxi

## Requisitos previos
1. **Scrapling instalado** con MCP para Claude (según guía de tododeia)
2. **Claude Desktop / Claude Code** con el MCP conectado
3. **Python 3.11+** para el script de limpieza
4. **pandas instalado**: `pip install pandas`

## Flujo de Trabajo

### Paso 1: Preparar extracción
1. Abre Claude Desktop o Claude Code
2. Asegúrate de que Scrapling MCP esté conectado
3. Copia el prompt desde `prompts/prompt-extraccion-abogados.md`

### Paso 2: Ejecutar extracción
Pega el prompt maestro en Claude:

```text
Usa Scrapling para extraer ABAOGADOS (abogados / attorneys / legal) por provincia en Ecuador.
Provincias: Imbabura, Pichincha, Cotopaxi.

Para cada provincia quiero un CSV con estos campos:
- nombre
- telefono
- direccion_completa
- sitio_web
- rating_google_maps
- numero_reseñas_google_maps
- categoria
- link_google_maps
- provincia

Reglas:
- Deduplica por teléfono (si existe) y si no existe por nombre + dirección.
- Si no existe teléfono, deja la celda vacía (no inventes).
- Exporta un único CSV final llamado: abogados-ecuador-abogados.csv.
- Ordena por provincia y luego por numero_reseñas (desc).

Si encuentras menos registros que [LIMIT], dime cuántos encontraste por provincia.

LIMIT por provincia: [LIMIT]
```

**Ajusta `[LIMIT]`** según necesites:
- Mínimo recomendado: 50 por provincia
- Máximo recomendado: 200 por provincia

### Paso 3: Esperar resultados
- **Tiempo estimado**: 10-30 minutos
- Scrapling mostrará progreso por provincia
- Al finalizar, el CSV se guardará en la ubicación especificada

### Paso 4: Validar resultado
Verifica manualmente:
- [ ] El CSV tiene filas por las 3 provincias
- [ ] Las columnas coinciden con las solicitadas
- [ ] Hay al menos 50 registros por provincia (o el límite que definiste)

### Paso 5: Limpiar CSV
```bash
# Navega a la carpeta de Scrapling
cd Scrapling

# Ejecuta el script de limpieza
python scripts/limpiar_csv.py ../abogados-ecuador-abogados.csv

# El script generará: abogados-ecuador-limpio-[TIMESTAMP].csv
```

**Qué hace el script:**
1. Elimina duplicados restantes
2. Normaliza teléfonos al formato +593XXXXXXXXX
3. Calcula calidad del lead (Baja, Media, Alta, Premium, VIP)
4. Ordena por provincia y calidad
5. Genera estadísticas

### Paso 6: Usar en Conector
El CSV limpio está listo para:
1. **Conector**: Crear Custom Audience en Meta Ads
2. **PeritoDigital**: Campañas de WhatsApp (si aplica)
3. **MemoryPalace**: Registrar resultados en `memory/research.md`

## Validación del Resultado

### Checklist de Calidad
- [ ] **Total registros**: 150-600 (50-200 por provincia)
- [ ] **Teléfonos válidos**: >80% con formato +593...
- [ ] **Emails**: >20% (para Custom Audience)
- [ ] **Duplicados**: <5% después de limpieza
- [ ] **Campos vacíos**: <20% en campos críticos (nombre, teléfono)

### Si algo falla

#### Scrapling no encuentra suficientes resultados
- **Causa**: Términos de búsqueda muy específicos
- **Solución**: Usa términos más amplios ("legal", "leyes", "justicia")
- **Alternativa**: Reduce el límite y haz múltiples pasadas

#### CSV con muchos campos vacíos
- **Causa**: Perfiles incompletos en Google Maps
- **Solución**: Ejecuta variante "Extracción Premium" (con visita a sitio web)
- **Alternativa**: Acepta campos vacíos, el script de limpieza los manejará

#### Errores en el script de limpieza
- **Causa**: Columnas faltantes o formato incorrecto
- **Solución**: Verifica que el CSV tenga las columnas esperadas
- **Alternativa**: Ejecuta `head -n 5 abogados-ecuador.csv` para ver estructura

## Entregables

### Archivo Principal
- `abogados-ecuador-limpio-[TIMESTAMP].csv`

### Estadísticas Generadas
El script de limpieza mostrará:
```
📖 Leyendo abogados-ecuador.csv...
   Total registros iniciales: 450
   Duplicados por teléfono encontrados: 23
   Total después de eliminar duplicados: 427
   Teléfonos válidos: 380/427

✅ CSV limpio guardado como: abogados-ecuador-limpio-20260511-220000.csv
   Total registros finales: 427

📊 Estadísticas por provincia:
   Cotopaxi: 120 registros
      Calidad: {'Media': 45, 'Alta': 50, 'Premium': 20, 'VIP': 5}
   Imbabura: 130 registros
      Calidad: {'Media': 50, 'Alta': 55, 'Premium': 20, 'VIP': 5}
   Pichincha: 177 registros
      Calidad: {'Media': 60, 'Alta': 70, 'Premium': 35, 'VIP': 12}
```

## Variantes del Prompt

### Extracción Rápida (solo teléfonos)
```text
Usa Scrapling para extraer SOLO abogados con teléfono visible en Google Maps.
Provincias: Imbabura, Pichincha, Cotopaxi.
Campos: nombre, telefono, provincia, link_google_maps.
Máximo 100 por provincia. Filtra los que no tengan teléfono.
```

### Extracción Premium (con email)
```text
Extrae abogados con sitio web visible. Para cada uno:
1. Extrae datos de Google Maps
2. Visita el sitio web (si existe)
3. Busca email de contacto en la página
4. Agrega campo "email" al CSV
Nota: Esto tomará más tiempo pero la calidad es mayor.
```

### Extracción por Especialidad
```text
Busca abogados especializados en:
- "derecho informático"
- "propiedad intelectual"
- "derecho digital"
- "delitos informáticos"
Provincias: Imbabura, Pichincha, Cotopaxi.
Estos son los prospectos más calificados para SORSABSA.
```

## Integración con el Ecosistema

### Después de generar el CSV

1. **Conector** (Meta Ads):
   - Usa el CSV para crear Custom Audience
   - Segmenta por provincia para campañas locales
   - Prioriza leads Premium y VIP

2. **MemoryPalace**:
   - Registra resultados en `memory/research.md`
   - Actualiza `memory/INDEX.md` con nueva entrada
   - Documenta lecciones aprendidas

3. **PeritoDigital**:
   - Opcional: Usa la lista para campañas de WhatsApp
   - Segmenta por calidad de lead

## Comandos Rápidos

```bash
# 1. Extraer (en Claude)
# Copia y pega el prompt desde prompts/prompt-extraccion-abogados.md

# 2. Limpiar CSV
python scripts/limpiar_csv.py abogados-ecuador.csv

# 3. Ver estadísticas
python scripts/limpiar_csv.py abogados-ecuador.csv --stats-only

# 4. Ver primeras filas
head -n 5 abogados-ecuador.csv
```

## Notas Importantes

1. **Tiempo de extracción**: 10-30 minutos (no interrumpas)
2. **Calidad sobre cantidad**: Mejor 150 registros con teléfonos válidos que 600 sin teléfonos
3. **Privacidad**: Los datos son para uso interno de SORSABSA
4. **Actualización**: Ejecuta extracciones mensuales para mantener la lista actualizada

## Solución de Problemas Avanzada

### Scrapling se cuelga
- **Causa**: Timeout de red o límite de rate de Google
- **Solución**: Reinicia Scrapling y reduce el límite por provincia

### CSV corrupto
- **Causa**: Interrupción durante la exportación
- **Solución**: Vuelve a ejecutar la extracción con un límite menor

### Teléfonos no se normalizan
- **Causa**: Formato inconsistente en los datos originales
- **Solución**: Revisa el script `limpiar_csv.py` y ajusta las reglas de normalización

---

**Próximo paso**: Una vez generado el CSV limpio, úsalo en **Conector** para crear campañas de Meta Ads.