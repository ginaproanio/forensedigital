# SORSABSA Arquitectura del Ecosistema

## Contexto

**SORSABSA** es una firma ecuatoriana con más de 15 años de trayectoria en **Peritaje Informático Forense** y **Ciberseguridad**. A partir de esa práctica especializada, ha evolucionado hacia una **fábrica de software legal-tech**, construyendo un ecosistema de productos, servicios transversales, agentes inteligentes y herramientas técnicas.

El reto actual no es crear más proyectos, sino **ordenar el ecosistema** para que pueda crecer sin depender de instalaciones manuales, configuraciones dispersas ni decisiones improvisadas.

## Problema actual

El crecimiento progresivo de los proyectos ha generado:

- dependencias instaladas en múltiples carpetas
- entornos inconsistentes entre proyectos
- duplicación de capacidades
- acoplamiento operativo innecesario
- dificultad para desplegar y mantener servicios
- falta de una clasificación arquitectónica estable

La meta no es solo “usar Docker”, sino establecer una arquitectura de **servicios desacoplados**, ejecutables de forma estándar, reproducible y portable.

## Líneas de Negocio y Operación

El ecosistema está diseñado para servir a dos propósitos de negocio complementarios, con una prioridad de ejecución definida:

1.  **Operación Pericial (Prioridad Alta):** Soporte tecnológico al Perito Forense. Automatización del embudo de atención, gestión de citas y base de conocimiento técnico/legal.
    *   *Agentes & Hubs:* PeritoDigital, RedesSociales, Conector, Memory Palace, Mensajería.
2.  **Fábrica de Productos SaaS:** Creación y mantenimiento de soluciones verticales por industria.
    *   *Verticales:* CondoManager, VetSys, Academy, etc.


## Visión objetivo

La arquitectura objetivo de SORSABSA se organiza en estas capas:

- **CORE transaccional**
- **servicios transversales de plataforma**
- **productos verticales**
- **agentes inteligentes**
- **herramientas de especialidad forense**

Cada componente debe evolucionar hacia un modelo con:

- responsabilidad clara
- dependencias explícitas
- configuración externa
- contenedor propio o rol definido en el orquestador
- contratos de integración claros

## Principios de arquitectura

- **desacoplamiento por dominio**
- **contenedorización como estándar**
- **reutilización de capacidades compartidas**
- **configuración externa y portable**
- **integración por contratos**
- **trazabilidad y auditoría**
- **orquestación progresiva**
- **mínima duplicación técnica**

## Mapa del ecosistema

### CORE transaccional

- **Identity** · autenticación global, usuarios, perfiles y tenants
- **Payments** · motor de integración con pasarelas de pago (estandarizado en PayPhone para el mercado local, extensible a Stripe/PayPal)
- **Marketplace** · suscripciones y comercialización de módulos

### Servicios transversales de plataforma

- **Firmar** · servicio transversal de firma electrónica legal y recolección formal de firmas; nació sirviendo a CondoManager, pero debe consolidarse como capacidad compartida
- **Convertidor** · servicio documental para transformar PDF a TXT, Markdown o CSV
- **Conector** · hub de integración del ecosistema con servidores MCP, notificaciones y conectores a Meta Ads, Gmail y WhatsApp
- **Memory Palace** · memoria operativa y coordinación de agentes, con registro de decisiones, investigación, bloqueos y contexto técnico
- **LexScraper** · vigilancia normativa automatizada; captura legislación oficial, procesa PDFs y alimenta la biblioteca legal de LegalConnect
- **Scrapling** · prospección y recolección de audiencias y datos públicos; en este contexto, orientado a abogados y automatización comercial
- **RRHH** · ingesta estructurada de perfiles para alimentar conocimiento organizacional y procesos internos

### Productos verticales

