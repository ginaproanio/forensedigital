# Glosario — Memory Palace SORSABSA

> Terminología del proyecto, acrónimos y conceptos clave.

---

## A

### ADR (Architecture Decision Record)
Registro de una decisión arquitectónica importante, incluyendo contexto, decisión y consecuencias. Se almacena en `memory/decisions.md`.

### Agente
Instancia de Claude Code que trabaja en un proyecto específico con un rol definido (investigador, coder, revisor, orquestador).

### AgentKit
Framework para construir agentes de WhatsApp con IA. Usado en PeritoDigital.

## B

### Bloqueo (WhatsApp)
Situación donde Meta bloquea un número de WhatsApp Business por comportamiento sospechoso (spam, reintentos, etc.).

### Brain (Cerebro)
Componente del agente que conecta con Claude API y genera respuestas inteligentes.

## C

### Coder
Rol responsable de implementar soluciones técnicas. Escribe en `memory/code-notes.md`.

### Conector
Proyecto que integra Meta Ads con Claude vía MCP server. App ID: `1650307639342860`.

### Cuaderno Compartido
Patrón de memoria compartida donde todos los agentes leen/escriben en archivos markdown en `memory/`.

## D

### Deduplicación
Técnica para evitar procesar el mismo mensaje de WhatsApp múltiples veces (usando msg.id).

## E

### Ecosistema SORSABSA
Conjunto de proyectos coordinados: MemoryPalace (cerebro), PeritoDigital (WhatsApp), Conector (Meta Ads).

### Effect Espejismo
Problema donde el agente acepta citas en la conversación pero no las agenda realmente (falta function calling).

## F

### Function Calling
Capacidad de la IA para detectar intenciones y ejecutar funciones específicas (ej: agendar cita, buscar información).

## I

### Investigador
Rol responsable de analizar y documentar hallazgos. Escribe en `memory/research.md`.

## K

### Knowledge Base
Base de conocimiento del negocio. En PeritoDigital: `knowledge/sorsabsa.txt`.

## M

### MCP (Model Context Protocol)
Protocolo para extender Claude con servidores especializados (ej: Meta Ads, FileSystem, PostgreSQL).

### Memory Palace
Cerebro central del ecosistema. Coordina agentes y mantiene memoria compartida en `memory/`.

### Memory.py
Componente que gestiona el historial de conversaciones (SQLite local / PostgreSQL producción).

## O

### Orquestador
Rol principal que coordina todos los agentes, toma decisiones estratégicas y mantiene INDEX.md.

## P

### PeritoDigital
Agente de WhatsApp para SORSABSA (peritaje informático forense). Construido con AgentKit.

### Provider (Proveedor)
Capa de abstracción para conectar con diferentes servicios de WhatsApp (Meta Cloud API, Twilio, Whapi).

## R

### Railway
Plataforma de deploy usada para PeritoDigital y futuros agentes Python.

### Revisor
Rol responsable de revisar código, identificar problemas y proponer fixes. Escribe en `memory/reviews.md`.

## S

### SORSABSA
Empresa de peritaje informático forense y ciberseguridad. Cliente principal del ecosistema.

### System Prompt
Instrucciones que definen la personalidad y comportamiento del agente. Almacenado en `config/prompts.yaml`.

## T

### Timeout
Tiempo máximo de espera para una operación (ej: webhook de WhatsApp debe responder en <10s).

### Tools (Herramientas)
Funciones específicas del negocio que el agente puede ejecutar (agendar cita, buscar en knowledge, etc.).

## W

### Webhook
Endpoint que recibe mensajes de WhatsApp desde el proveedor (Meta/Twilio/Whapi).

### Whapi
Proveedor de WhatsApp usado actualmente por PeritoDigital (legítimo, no scraper).

---

## Acrónimos

| Acrónimo | Significado | Uso |
|----------|-------------|-----|
| ADR | Architecture Decision Record | decisions.md |
| API | Application Programming Interface | General |
| B2B | Business to Business | Tipo de cliente |
| B2C | Business to Consumer | Tipo de cliente |
| CLI | Command Line Interface | Terminal |
| DB | Database | Base de datos |
| MCP | Model Context Protocol | Extensión de Claude |
| OK | Okay (confirmación) | Webhook response |
| SQL | Structured Query Language | Base de datos |
| URL | Uniform Resource Locator | Web |

## Conceptos Técnicos

### Rate Limiting
Control de frecuencia de mensajes para evitar comportamiento de spam.

### Circuit Breaker
Patrón para evitar reintentos infinitos cuando un servicio falla repetidamente.

### Backoff Exponencial
Estrategia de reintentos donde el tiempo de espera aumenta exponencialmente.

### Async/Await
Patrón de programación asíncrona usado en FastAPI y el agente.

### SQLite vs PostgreSQL
- **SQLite**: Base de datos local, volátil en Railway, buena para desarrollo
- **PostgreSQL**: Base de datos en producción, persistente, soporta concurrencia

## Referencias

- [CLAUDE.md](../CLAUDE.md) — Protocolo completo de Memory Palace
- [context.md](context.md) — Misión y alcance del ecosistema
- [decisions.md](decisions.md) — Decisiones arquitectónicas