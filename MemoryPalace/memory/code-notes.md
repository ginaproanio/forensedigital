# Code Notes — Decisiones de Código

> Patrones, trampas, gotchas y decisiones de implementación. Escrito por el coder.

---

## Formato de entrada

Cada entrada debe seguir este formato:

```markdown
## [YYYY-MM-DD] [coder] — Título (proyecto/archivo)

### Patrón/Solución
Descripción del patrón o solución implementada.

### Código
```python
# Ejemplo de código
```

### Trampas/Gotchas
- Advertencia 1
- Advertencia 2

### Referencias
- Enlace a decisión en decisions.md (si aplica)
```

---

## Entradas

<!-- Las entradas nuevas se agregan aquí, en orden cronológico inverso (más reciente primero) -->

---

## Patrones Comunes

### 1. Respuesta Inmediata + Procesamiento en Background
**Problema**: Webhooks de WhatsApp requieren respuesta en <10s, pero el procesamiento de IA tarda más.

**Solución**:
```python
@app.post("/webhook")
async def webhook(request: Request):
    # 1. Validar y extraer datos (rápido)
    # 2. Crear tarea en background
    asyncio.create_task(procesar_mensaje_async(...))
    # 3. Responder inmediatamente
    return {"status": "ok", "mensaje": "Procesando en background"}
```

**Trampas**:
- Asegurarse de que la tarea en background no lance excepciones no manejadas
- Logging adecuado para depurar problemas

### 2. Deduplicación por msg.id
**Problema**: Proveedores de WhatsApp reintentan webhooks, causando procesamiento duplicado.

**Solución**:
```python
mensajes_procesados = set()

async def procesar_mensaje(msg_id, ...):
    if msg_id in mensajes_procesados:
        logger.info(f"Mensaje duplicado ignorado: {msg_id}")
        return
    mensajes_procesados.add(msg_id)
    # Limitar tamaño del set
    if len(mensajes_procesados) > 1000:
        for _ in range(100):
            mensajes_procesados.pop()
```

**Trampas**:
- El set puede crecer indefinidamente → limitar tamaño
- Reinicio del servidor pierde el set → acceptable (es temporal)

### 3. Historial de Conversación por Cliente
**Problema**: Cada cliente necesita su propio historial de conversación.

**Solución**:
```python
async def obtener_historial(telefono: str, limite: int = 20) -> list[dict]:
    # Query por telefono, ordenar por timestamp, limitar a N mensajes
    async with async_session() as session:
        query = (
            select(Mensaje)
            .where(Mensaje.telefono == telefono)
            .order_by(Mensaje.timestamp.desc())
            .limit(limite)
        )
        result = await session.execute(query)
        return [...]
```

**Trampas**:
- SQLite no soporta concurrencia alta → usar PostgreSQL en producción
- No olvidar invertir el orden (los más recientes primero en query, pero orden cronológico en respuesta)

---

## Gotchas Conocidos

### 1. SQLite en Railway
**Problema**: SQLite se reinicia con cada deploy en Railway, perdiendo datos.

**Solución**: Migrar a PostgreSQL. Railway ofrece PostgreSQL gratis en el plan starter.

### 2. Timeouts de Webhook
**Problema**: Whapi/Meta esperan respuesta en <10s. Si el procesamiento tarda más, reintentan.

**Solución**: Respuesta 200 OK inmediata + procesamiento en background.

### 3. API Keys en Código
**Problema**: API keys hardcodeadas son riesgo de seguridad.

**Solución**: Siempre usar variables de entorno con python-dotenv. Nunca commitear `.env`.

### 4. Async/Await Mal Usado
**Problema**: Mezclar código síncrono y asíncrono bloquea el event loop.

**Solución**:
- Todas las funciones I/O deben ser `async def`
- Usar `await` para llamadas a APIs, DB, archivos
- No usar `time.sleep()` en código async (usar `asyncio.sleep()`)

---

## Referencias a Decisiones

- [2026-05-11] [orquestador] → decisions.md#stack-tecnológico-unificado — Stack unificado
- [2026-05-11] [orquestador] → decisions.md#estrategia-de-deploy — Deploy en Railway