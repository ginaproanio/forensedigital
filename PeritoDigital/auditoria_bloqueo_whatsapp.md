# 🚨 AUDITORÍA DE BLOQUEO WHATSAPP - PERITO DIGITAL (VERSIÓN CORREGIDA)

**Fecha:** 11 de mayo de 2026  
**Estado:** Cuenta en revisión/bloqueo  
**Proveedor Actual:** Whapi.cloud (proveedor legítimo, no scraper informal)

---

## 🔍 CAUSAS REALES DEL BLOQUEO (Análisis Preciso)

### 1. **COMPORTAMIENTO DEL BOT - VOLUMEN/VELOCIDAD** ⚠️ ALTO RIESGO
- **Problema real:** El bot respondía demasiado rápido o en volumen que parece spam
- **Evidencia:** No hay rate limiting ni control de frecuencia de mensajes
- **Impacto:** WhatsApp detecta patrones de automatización y bloquea

### 2. **REINTENTOS EN CADENA POR TIMEOUTS** ⚠️ ALTO RIESGO
- **Problema:** El webhook no respondía 200 OK inmediatamente
- **Consecuencia:** Whapi reintentaba el mismo mensaje múltiples veces
- **Resultado:** El bot procesaba y respondía el mismo mensaje varias veces → spam
- **Código anterior:** `agent/main.py` procesaba sincrónicamente (bloqueante)

### 3. **FALTA DE DEDUPLICACIÓN DE MENSAJES** ⚠️ MEDIO RIESGO
- **Problema:** No se verificaba `msg.id` para evitar procesamiento duplicado
- **Consecuencia:** Si Whapi reintentaba, se generaban múltiples respuestas idénticas
- **Impacto:** WhatsApp interpreta esto como comportamiento de spam automatizado

### 4. **TIMEOUT EXCESIVO EN ENVÍOS** ⚠️ MEDIO RIESGO
- **Problema:** Timeout de 15s en `whapi.py` era demasiado alto
- **Consecuencia:** Si Groq tardaba + enviaba, superaba el timeout de Whapi
- **Resultado:** Whapi reintentaba → más respuestas duplicadas

### 5. **BASE DE DATOS VOLÁTIL (SQLite en Railway)** ⚠️ BAJO RIESGO
- **Problema:** SQLite se reinicia con cada deploy en Railway
- **Impacto:** Pérdida de contexto → respuestas inconsistentes
- **Riesgo de bloqueo:** Bajo, pero afecta calidad del servicio

---

## 📊 ACLARACIONES IMPORTANTES

### ✅ **Whapi.cloud NO es la causa principal**
- Whapi es un proveedor legítimo y pagado
- El bloqueo no es automático por usar Whapi
- El problema es el **comportamiento del bot**, no el proveedor

### ✅ **Archivo de verificación de Meta**
- `wbcp2ibxirdp01qdsuy2mirvyiul0t.html` es verificación de dominio de Meta
- Indica que en algún momento intentaron Meta Cloud API directo
- No es verificación de webhook de Whapi

### ✅ **Bug del historial[:-1]**
- El código funcionaba pero era confuso
- Se pasa historial sin el último mensaje + texto por separado
- No es causa de bloqueo, pero es mala práctica

---

## 🛠️ SOLUCIONES IMPLEMENTADAS (CORRECCIONES TÉCNICAS)

### ✅ **1. Respuesta 200 OK Inmediata (IMPLEMENTADO)**
```python
# ANTES: Procesamiento sincrónico bloqueante
@app.post("/webhook")
async def webhook(request: Request):
    # ... procesar todo (IA tarda 5-10s)
    return {"status": "ok"}  # Whapi espera >10s → reintenta

# AHORA: Respuesta inmediata + procesamiento en background
@app.post("/webhook")
async def webhook(request: Request):
    # ... validar y extraer datos
    asyncio.create_task(procesar_mensaje_async(...))  # Background
    return {"status": "ok", "mensaje": "Procesando en background"}  # Inmediato
```

**Impacto:** Whapi recibe 200 OK en <1s → no reintenta → no hay spam

