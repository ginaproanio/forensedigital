# RedesSociales — Agente de Contenido y Gestión de Redes

> IA que genera contenido, publica y gestiona redes sociales para SORSABSA — 100% automático.

---

## 🎯 Función

Esta herramienta se encarga de:
- **Generar contenido** para redes sociales (posts, stories, reels)
- **Publicar automáticamente** en redes (orgánico, no pagado)
- **Gestionar comunidad** (responder comentarios, mensajes)
- **Crear contenido educativo** sobre peritaje informático

---

## 🔄 Diferencias con Conector

| Herramienta | Función | Tipo |
|-------------|---------|------|
| **Conector** | Meta Ads + WhatsApp Oficial | Gateway Aprobado |
| **RedesSociales** | Contenido orgánico + gestión | Redes sociales naturales |

---

## 📁 Estructura del Proyecto

```
RedesSociales/
├── README.md              # Este archivo
├── CLAUDE.md              # Instrucciones para Claude
├── .gitignore             # Archivos ignorados
├── config/
│   ├── business.yaml      # Configuración del negocio
│   ├── platforms.yaml     # Configuración de redes
│   └── voice.yaml         # Voz y tono de la marca
├── content/
│   ├── templates/         # Plantillas de contenido
│   ├── scheduled/         # Contenido programado
│   └── published/         # Historial de publicaciones
├── agents/
│   ├── creator.md         # Agente creador de contenido
│   ├── scheduler.md       # Agente programador
│   └── community.md       # Agente de comunidad
├── prompts/
│   ├── prompt-crear-post.md
│   ├── prompt-plan-semanal.md
│   └── prompt-responder-comentarios.md
└── scripts/
    ├── publicar.py        # Script de publicación
    └── monitorear.py      # Script de monitoreo
```

---

## 🛠️ Stack Técnico

| Componente | Tecnología | Notas |
|-----------|-----------|-------|
| IA | Claude (suscripción actual) | Sin API key separada |
| Skills | 40 Skills de tododeia | Redacción de contenido |
| Estrategia | Andromeda (tododeia) | 8 reglas para contenido |
| Auditoría | Claude Ads (tododeia) | Revisión de calidad |
| Coordinación | MemoryPalace | Conocimiento centralizado |

---

## 🚀 Flujo de Trabajo

### 1. Planificación Semanal
```
MemoryPalace (knowledge/) → RedesSociales → Plan de contenido semanal
```

### 2. Creación de Contenido
```
Plan semanal → Agente Creator → Posts listos (texto + indicaciones visuales)
```

### 3. Programación
```
Posts listos → Agente Scheduler → Programar en redes
```

### 4. Publicación Automática
```
Contenido programado → Scripts → Publicar en redes
```

### 5. Gestión de Comunidad
```
Comentarios/mensajes → Agente Community → Respuestas automáticas
```

---

## 📋 Configuración Requerida

### 1. Variables de Entorno (.env)
```bash
# MemoryPalace (conocimiento centralizado)
MEMORY_PALACE_PATH=./knowledge/ # Mapeado vía Docker a /app/knowledge

# Redes sociales (credenciales)
FACEBOOK_PAGE_ID=tu_page_id
INSTAGRAM_ACCOUNT_ID=tu_account_id
LINKEDIN_COMPANY_ID=tu_company_id
TWITTER_ACCOUNT_ID=tu_account_id

# Horarios de publicación
PUBLISH_SCHEDULE=09:00,13:00,18:00
```

### 2. Configuración de Voice (config/voice.yaml)
```yaml
voice:
  tono: profesional-cercano
  estilo: educativo-informativo
  lenguaje: español-latam
  especialidad: peritaje-informatico
```

---

## 🎯 Casos de Uso

### 1. Post Educativo sobre Peritaje
```
Tema: "¿Cuándo necesitas un perito informático?"
→ Agente Creator genera post
→ Incluye: texto, hashtags, indicaciones visuales
→ Agente Scheduler programa publicación
```

### 2. Responder Pregunta en Comentarios
```
Comentario: "¿Qué es una imagen forense?"
→ Agente Community detecta pregunta
→ Consulta MemoryPalace para respuesta técnica
→ Genera respuesta clara y profesional
```

### 3. Plan Semanal de Contenido
```
Lunes: Post educativo (peritaje)
Martes: Caso de éxito (anonimizado)
Miércoles: Pregunta interactiva
Jueves: Consejo de ciberseguridad
Viernes: Resumen semanal + CTA
```

---

## 🔗 Integración con MemoryPalace

### Conocimiento que usa:
- `knowledge/sorsabsa.txt` — Información del negocio
- `knowledge/informes/` — Informes periciales (como referencia)
- `knowledge/faq/` — Preguntas frecuentes
- `knowledge/contenido/` — Contenido aprobado anteriormente

### Lo que registra:
- `research.md` — Interacciones con comunidad
- `decisions.md` — Decisiones de contenido
- `code-notes.md` — Patrones de contenido exitoso

---

## 📊 Métricas de Éxito

| Métrica | Objetivo | Cómo se mide |
|---------|----------|--------------|
| Posts por semana | 5-7 | Conteo de publicaciones |
| Engagement rate | >3% | Likes + comentarios / alcance |
| Respuestas automáticas | >80% | % de comentarios respondidos |
| Tiempo ahorrado | >10h/semana | Horas no dedicadas a redes |

---

## 🚨 Reglas de Seguridad

1. **NUNCA** publicar sin revisión de MemoryPalace
2. **NUNCA** revelar información confidencial de clientes
3. **SIEMPRE** mantener tono profesional
4. **SIEMPRE** citar fuentes técnicas
5. **NUNCA** dar consejos legales (solo técnicos)

---

## 🔧 Comandos Útiles

```bash
# Planear contenido semanal
claude "Genera plan de contenido para esta semana"

# Crear post específico
claude "Crea post sobre transcripción de audios"

# Responder comentarios
claude "Responde comentarios de la última publicación"

# Auditar calidad
claude "Audita el contenido de esta semana con Claude Ads"
```

---

## 📞 Próximos Pasos

1. **Configurar .env** con credenciales de redes
2. **Instalar skills de tododeia**:
   - 40 Skills (redacción)
   - Claude Ads (auditoría)
   - Andromeda (estrategia)
3. **Crear primeros templates** de contenido
4. **Probar flujo completo** con post de prueba

---

> **Estado**: En desarrollo  
> **Última actualización**: 2026-05-11  
> **Próxima revisión**: Después de configuración inicial