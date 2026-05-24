# Decisiones de Arquitectura (ADRs)

> Registro cronológico de decisiones técnicas. Cada entrada incluye: fecha, autor, contexto, decisión y consecuencias.

---

## [2026-05-11] [orquestador] — Arquitectura del ecosistema SORSABSA

### Contexto
Necesitamos coordinar múltiples agentes (PeritoDigital, Conector) bajo un mismo techo. Cada uno tiene su propio CLAUDE.md y flujos de trabajo, pero carecemos de un punto de coordinación central.

### Decisión
Crear **MemoryPalace** como cerebro central con:
1. **Protocolo de cuaderno compartido** en `memory/`
2. **Roles definidos** (investigador, coder, revisor, orquestador)
3. **Reglas estrictas** de lectura/escritura
4. **Trazabilidad completa** de decisiones

### Consecuencias
- ✅ Cada agente sabe exactamente dónde leer/escribir
- ✅ Las decisiones quedan documentadas y son reversibles
- ⚠️ Requiere disciplina para mantener el protocolo
- ✅ Permite escalar a más agentes sin caos

---

## [2026-05-11] [orquestador] — Stack tecnológico unificado

### Contexto
Los diferentes proyectos usan tecnologías diversas. Necesitamos estandarizar para facilitar el mantenimiento y la coordinación.

### Decisión
Adoptar stack unificado:
- **IA**: Claude API (claude-sonnet-4-6) para todos los agentes
- **Orquestación**: Claude Code + MCP servers
- **Deploy**: Railway para agentes Python, Docker para consistencia
- **Memoria**: SQLite local + PostgreSQL en producción
- **Control**: Git para versionado de memoria compartida

### Consecuencias
- ✅ Coherencia técnica entre proyectos
- ✅ Facilita rotación de desarrolladores
- ✅ Reduce curva de aprendizaje
- ⚠️ Dependencia de Anthropic Claude

---

## [2026-05-11] [orquestador] — Protocolo de comunicación entre agentes

### Contexto
PeritoDigital y Conector necesitan comunicarse indirectamente a través de MemoryPalace, pero sin acoplamiento directo.

### Decisión
Establecer protocolo de comunicación asíncrona:
1. **PeritoDigital** escribe hallazgos en `memory/research.md`
2. **Conector** lee research.md y ajusta campañas
3. **Orquestador** coordina y toma decisiones en `memory/decisions.md`
4. **Nunca** comunicación directa entre agentes

### Consecuencias
- ✅ Bajo acoplamiento entre sistemas
- ✅ Cada agente es independiente y reemplazable
- ✅ Trazabilidad completa de interacciones
- ⚠️ Latencia en comunicación (asíncrona)

---

## [2026-05-11] [orquestador] — Estructura de memoria compartida

### Contexto
Necesitamos definir qué archivos van en `memory/` y quién puede escribir en cada uno.

### Decisión
**Core 4 (obligatorios):**
- `INDEX.md` → Mapa del cuaderno (todos leen, orquestador escribe)
- `context.md` → Misión y alcance (todos leen, orquestador escribe)
- `decisions.md` → ADRs (todos leen, orquestador escribe)
- `research.md` → Hallazgos (todos leen, investigador escribe)

**Extended (opcionales):**
- `code-notes.md` → Patrones de código (coder escribe)
- `reviews.md` → Revisiones (revisor escribe)
- `blockers.md` → Bloqueos (todos escriben)
- `glossary.md` → Terminología (todos escriben)

### Consecuencias
- ✅ Claridad en permisos de escritura
- ✅ Evita conflictos de edición
- ✅ Escalable a nuevos archivos/roles
- ⚠️ Requiere disciplina para no saltarse permisos

---

## [2026-05-11] [orquestador] — Integración con PeritoDigital

### Contexto
PeritoDigital ya tiene conocimiento de SORSABSA en `knowledge/sorsabsa.txt`. MemoryPalace necesita integrar este conocimiento sin duplicarlo.

### Decisión
1. **Fuente única de verdad**: `PeritoDigital/knowledge/sorsabsa.txt`
2. **MemoryPalace** referencia este archivo, no lo copia
3. **PeritoDigital** actualiza sorsabsa.txt cuando cambia el negocio
4. **MemoryPalace** notifica a Conector sobre cambios relevantes

### Consecuencias
- ✅ Sin duplicación de conocimiento
- ✅ Actualizaciones automáticas
- ⚠️ Dependencia de ruta relativa entre proyectos
- ✅ Conocimiento siempre actualizado

---

## [2026-05-11] [orquestador] — Estrategia de deploy

### Contexto
Necesitamos deployar múltiples agentes en producción de forma coordinada.

### Decisión
1. **Railway** para todos los agentes Python (PeritoDigital, futuros)
2. **Docker** para consistencia de entornos
3. **Git** como trigger de deploy automático
4. **Variables de entorno** para configuración sensible
5. **MemoryPalace** como repo principal de coordinación

### Consecuencias
- ✅ Deploy automático y consistente
- ✅ Rollback fácil con Git
- ✅ Entornos reproducibles
- ⚠️ Costo de Railway (pero hay plan gratis)

---

## Próximas Decisiones Pendientes
- [ ] ¿Cómo manejar autenticación entre agentes?
- [ ] ¿Qué hacer con datos sensibles en memoria compartida?
- [ ] ¿Cómo versionar la memoria compartida?
- [ ] ¿Qué métricas de éxito para el ecosistema?