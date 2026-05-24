# 🚀 PLAN DE DEPLOY - SOLUCIÓN ANTIBLOQUEO

**Objetivo:** Resolver el bloqueo de WhatsApp implementando respuesta inmediata + deduplicación

---

## 📝 RESUMEN DE CAMBIOS REALIZADOS

### ✅ **Archivos Modificados:**
1. **`agent/main.py`** - Respuesta 200 OK inmediata + procesamiento en background + deduplicación
2. **`agent/whapi.py`** - Timeout reducido de 15s a 8s
3. **`auditoria_bloqueo_whatsapp.md`** - Auditoría corregida y precisa

### 🆕 **Archivos Nuevos:**
1. **`auditoria_bloqueo_whatsapp.md`** - Análisis técnico del bloqueo
2. **`PLAN_DEPLOY_ANTIBLOQUEO.md`** - Este archivo

---

## 🔧 PASOS PARA DEPLOY

### **Paso 1: Verificar cambios locales**
```bash
cd PeritoDigital
git status
```

Deberías ver:
- `agent/main.py` modificado
- `agent/whapi.py` modificado
- `auditoria_bloqueo_whatsapp.md` nuevo (o modificado)

### **Paso 2: Hacer commit**
```bash
git add .
git commit -m "fix: respuesta inmediata webhook + deduplicación para evitar bloqueo de WhatsApp

- Respuesta 200 OK inmediata al webhook (evita reintentos de Whapi)
- Deduplicación por msg.id (previene respuestas duplicadas)
- Timeout reducido a 8s en envíos a Whapi
- Logging estructurado para monitoreo
- Auditoría técnica actualizada"
```

### **Paso 3: Push a Railway**
```bash
git push origin main
```

Railway detectará el push y desplegará automáticamente.

