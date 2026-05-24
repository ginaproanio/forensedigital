# Investigación — Memory Palace SORSABSA

> Hallazgos de investigación, análisis técnicos y descubrimientos relevantes para el ecosistema.

---

## [2026-05-11] [investigador] — Análisis del estado actual de PeritoDigital

### Hallazgos
1. **Estructura existente**:
   - AgentKit completo con main.py, brain.py, memory.py, tools.py
   - Knowledge base: `knowledge/sorsabsa.txt` con información de SORSABSA
   - Deploy en Railway con nixpacks.toml
   - Problemas de bloqueo de WhatsApp documentados en `auditoria_bloqueo_whatsapp.md`

2. **Problemas identificados**:
   - Bloqueo de WhatsApp por reintentos y falta de deduplicación
   - SQLite volátil en Railway (se reinicia con cada deploy)
   - Falta integración con Google Calendar para citas
   - No hay function calling para acciones (solo responde texto)

3. **Oportunidades**:
   - Ya tiene base sólida para agente de WhatsApp
   - Knowledge base completa y actualizada
   - Documentación técnica detallada (auditorías)

### Acciones recomendadas
- [ ] Implementar deduplicación por msg.id (ya documentado en auditoria_bloqueo_whatsapp.md)
- [ ] Migrar a PostgreSQL en Railway
- [ ] Integrar Google Calendar API
- [ ] Agregar function calling para agendar citas

---

## [2026-05-11] [investigador] — Análisis del estado actual de Conector

### Hallazgos
1. **Estructura existente**:
   - MCP server de Meta Ads configurado
   - App ID: `1650307639342860`
   - Scripts de setup para Windows y Linux
   - Plantillas de prompts en `prompts/`
   - RUNBOOK.md con instrucciones operativas

2. **Capacidades**:
   - Crear campañas en PAUSED (seguridad)
   - Reportes semanales de desempeño
   - Auditoría de pixel/dataset
   - Integración con Claude vía MCP

3. **Estado**:
   - Configuración inicial completada
   - Pendiente: configurar variables de entorno (.env)
   - Pendiente: probar conexión con Meta Ads API

### Acciones recomendadas
- [ ] Completar .env con META_ACCESS_TOKEN y META_AD_ACCOUNT_ID
- [ ] Probar conexión con `meta ads campaign list`
- [ ] Crear primera campaña de prueba (en PAUSED)

---

## [2026-05-11] [investigador] — Patrones de diseño para agentes coordinados

### Investigación
Basado en el protocolo Memory Palace, identificamos estos patrones:

1. **Patrón Cuaderno Compartido**:
   - Un solo lugar de verdad para cada tipo de información
   - Permisos de escritura claros por rol
   - Trazabilidad completa de cambios

2. **Patrón Orquestador-Trabajadores**:
   - Orquestador toma decisiones estratégicas
   - Trabajadores (agentes) ejecutan tareas específicas
   - Comunicación asíncrona vía archivos compartidos

3. **Patrón Fuente Única de Verdad**:
   - Knowledge base en un solo lugar (PeritoDigital/knowledge/)
   - Otros proyectos referencian, no copian
   - Actualizaciones automáticas

### Aplicación a SORSABSA
- MemoryPalace = Orquestador
- PeritoDigital = Trabajador (atención al cliente)
- Conector = Trabajador (marketing/ads)
- memory/ = Cuaderno compartido

---

## [2026-05-11] [investigador] — Mejores prácticas para agentes Claude

### Hallazgos
1. **System Prompts efectivos**:
   - Identidad clara del agente
   - Reglas de comportamiento explícitas
   - Límites de lo que NO debe hacer
   - Ejemplos de respuestas correctas

2. **Gestión de contexto**:
   - Historial de conversación por cliente
   - Límite de tokens (20 mensajes recientes)
   - Resumen de conversaciones largas

3. **Error handling**:
   - Mensajes de fallback para errores
   - Reintentos con backoff exponencial
   - Logging estructurado para debugging

### Aplicación a PeritoDigital
- Actualizar system prompt en `config/prompts.yaml`
- Implementar circuit breaker para errores de API
- Agregar logging estructurado (ya hecho en auditoria_bloqueo_whatsapp.md)

---

## [2026-05-11] [investigador] — Integración de MCP servers

### Investigación
Los MCP (Model Context Protocol) servers permiten extender Claude con capacidades especializadas:

1. **MCP de Meta Ads** (ya configurado en Conector):
   - URL: `https://mcp.facebook.com/ads`
   - Comandos: campaign create/list/update, insights get, pixel validate
   - Configuración: mcp-config.json + variables de entorno

2. **Otros MCP disponibles**:
   - FileSystem: Acceso a archivos locales
   - PostgreSQL: Consultas a base de datos
   - GitHub: Gestión de repositorios
   - Slack: Integración con Slack

### Oportunidades para SORSABSA
- [ ] MCP de PostgreSQL para consultas directas a Supabase
- [ ] MCP de FileSystem para gestión de expedientes
- [ ] MCP de Calendar para integración con Google Calendar

---

## [2026-05-11] [investigador] — Estrategias anti-bloqueo de WhatsApp

### Investigación
Basado en `auditoria_bloqueo_whatsapp.md`:

1. **Causas de bloqueo**:
   - Reintentos de webhook por timeout >10s
   - Mensajes duplicados por falta de deduplicación
   - Comportamiento que parece spam (muchos mensajes rápidos)
   - Reportes de usuarios (poco probable en este caso)

2. **Soluciones implementadas**:
   - Respuesta 200 OK inmediata + procesamiento en background
   - Deduplicación por msg.id
   - Timeout reducido a 8s
   - Logging estructurado

3. **Soluciones pendientes**:
   - Rate limiting de mensajes salientes
   - Migración a PostgreSQL para evitar bloqueos de SQLite
   - Circuit breaker para errores de Groq API

### Recomendación
Las soluciones ya están documentadas en el código de PeritoDigital. Solo falta deploy y monitoreo.

---

## Bloqueos Activos
- [ ] PeritoDigital: Bloqueo de WhatsApp (soluciones implementadas, pendiente deploy)
- [ ] Conector: Falta configurar variables de entorno
- [ ] MemoryPalace: Falta configurar roles en .claude/agents/

## Unknowns (preguntas sin respuesta)
- ¿Cómo manejar datos sensibles en memoria compartida?
- ¿Qué métricas de éxito usar para el ecosistema?
- ¿Cuánto cuesta Railway en producción con PostgreSQL?