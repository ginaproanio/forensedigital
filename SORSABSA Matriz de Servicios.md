# SORSABSA Matriz de Servicios

## 🎯 Enfoque de Lanzamiento (Fase 1: Línea Pericial)

Sorsabsa divide sus capacidades en dos líneas de negocio. Por decisión estratégica, el lanzamiento inicial se enfoca exclusivamente en la **Línea de Peritaje Informático Forense**.

| Línea de Negocio | Estado | Descripción | Componentes Requeridos |
| :--- | :--- | :--- | :--- |
| **Informatica Forense** | 🚀 **Prioridad 1** | Servicios periciales, ciberseguridad y mediación. Requiere atención automatizada 24/7. | PeritoDigital, RedesSociales, Memory Palace, Conector, Mensajería. |
| **Fábrica de Software** | ⏳ **Fase 2** | Productos verticales para diversas industrias (Inmobiliaria, Salud, Educación). | CondoManager, VetSys, Academy, Marketplace. |

---

## Matriz Técnica de Componentes

| Servicio | Categoría | Propósito | Consumidores | Dependencias clave | Interfaz principal | Estado Docker | Prioridad |
|---|---|---|---|---|---|---|---|
| Identity | CORE transaccional | Autenticación global y multi-tenancy | Todo el ecosistema | Base de datos de identidad | API | ✅ Esquema v2.0 Reconstruido | Alta |
| Accounting | Vertical | Libro mayor y asientos contables (SaaS) | CondoManager, Vetsys, clientes directos | Billing, pagos, DB contable | API / Web | ✅ Esquema v2.0 Reconstruido | Alta |
| Billing | Vertical | Deudas y cobranza (SaaS) | Verticales, marketplace, clientes directos | Ledger, pagos, tenants | API / Web | ✅ Esquema v2.0 Reconstruido | Alta |
| Payments | CORE transaccional | Integración técnica con Pasarelas | Billing, marketplace, verticales | Payphone API | API / webhooks | ✅ Esquema v2.0 Reconstruido | Alta |
| Marketplace | CORE transaccional | Suscripciones y módulos | Verticales y clientes | Identity, billing, payments | API | ✅ Declarado | Media |
| Firmar | Plataforma transversal | Firma electrónica legal y recolección formal de firmas | CondoManager y verticales futuros | Identity, documentos, evidencia legal | API / firma | ✅ Declarado | Alta |
| Convertidor | Plataforma transversal | Conversión PDF → TXT / MD / CSV | LexScraper, peritajes, biblioteca legal | Python, parsing documental | API / proceso | ✅ Operativo | Alta |
| Conector | Plataforma transversal | Hub MCP, notificaciones e integraciones externas | Todo el ecosistema y agentes | Meta Ads, Gmail, WhatsApp, colas | MCP / API / workers | ✅ Operativo | Alta |
| Memory Palace | Plataforma transversal | Memoria operativa y coordinación de agentes | Agentes y equipos técnicos | Cuaderno compartido, protocolos, contexto | Agentes / memoria | ✅ Declarado | Alta |
| LexScraper | Plataforma transversal | Vigilancia normativa y alimentación de biblioteca legal | LegalConnect | Playwright, Convertidor, colas, DB legal | Worker / scraping | ✅ Esquema v2.0 Materializado | Alta |
| Scrapling | Plataforma transversal | Prospección de audiencias y datos públicos | Conector, marketing, growth | Fuentes públicas, limpieza de datos | Worker / ingestión | ✅ Sincronizado (Etapa 2.5) | Media |
| RRHH | Plataforma transversal | Ingesta estructurada de perfiles | Conocimiento interno, reclutamiento | Base de conocimiento, perfiles | API / ingestión | ✅ Declarado | Media |
| CondoManager SaaS | Vertical Inmobiliario | Gestión operativa de condominios e inmuebles | Administraciones de edificios y residentes | Identity, billing, firmar, accounting | Web app / API | 🏗️ Desbloqueado (Fase Refactor) | Alta |
| Academy | Vertical | Gestión educativa y aula virtual | Comunidades educativas | Identity, billing, marketplace | Web app / API | ✅ Declarado | Media |
| LegalConnect | Vertical | Plataforma jurídica y biblioteca legal | Abogados y entorno legal | LexScraper, Convertidor, Conector, Identity | Web app / API | ✅ Declarado | Alta |
| AgenteInmobiliario / Ecoinmobiliaria | Vertical | Gestión y marketplace inmobiliario | Sector inmobiliario | Identity, billing, marketplace | Web app / API | ✅ Declarado | Media |
| Vetsys | Vertical | Gestión para clínicas veterinarias | Clínicas veterinarias | Identity, billing, accounting | Web app / API | ✅ Declarado | Media |
| PeritoDigital | Agente inteligente | Atención inicial de peritajes por WhatsApp y agenda | Clientes y abogados | WhatsApp, Google Calendar, Memory Palace, Conector | Agente / mensajería | ✅ Operativo (Etapa 2 OK) | Alta |
| Memory Palace Agents | Agente inteligente | Investigación, codificación, revisión y orquestación | Equipos internos | Memory Palace, Conector, contexto del ecosistema | Agentes | ✅ Declarado | Media |
| peritajes-forenses | Especialidad Forense | Gestión de pericias (Informática, Ocular, Accidentología) | Peritos acreditados y sistema judicial | Evidencia, normativa 216-2024, convertidor | App / procesos forenses | ✅ Sincronizado | Alta |
| recuperacion | Especialidad forense | Recuperación de datos y trabajo con discos raw | Equipo técnico forense | Acceso de bajo nivel, discos, tooling especializado | Herramienta técnica | ✅ Declarado | Media |

## Vacíos detectados

 🚩 **Velo Negro Activo**: `condomanager-saas`, `agenteinmobiliario` y `Vetsys` requieren auditoría de esquemas.
 ✅ **Infraestructura v2.0**: 100% materializada y validada vía `health_check.py` (Puerto 6543).
 ✅ Estandarización Docker completada vía .docker_global

## Auditoría de Carpetas (vs Realidad Física)
| Carpeta | Estado Auditoría | Riesgo Velo Negro |
|---|---|---|
| `mensajeria` | ✅ Auditado | Ninguno (Sincronizado v2.0) |
| `RedesSociales` | ✅ Operativo | Ninguno (Consolidado en Docker) |
| `Recuperacion` | Pendiente | Bajo (Herramienta local) |
- **n8nMCP**: ELIMINADO FÍSICAMENTE. Toda la lógica MCP y de automatización ha sido absorbida por `Conector`.
- falta registrar propietarios técnicos por servicio
- falta definir qué servicios serán API, workers, jobs o herramientas operativas

## Siguiente uso de esta matriz

- completar dependencias reales por servicio
- añadir repositorio o carpeta fuente
- marcar estado actual: idea, prototipo, operativo, refactor, pausado
- priorizar migración por impacto y complejidad
