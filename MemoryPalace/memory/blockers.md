# Bloqueos y Unknowns

> Registro de bloqueos activos, unknowns y dependencias externas que impiden el avance.

---

## Bloqueos Activos

### [2026-05-11] [orquestador] — Bloqueo de WhatsApp en PeritoDigital

**Estado**: 🟡 Parcialmente resuelto (soluciones implementadas, pendiente deploy)

**Descripción**:
- El número de WhatsApp de PeritoDigital está bloqueado por Meta
- Causa: Reintentos de webhook y mensajes duplicados por falta de deduplicación

**Impacto**:
- PeritoDigital no puede atender clientes vía WhatsApp
- Pérdida de oportunidades de negocio
- Necesidad de usar número alternativo temporal

**Acciones tomadas**:
1. ✅ Implementada deduplicación por msg.id en `agent/main.py`
2. ✅ Respuesta 200 OK inmediata + procesamiento en background
3. ✅ Timeout reducido a 8s en `agent/whapi.py`
4. ✅ Logging estructurado agregado

**Próximos pasos**:
1. Deploy a Railway de los cambios
2. Monitoreo de logs por 24-48 horas
3. Si persiste: contactar a Whapi Support y apelar en Meta

**Responsable**: Coder (deploy) + Orquestador (monitoreo)

---

### [2026-05-11] [investigador] — Variables de entorno faltantes en Conector

**Estado**: 🔴 Activo

**Descripción**:
- El Conector (Meta Ads) no puede funcionar sin las variables de entorno configuradas
- Faltan: `META_ACCESS_TOKEN` y `META_AD_ACCOUNT_ID`

**Impacto**:
- No se pueden crear campañas de Meta Ads
- No se pueden generar reportes
- MCP server no puede autenticar

**Dependencias**:
- Necesita acceso a Meta for Developers
- Necesita token de sistema con permisos: ads_management, ads_read, business_management

**Próximos pasos**:
1. Obtener credenciales de Meta for Developers (App ID: 1650307639342860)
2. Completar `.env` en Conector
3. Probar conexión con `meta ads campaign list`

**Responsable**: Orquestador (obtener credenciales)

---

## Unknowns (Preguntas sin respuesta)

### ¿Cómo manejar datos sensibles en memoria compartida?
- **Contexto**: MemoryPalace usa archivos markdown para memoria compartida
- **Riesgo**: No se deben exponer API keys, tokens o datos de clientes
- **Posibles soluciones**:
  1. Nunca escribir datos sensibles en `memory/`
  2. Usar `.env` para secretos
  3. Encriptar archivos sensibles (complejidad alta)

### ¿Qué métricas de éxito usar para el ecosistema?
- **Contexto**: Necesitamos medir si el ecosistema funciona
- **Posibles métricas**:
  1. Tiempo de respuesta de PeritoDigital
  2. Tasa de conversión de Conector
  3. Número de bloqueos resueltos
  4. Actualización de memoria (entradas en INDEX.md)

### ¿Cuánto cuesta Railway en producción con PostgreSQL?
- **Contexto**: PeritoDigital necesita PostgreSQL para evitar problemas de SQLite
- **Necesidad**: Presupuesto para producción
- **Investigar**: Precios de Railway para PostgreSQL + instancias Python

---

## Dependencias Externas

| Dependencia | Estado | Impacto | Responsable |
|-------------|--------|---------|-------------|
| Meta WhatsApp API | 🔴 Bloqueada | PeritoDigital no funciona | Orquestador |
| Meta Ads API | 🟡 Pendiente credenciales | Conector no funciona | Orquestador |
| Railway PostgreSQL | 🟢 Disponible | PeritoDigital estable | Coder |
| Claude API | 🟢 Funcionando | Todos los agentes | - |

---

## Historial de Bloqueos Resueltos

### [2026-05-11] [coder] — Estructura de MemoryPalace incompleta

**Estado**: ✅ Resuelto

**Descripción**: MemoryPalace tenía archivos vacíos y faltaban roles.

**Solución**:
1. Creados context.md, decisions.md, research.md
2. Configurados 4 roles en `.claude/agents/`
3. Actualizado INDEX.md con estado

**Lecciones aprendidas**:
- La disciplina del cuaderno es más importante que la herramienta
- Los roles deben estar documentados antes de empezar a trabajar