### **Paso 4: Monitorear deploy**
1. Ve a [Railway Dashboard](https://railway.app)
2. Selecciona tu proyecto "PeritoDigital"
3. Click en "Deployments" → Verás el nuevo deploy en progreso
4. Espera a que diga "Deployed" (verde)

---

## 🔍 MONITOREO POST-DEPLOY

### **Inmediato (primeras 2 horas):**

1. **Revisar logs en Railway:**
   ```
   Railway Dashboard → Tu proyecto → Logs
   ```

2. **Buscar estos patrones:**
   - ✅ `"Procesando mensaje {msg_id} de {telefono}"` - Mensajes procesándose
   - ⚠️ `"Mensaje duplicado ignorado: {msg_id}"` - Deduplicación funcionando
   - ❌ `"Error procesando mensaje"` - Errores (investigar)

3. **Verificar respuesta rápida:**
   - Los logs deberían mostrar `"📩 Mensaje recibido"` y casi inmediatamente `"Procesando en background"`
   - Si ves demora entre estos dos, algo está mal

### **Primeras 24 horas:**

1. **Contar mensajes duplicados:**
   ```bash
   # En Railway logs, busca:
   "Mensaje duplicado ignorado"
   ```
   - Si ves varios, la deduplicación está funcionando ✅
   - Si no ves ninguno, puede que Whapi no esté reintentando (buena señal)

2. **Verificar que no hay timeouts:**
   - Busca en logs: `"Error Whapi al enviar"`
   - Deberían ser pocos o ninguno

3. **Monitorear tiempo de respuesta de Groq:**
   - Fíjate en el tiempo entre `"🔄 Procesando mensaje"` y `"✅ Respuesta enviada"`
   - Debería ser 3-8 segundos típicamente

### **48 horas:**

1. **Evaluar si el bloqueo se levantó:**
   - Intenta enviar mensajes desde otro número a tu WhatsApp business
   - Debería responder normalmente

2. **Si persiste el bloqueo:**
   - Contactar a Whapi Support
   - Apelar en Meta Business Suite

---

## 🚨 POSIBLES PROBLEMAS Y SOLUCIONES

### **Problema 1: Deploy falla en Railway**
**Síntoma:** El deploy se queda en "Building" o falla

**Solución:**
```bash
# 1. Verificar que requirements.txt está actualizado
cat requirements.txt

# 2. Si falta algo, agregar y hacer commit de nuevo
echo "nueva-dependencia==1.0.0" >> requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

### **Problema 2: Mensajes no se procesan**
**Síntoma:** Logs muestran `"📩 Mensaje recibido"` pero no `"🔄 Procesando mensaje"`

**Posibles causas:**
1. **Error en extracción:** Revisar logs de `extraer_mensaje`
2. **Error en background task:** Revisar logs de `procesar_mensaje_async`
3. **Problema de permisos:** Verificar que `.env` tenga `WHAPI_TOKEN` y `GROQ_API_KEY`

**Diagnóstico:**
```bash
# En Railway, revisar variables de entorno
Railway Dashboard → Variables → Verificar:
- WHAPI_TOKEN
- GROQ_API_KEY
- DATABASE_URL (si usas PostgreSQL)
```

### **Problema 3: Muchas duplicaciones**
**Síntoma:** Logs muestran muchos `"Mensaje duplicado ignorado"`

**Causa probable:** El procesamiento en background está tardando demasiado

**Solución:**
1. Revisar tiempo de respuesta de Groq (puede estar lento)
2. Considerar reducir `max_tokens` en `brain.py`
3. Verificar conexión a base de datos (SQLite puede estar bloqueado)

### **Problema 4: SQLite se bloquea**
**Síntoma:** Errores de base de datos en logs

**Causa:** SQLite no está diseñado para concurrencia alta

**Solución temporal:**
```python
# En agent/database.py, agregar al inicio de cada función:
import asyncio
await asyncio.sleep(0.1)  # Pequeña pausa para evitar bloqueos
```

**Solución permanente:** Migrar a PostgreSQL (ver sección siguiente)

---

## 🔄 MIGRACIÓN A POSTGRESQL (RECOMENDADO)

Si después del deploy ves problemas de SQLite, migra a PostgreSQL:

### **Paso 1: Crear PostgreSQL en Railway**
1. Railway Dashboard → Tu proyecto → New → PostgreSQL
2. Esperar a que se cree (2-3 minutos)

### **Paso 2: Actualizar variables de entorno**
Railway automáticamente agregará `DATABASE_URL` con la conexión a PostgreSQL.

### **Paso 3: Actualizar código (si es necesario)**
El código actual ya soporta PostgreSQL si usas la URL correcta.

En `agent/database.py`, la línea:
```python
DB_PATH = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./agentkit.db").replace("sqlite+aiosqlite:///", "")
```

Esta línea asume SQLite. Para PostgreSQL, necesitas un enfoque diferente.

**Opción A: Mantener SQLite por ahora** (si no hay problemas)
**Opción B: Migrar a PostgreSQL** (si hay problemas de concurrencia)

Si eliges Opción B, avísame y te ayudo a actualizar `database.py`.

---

## 📊 MÉTRICAS DE ÉXITO

### **Señales de que está funcionando:**
- ✅ Deploy exitoso en Railway
- ✅ Logs muestran procesamiento de mensajes
- ✅ Respuestas se envían correctamente
- ✅ No hay errores masivos de Whapi
- ✅ Después de 24-48h, WhatsApp responde normalmente

### **Señales de alerta:**
- ❌ Errores constantes de base de datos
- ❌ Mensajes que nunca se procesan
- ❌ Timeouts frecuentes (>20% de los mensajes)
- ❌ Crecimiento rápido del set de duplicados (>100 por hora)

---

## 🆘 CONTACTO DE SOPORTE

Si después de seguir estos pasos el problema persiste:

### **Whapi Support:**
- Email: support@whapi.cloud
- Explicar: "Implementé deduplicación y respuesta inmediata, pero persiste el bloqueo"
- Adjuntar: Logs de Railway (últimas 24h)

### **WhatsApp Business:**
- Meta Business Suite → Ayuda → Contactar soporte
- Sección: "Calidad del número" → "Solicitar revisión"

---

## 📞 CHECKLIST PRE-DEPLOY

Antes de hacer push, verifica:

- [ ] Probaste localmente con `uvicorn agent.main:app --reload`
- [ ] Verificaste que `WHAPI_TOKEN` y `GROQ_API_KEY` están en Railway
- [ ] Revisaste que no hay errores de sintaxis en los archivos
- [ ] Tienes acceso al Railway Dashboard para monitorear

---

**¡Listo! Una vez hecho el push, monitorea los logs y reporta cualquier anomalía.**

**Estado:** ✅ Código listo para deploy  
**Próximo paso:** `git push origin main`  
**Expectativa:** Deploy automático en Railway + monitoreo de logs