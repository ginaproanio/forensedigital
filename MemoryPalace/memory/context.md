# Contexto — Memory Palace SORSABSA

## Misión
Memory Palace es el **cerebro central** que coordina todos los agentes y sistemas del ecosistema SORSABSA. Actúa como memoria compartida, orquestador de decisiones y garante de la coherencia entre los diferentes componentes.

## Alcance
- **PeritoDigital**: Agente de WhatsApp para peritajes informáticos
- **Conector**: Integración con Meta Ads para campañas publicitarias
- **Sistemas futuros**: Cualquier nuevo agente o herramienta que se integre al ecosistema

## Stakeholders
1. **Perito Informático** (rol principal)
   - Necesita: Gestión eficiente de casos, automatización de respuestas, integración con WhatsApp
   - Usa: PeritoDigital para atención al cliente

2. **Media Buyer / Marketing**
   - Necesita: Campañas automatizadas, reportes, auditoría de pixel
   - Usa: Conector para Meta Ads

3. **Desarrollador / Orquestador**
   - Necesita: Visión unificada, control de versiones, coordinación entre agentes
   - Usa: Memory Palace como centro de comando

## Arquitectura del Ecosistema

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

## Principios de Diseño
1. **Memoria persistente**: Todo queda registrado en `memory/`
2. **Roles definidos**: Cada agente sabe qué puede leer/escribir
3. **Protocolo estricto**: 6 reglas obligatorias de escritura
4. **Trazabilidad**: Cada decisión tiene autor, fecha y contexto

## Tecnologías Clave
- **Claude Code**: Motor de IA para todos los agentes
- **MCP Servers**: Conectores especializados (Meta Ads, etc.)
- **Git**: Control de versiones para memoria compartida
- **Railway**: Deploy de agentes en producción

## Relación con Otros Proyectos
- **PeritoDigital**: Usa `knowledge/sorsabsa.txt` como base de conocimiento
- **Conector**: Usa MCP server de Meta Ads para campañas
- **MemoryPalace**: Coordina ambos y mantiene la memoria histórica

## Próximos Pasos
1. Completar archivos Core 4 (decisions.md, research.md)
2. Configurar roles en `.claude/agents/`
3. Establecer flujo de trabajo entre agentes
4. Integrar con sistemas existentes