- **Accounting / Ledger** · Sistema contable y libro mayor (SaaS independiente y motor contable del ecosistema)
- **Billing / Recaudación** · Motor de facturación y cobranza (SaaS independiente y gestor de deudas del ecosistema)
- **CondoManager SaaS** · gestión operativa de condominios e inmuebles
- **Academy** · plataforma educativa
- **LegalConnect** · plataforma jurídica, reforzada por una biblioteca legal automatizada
- **AgenteInmobiliario / Ecoinmobiliaria** · vertical inmobiliario y marketplace público
- **Vetsys** · software para clínicas veterinarias

### Agentes inteligentes

- **PeritoDigital** · agente por WhatsApp para atención de casos, agendamiento y captura inicial de información
- **Memory Palace Agents** · Investigador, Coder, Revisor y Orquestador
- **futuros agentes por dominio** · automatización especializada por vertical o función

### Herramientas de especialidad forense

- **peritajes-forenses** · gestión central de pericias digitales
- **recuperacion** · trabajo con discos raw y recuperación de datos de bajo nivel

## Relaciones clave

Ya existen flujos concretos entre componentes:

- **LexScraper** detecta normativa oficial en PDF
- **Convertidor** transforma esos documentos a formatos procesables
- el contenido procesado se inserta en la biblioteca legal de **LegalConnect**
- **Conector** puede notificar novedades o ejecutar acciones en servicios externos
- **Scrapling** puede apoyar la formación de audiencias y procesos de captación
- **Memory Palace** conserva contexto, decisiones y conocimiento técnico del ecosistema

La meta no es tener contenedores aislados, sino una **red de servicios interoperables**.

## Rol de Docker

Docker debe funcionar como estándar operativo del ecosistema.

Objetivos:

- eliminar instalaciones manuales por proyecto
- evitar conflictos de versiones y dependencias
- unificar desarrollo, pruebas y despliegue
- facilitar onboarding técnico
- preparar el ecosistema para orquestación futura

Cada servicio debería tender a tener:

- `Dockerfile`
- variables de entorno definidas
- healthcheck
- puertos y dependencias explícitas
- integración con una red común
- logs claros y auditables

## Patrón operativo recomendado

- **un servicio = una responsabilidad**
- **un contenedor = una unidad de ejecución**
- **dependencias dentro del contenedor**
- **comunicación entre servicios por API, colas o eventos**
- **docker-compose para desarrollo local**
- **configuración por entorno**
- **scripts homogéneos de build, run y test**

## Hallazgos de madurez actual

Ya existen avances importantes que deben consolidarse, no reiniciarse:

- **Conector** ya opera como hub de integración y notificaciones
- **LexScraper** ya cuenta con scraping funcional, cola, auditoría e integración con Convertidor
- **Convertidor** ya sirve como servicio documental reusable
- **Memory Palace** ya dispone de protocolo operativo, roles y estructura de gobernanza técnica
- parte del ecosistema ya fue pensada para un **Docker global**

## Riesgos a evitar

- seguir creando proyectos sin taxonomía estable
- mezclar servicios transversales con verticales
- crecer por intuición en lugar de dominio
- depender de scripts locales no estandarizados
- no documentar contratos entre componentes

## Próximos pasos

1. clasificar formalmente todos los proyectos por tipo
2. identificar cuáles ya están dockerizados y cuáles no
3. definir contratos entre servicios
4. estandarizar naming, variables de entorno y estructura de contenedores
5. consolidar un `docker-compose` maestro de desarrollo
6. separar servicios realmente transversales de los verticales
7. documentar dependencias, bases de datos y flujos de datos
8. definir roadmap de migración por fases

## Resumen ejecutivo

SORSABSA está construyendo un ecosistema tecnológico compuesto por motores core, servicios transversales, productos verticales, agentes inteligentes y herramientas forenses especializadas.

La prioridad arquitectónica no es únicamente contenerizar, sino **ordenar el ecosistema bajo una lógica de dominios, servicios reutilizables y despliegue estandarizado con Docker**, para reducir fragilidad operativa y permitir crecimiento sostenible.
