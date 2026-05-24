# Reviews — Hallazgos de Revisión

> Revisiones de código, bugs identificados, vulnerabilidades y fixes propuestos. Escrito por el revisor.

---

## Formato de entrada

Cada entrada debe seguir este formato:

```markdown
## [YYYY-MM-DD] [revisor] — Revisión de (proyecto/archivo)

### Hallazgos
| Severidad | Archivo | Problema | Fix propuesto |
|-----------|---------|----------|---------------|
| Alta | agent/main.py | Falta validación de input | Agregar validación con pydantic |

### Fixes aplicados
- [x] Fix 1 (commit hash o descripción)
- [ ] Fix 2 (pendiente)

### Recomendaciones
- Mejora 1
- Mejora 2
```

### Niveles de severidad
- **Crítica**: Bug que causa fallo inmediato o vulnerabilidad de seguridad
- **Alta**: Problema funcional que afecta comportamiento esperado
- **Media**: Code smell, mala práctica, falta de testing
- **Baja**: Estilo, formato, documentación

---

## Entradas

<!-- Las entradas nuevas se agregan aquí -->

---

## Plantilla de Revisión

### Seguridad
- [ ] No hay API keys hardcodeadas
- [ ] Validación de input en todos los endpoints
- [ ] Rate limiting implementado
- [ ] Sanitización de datos de usuario

### Funcionalidad
- [ ] El código hace lo que debería hacer
- [ ] Manejo de errores adecuado
- [ ] Timeouts configurados
- [ ] Reintentos con backoff

### Calidad de código
- [ ] Nombres descriptivos de variables/funciones
- [ ] Funciones cortas y con una sola responsabilidad
- [ ] Comentarios solo donde es necesario
- [ ] Sin código duplicado

### Testing
- [ ] Tests para lógica crítica
- [ ] Tests de integración para endpoints
- [ ] Tests de errores y edge cases

### Performance
- [ ] Sin queries N+1
- [ ] Conexiones a DB cerradas correctamente
- [ ] Sin bloqueos en event loop (async)

---

## Notas

- Este archivo está vacío inicialmente. El revisor agregará entradas cuando realice revisiones de código.
- Para revisiones programadas, el orquestador debe solicitar revisión explícitamente.
- Los problemas críticos o altos deben notificarse inmediatamente al orquestador.