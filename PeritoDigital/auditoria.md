# Auditoría Técnica y Plan de Mejora — Perito Digital SORSABSA

Este documento detalla el estado actual del proyecto "Perito Digital", los fallos detectados en su despliegue en Railway y la hoja de ruta para su optimización.

## 1. Diagnóstico de Problemas Detectados

### 1.1 El "Efecto Espejismo" en Agendamientos
*   **Problema:** El agente acepta citas en la conversación pero no las agenda realmente.
*   **Causa:** Actualmente el `brain.py` utiliza un modelo de lenguaje que simula la confirmación por cortesía, pero carece de **Function Calling** (herramientas). No existe una conexión real entre el texto generado y una acción programática (API de Calendario o Base de Datos).
*   **Necesidad:** Implementar "Tools" en el modelo para que detecte la intención de agendar y ejecute una función de guardado.

### 1.2 Intermitencia en las Respuestas (Railway)
*   **Problema:** El bot responde de forma aleatoria o deja de responder.
*   **Causas Técnicas:**
    *   **Timeouts de Webhook:** Los proveedores de WhatsApp (como Whapi) requieren respuesta en <10 segundos. Si el procesamiento de la IA en Railway excede este tiempo, la conexión se corta.
    *   **Persistencia Volátil:** El uso de SQLite sin volúmenes persistentes en Railway provoca que la base de datos se reinicie o se bloquee, perdiendo el hilo de la conversación (`historial`).
    *   **Recursos:** Posibles reinicios del contenedor por exceder el límite de memoria RAM en el plan actual de Railway.

### 1.3 Diferenciación de Interlocutor (Empresa vs. Persona)
*   **Problema:** El bot no ajusta su protocolo según el perfil del cliente.
*   **Causa:** El `SYSTEM_PROMPT` es estático y muy general.
*   **Necesidad:** Reestructurar el prompt para incluir una fase de "Calificación de Lead" que identifique si es un abogado/empresa (B2B) o una persona natural (B2C) antes de proceder con el peritaje.

## 2. Estado de Infraestructura y Docker
*   **Situación:** El proyecto es un clon de AgentKit y mantiene su propio `Dockerfile` y `docker-compose.yml`.
*   **Estrategia:** Se mantiene la independencia del Docker de Sorsabsa por ahora para facilitar las pruebas rápidas de lógica.
*   **Riesgo:** La configuración actual de Railway no es óptima para producción si no se migra a una base de datos externa (PostgreSQL).

## 3. Hoja de Ruta Sugerida

### Fase 1: Estabilidad (Inmediato)
1.  Configurar una base de datos **PostgreSQL** en Railway y actualizar el `DATABASE_URL` para asegurar que la memoria del bot sea persistente.
2.  Implementar logs detallados en `main.py` para medir el tiempo exacto de respuesta de la IA.

### Fase 2: Acción (Lógica de Negocio)
1.  **Añadir Tools:** Crear `agent/tools.py` para manejar el registro de citas.
2.  **Refinar Cerebro:** Modificar `agent/brain.py` para que soporte llamadas a funciones (Function Calling) de Groq/Llama.

### Fase 3: Especialización Forense
1.  Actualizar el Prompt para solicitar datos obligatorios de cadena de custodia según el tipo de cliente.
2.  Incorporar archivos técnicos en la carpeta `/knowledge` sobre legislaciones locales para evitar alucinaciones legales.

---
**Documento generado para:** SORSABSA - Área de Desarrollo
**Fecha:** Mayo 2024
**Estado:** Auditoría Inicial Completada
```

He diseñado esta auditoría para que sea tu guía de referencia. Lo más crítico que está "necesitando hacerse" es pasar de un bot que solo habla a un bot que ejecuta acciones (Tools) y asegurar que Railway no mate los procesos por falta de una base de datos robusta.

¿Te gustaría que profundicemos en cómo configurar la base de datos PostgreSQL en Railway para solucionar la intermitencia?

<!--
[PROMPT_SUGGESTION]¿Cómo configuro el DATABASE_URL en Railway para usar PostgreSQL con este proyecto?[/PROMPT_SUGGESTION]
[PROMPT_SUGGESTION]Ayúdame a crear la función de agendamiento en agent/tools.py para que el perito deje de alucinar citas.[/PROMPT_SUGGESTION]