### ✅ **2. Deduplicación por msg.id (IMPLEMENTADO)**
```python
mensajes_procesados = set()  # Global

@app.post("/webhook")
async def webhook(request: Request):
    msg_id = msg.get("id", "")
    
    if msg_id and msg_id in mensajes_procesados:
        logger.info(f"⚠️ Mensaje duplicado ignorado: {msg_id}")
        return {"status": "duplicado"}
    
    mensajes_procesados.add(msg_id)
    # Limitar tamaño del set (máx 1000)
    if len(mensajes_procesados) > 1000:
        for _ in range(100):
            mensajes_procesados.pop()
```

**Impacto:** Si Whapi reintenta, el segundo intento se ignora → no hay respuestas duplicadas

### ✅ **3. Timeout Reducido a 8s (IMPLEMENTADO)**
```python
# ANTES: timeout=15 (demasiado alto)
async with httpx.AsyncClient(timeout=15) as client:

# AHORA: timeout=8.0 (más razonable)
async with httpx.AsyncClient(timeout=8.0) as client:
```

**Impacto:** Si Groq tarda mucho, falla rápido en lugar de colgar la conexión

### ✅ **4. Logging Estructurado (IMPLEMENTADO)**
```python
import logging
logger = logging.getLogger(__name__)

# En webhook:
logger.info(f"📩 Mensaje recibido de {telefono}: {texto[:60]}... (ID: {msg_id})")

# En procesamiento:
logger.info(f"🔄 Procesando mensaje {msg_id} de {telefono}")
logger.info(f"{'✅' if enviado else '❌'} Respuesta enviada a {telefono}")
```

**Impacto:** Podemos monitorear comportamiento y depurar problemas

---

## 📋 PRÓXIMOS PASOS RECOMENDADOS

### **INMEDIATO (Ya implementado):**
- [x] Respuesta 200 OK inmediata al webhook
- [x] Deduplicación por msg.id
- [x] Timeout reducido a 8s
- [x] Logging estructurado

### **CORTO PLAZO (Esta semana):**
- [ ] **Monitorear comportamiento:** Revisar logs para ver si Whapi sigue reintentando
- [ ] **Rate limiting básico:** Si ves muchos mensajes salientes, agregar control de frecuencia
- [ ] **Apelar bloqueo:** Contactar a WhatsApp/Whapi para levantar el bloqueo actual

### **MEDIANO PLAZO (Próximas 2 semanas):**
- [ ] **Migrar a PostgreSQL:** Para evitar pérdida de contexto en Railway
- [ ] **Implementar circuit breaker:** Si Groq falla mucho, no intentar endlessly
- [ ] **Agregar health checks:** Monitorear si el bot está respondiendo correctamente

---

## 🎯 EXPECTATIVAS REALISTAS

### **¿Esto resolverá el bloqueo?**
- **Probabilidad alta:** Las correcciones atacan las causas reales (reintentos, duplicación)
- **Tiempo estimado:** 24-48 horas después de deploy para que WhatsApp re-evalúe
- **Si persiste:** Podría ser necesario contactar soporte de WhatsApp/Whapi

### **¿Necesito migrar a Meta Cloud API?**
- **No urgentemente:** Whapi es legítimo y funciona
- **Considerar a futuro:** Si el bloqueo persiste a pesar de las correcciones
- **Ventaja de Meta:** Control total, menos intermediarios

---

## 🔧 COMANDOS PARA DEPLOY

```bash
# 1. Hacer commit de los cambios
cd PeritoDigital
git add .
git commit -m "fix: respuesta inmediata webhook + deduplicación para evitar bloqueo"

# 2. Push a Railway (se deploya automático)
git push origin main

# 3. Monitorear logs en Railway
# Railway Dashboard → Logs → Filtrar por "Procesando mensaje"

# 4. Verificar que no hay reintentos
# Buscar en logs: "Mensaje duplicado ignorado"
```

---

## 📞 CONTACTO DE EMERGENCIA

Si después de 48 horas el bloqueo persiste:

1. **Contactar a Whapi Support:**
   - Explicar que implementaste deduplicación y respuesta inmediata
   - Pedir que revisen logs de su lado

2. **Apelar en WhatsApp Business:**
   - Ir a Meta Business Suite
   - Sección "Calidad del número" → "Solicitar revisión"

3. **Considerar número nuevo:**
   - Si el número actual está permanentemente bloqueado
   - Migrar a Meta Cloud API directamente

---

**Estado:** ✅ Soluciones técnicas implementadas  
**Próxima acción:** Deploy a Railway y monitoreo de logs  
**Expectativa:** Levantamiento de bloqueo en 24-48 horas