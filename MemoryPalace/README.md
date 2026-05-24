# Memory Palace — Cerebro del Ecosistema SORSABSA

Plantilla para crear equipos de agentes con Claude usando un cuaderno compartido (`memory/`) y roles definidos en `.claude/agents/`.

## 🎯 Propósito

Memory Palace es el **cerebro central** que coordina todos los agentes y sistemas del ecosistema SORSABSA:

- **PeritoDigital**: Agente de WhatsApp para peritajes informáticos
- **Conector**: Integración con Meta Ads para campañas publicitarias
- **Sistemas futuros**: Cualquier nuevo agente o herramienta

## 📁 Estructura del Proyecto

```
MemoryPalace/
├── CLAUDE.md                    # Protocolo del cuaderno compartido
├── README.md                    # Este archivo
├── memory/                      # Cuaderno compartido
│   ├── INDEX.md                # Mapa del cuaderno + estado
│   ├── context.md              # Misión, alcance, stakeholders
│   ├── decisions.md            # ADRs (Architecture Decision Records)
│   ├── research.md             # Hallazgos de investigación
│   ├── code-notes.md           # Patrones y gotchas de código
│   ├── reviews.md              # Hallazgos de revisión (vacío inicialmente)
│   ├── blockers.md             # Bloqueos activos y unknowns
│   └── glossary.md             # Glosario de terminología
└── .claude/agents/             # Roles definidos
    ├── investigador.md          # Rol: Investigador
    ├── coder.md                # Rol: Coder
    ├── revisor.md              # Rol: Revisor
    └── orquestador.md          # Rol: Orquestador
```

## 🏗️ Arquitectura del Ecosistema

```
┌─────────────────┐
│  Memory Palace  │ ← CEREBRO (este proyecto)
│   (Coordinador) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼────┐ ┌─▼────────┐
│Perito  │ │ Conector │
│Digital │ │ Meta Ads │
└────────┘ └──────────┘
```

## 👥 Roles del Equipo

| Rol | Permisos de Escritura | Responsabilidades |
|-----|----------------------|-------------------|
| **Investigador** | `memory/research.md` | Analizar proyectos, investigar mejores prácticas |
| **Coder** | `memory/code-notes.md` | Implementar soluciones, documentar patrones |
| **Revisor** | `memory/reviews.md` | Revisar código, identificar problemas |
| **Orquestador** | `memory/decisions.md`, `memory/INDEX.md`, `memory/context.md` | Coordinar agentes, tomar decisiones estratégicas |

## 📋 Protocolo (6 Reglas Obligatórias)

1. **Antes de trabajar**: Lee `INDEX.md` + archivos relevantes a tu rol
2. **Al terminar**: Añade entrada con formato `### [YYYY-MM-DD] [agente] — título`
3. **Nunca borres** lo que otro escribió. Marca obsoleto con `~~texto~~`
4. **Si contradices** una decisión, NO la sobrescribas: escribe en `decisions.md` con prefijo "CONFLICTO:"
5. **Mantén `INDEX.md` actualizado**: una línea por entrada nueva
6. **Si no tienes permiso** de escritura sobre un archivo, pide al orquestador que lo haga por ti

## 🚀 Inicio Rápido

### Para nuevos agentes

1. **Lee el protocolo** en `CLAUDE.md`
2. **Identifica tu rol** en `.claude/agents/`
3. **Lee los archivos relevantes** según tu rol
4. **Trabaja en tu tarea**
5. **Documenta** en el archivo correspondiente
6. **Actualiza** `INDEX.md` con tu entrada

### Para el orquestador

1. Lee `memory/blockers.md` para bloqueos activos
2. Revisa `memory/research.md` para hallazgos nuevos
3. Revisa `memory/reviews.md` para problemas críticos
4. Toma decisiones y registra en `memory/decisions.md`
5. Delega tareas a los agentes correspondientes
6. Actualiza `memory/INDEX.md`

## 📊 Estado Actual

| Componente | Estado | Descripción |
|------------|--------|-------------|
| **Core 4** | ✅ Completo | context.md, decisions.md, research.md, INDEX.md |
| **Extended** | ✅ Completo | code-notes.md, reviews.md, blockers.md, glossary.md |
| **Roles** | ✅ Completo | investigador, coder, revisor, orquestador |
| **Integración** | 🟡 Pendiente | Conectar con PeritoDigital y Conector |

## 🔗 Proyectos Relacionados

- **PeritoDigital**: `../PeritoDigital/` — Agente de WhatsApp con AgentKit
- **Conector**: `../Conector/` — Integración Meta Ads con MCP server
- **SORSABSA**: `../PeritoDigital/knowledge/sorsabsa.txt` — Knowledge base

## 🛠️ Tecnologías

- **Claude Code**: Motor de IA para todos los agentes
- **MCP Servers**: Conectores especializados (Meta Ads, etc.)
- **Git**: Control de versiones para memoria compartida
- **Railway**: Deploy de agentes Python en producción

## 📖 Documentación

- **[CLAUDE.md](CLAUDE.md)** — Protocolo completo del cuaderno compartido
- **[memory/context.md](memory/context.md)** — Misión y alcance del ecosistema
- **[memory/decisions.md](memory/decisions.md)** — Decisiones arquitectónicas (ADRs)
- **[memory/research.md](memory/research.md)** — Hallazgos de investigación
- **[memory/blockers.md](memory/blockers.md)** — Bloqueos activos y unknowns
- **[memory/glossary.md](memory/glossary.md)** — Glosario de terminología

---

> *"La disciplina del cuaderno es más importante que la herramienta."*