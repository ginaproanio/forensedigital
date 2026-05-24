# SORSABSA - Plataforma de Software Multi-Industria

## 🎯 Estrategia de Lanzamiento 2026

Sorsabsa opera mediante un modelo de dos líneas de negocio principales. **La prioridad actual es la salida a producción de la Línea Pericial.**

1.  **Línea de Peritaje Informático Forense (FOCO ACTUAL):** Orientada a la atención de clientes periciales, gestión de evidencias y agendamiento inteligente. Proyectos críticos: `PeritoDigital`, `RedesSociales`, `MemoryPalace`, `Conector`, `Mensajería`, `Scrapling`.
2.  **Línea de Desarrollo de Software (Verticales):** Desarrollo de soluciones SaaS para múltiples industrias. Proyectos: `CondoManager`, `LegalConnect`, `VetSys`, `Academy`.

---

## 📋 Auditoría de Proyectos y Estatus (Mayo 2026)

Este cuadro resume el estado actual de los módulos (v1.2.0) y su integración con la infraestructura **Docker Global**.

| Proyecto | Categoría | Estatus | Declarado en Docker | Notas |
| :--- | :--- | :--- | :---: | :--- |
| **CondoManager SAAS** | Vertical | 45% (Desarrollo) | ✅ Sí | Gestión de alícuotas y deudas funcional. |
| **Convertidor** | Transversal | Operativo | ✅ Sí | Motor de extracción PDF -> TXT/MD. |
| **Firmar** | Transversal | Prototipo | ✅ Sí | Sistema de firma digital certificada. |
| **Scrapling** | Transversal | Operativo | ✅ Sí | Web scraping para análisis legal. |
| **LexScraper** | Transversal | Operativo | ✅ Sí | Vigilancia normativa y alimentación de Biblioteca Legal. |
| **Peritajes Forenses** | Vertical | Operativo | ✅ Sí | Generadores de informes y declaraciones. |
| **RRHH** | Core | Operativo | ✅ Sí | Ingesta de perfiles a base de conocimiento. |
| **Recuperación** | Utilitario | Operativo | ✅ Sí | Acceso a hardware/discos RAW (E:). |
| **Conector (MCP Hub)** | Transversal | Operativo | ✅ Sí | Hub MCP para Meta Ads, Gmail y WhatsApp + Notificaciones. |
| **MemoryPalace** | Core | En pausa | ✅ Sí | Integrado en infraestructura global. |
| **PeritoDigital** | Vertical | Operativo (Railway) | ✅ Sí | Integrado en infraestructura global. |
| **Academy** | Vertical | Por desarrollar | ✅ Sí | Integrado en infraestructura global. |
| **LegalConnect** | Vertical | Operativo | ✅ Sí | Conexión legal + Biblioteca Legal automatizada. |
| **AgenteInmobiliario** | Vertical | En desarrollo | ✅ Sí | Integrado en infraestructura global. |
| **Ecoinmobiliaria** | Cliente | Operativo (WASI) | ✅ Sí | Integrado en infraestructura global. |
| **RedesSociales** | Transversal | En desarrollo | ✅ Sí | Integrado en infraestructura global. |
| **Vetsys** | Vertical | Por desarrollar | ✅ Sí | Integrado en infraestructura global. |

---

## 🐳 Infraestructura: Orquestación Única (Raíz)

Ubicación: `C:\Sorsabsa\docker-compose.yml`

El corazón técnico de Sorsabsa es el orquestador maestro en la raíz. Se abandonó la estrategia de "Docker Global" para favorecer servicios independientes y ligeros.
1. **Consistencia:** Cada servicio tiene su propio Dockerfile optimizado (`python-slim`, `node-alpine`).
2. **Ahorro de Espacio:** Se evita la duplicidad de capas compartiendo imágenes base de Docker.
3. **Interconectividad:** Los volúmenes permiten que un proyecto use la salida de otro (ej: RRHH usando el motor del Convertidor).
4. **Diagnóstico Único:** El script `health_check.py` en la raíz valida la salud de todo el ecosistema.

### 📖 Documentación de Referencia
- **[Arquitectura](SORSABSA_ARQUITECTURA.md)**: Estándares de desarrollo y base de datos.
- **[Log de Transición Docker](DOCKER_TRANSITION_LOG.md)**: Registro de deuda técnica y problemas superados en la migración.
- **[Matriz de Servicios](SORSABSA%20Matriz%20de%20Servicios.md)**: Estado de integración de cada módulo.
  
### 🛠️ Cómo declarar un proyecto faltante
Para que los proyectos se integren, deben añadirse al archivo `C:\Sorsabsa\docker-compose.yml` siguiendo este formato:

```yaml
  nombre-del-proyecto:
    build: ./Carpeta
    volumes:
      - ./NombreCarpeta:/app
    working_dir: /app
```

---

## 🏢 Visión General

**Sorsabsa** es una plataforma de desarrollo de software que produce soluciones para diferentes industrias, organizadas en tres categorías principales:

### 📊 Estructura del Portafolio

```
SORSABSA
├── 🏗️ VERTICALES (Productos por Industria)
│   ├── CondoManager SAAS → Gestión de condominios y conjuntos residenciales
│   ├── AgenteInmobiliario → Plataforma de gestión inmobiliaria
│   │   └── Ecoinmobiliaria (cliente) → Marketplace inmobiliario
│   ├── LegalConnect → Plataforma de conexión legal (Ecuador)
│   ├── VetSys System → Sistema para clínicas veterinarias
│   ├── Academy → Plataforma de comunidades educativas
│   │   └── VetSys Academy (primer cliente) → Comunidad veterinaria
│   └── [Otras verticales en desarrollo]
│
├── 🔧 TRANSVERSALES (Productos Multipropósito)
│   ├── Convertidor → Motor de extracción PDF -> TXT/MD
│   ├── LexScraper → Vigilancia normativa y alimentación de Biblioteca Legal
│   ├── Firmar → Firma digital y validación documental
│   ├── Gestión Documental → Administración de documentos
│   ├── Marketplace → Catálogo de productos/servicios integrables
│   └── [Otros transversales]
│
└── 🎯 CORE (Componentes Operativos No Vendibles)
    ├── Autenticación → Gestión de usuarios y permisos
    ├── Notificaciones → Sistema de alertas y comunicaciones
    ├── Auditoría → Trazabilidad de operaciones
    ├── Backup → Respaldo y recuperación de datos
    └── [Otros componentes core]
```

---

## 🏗️ Verticales (Productos por Industria)

Las **verticales** son productos completos diseñados para industrias específicas, que integran componentes transversales y core según las necesidades del sector.

### CondoManager SAAS
**Gestión integral de condominios y conjuntos residenciales**

- ✅ **Estado**: En desarrollo activo (~45% completado)
- 🎯 **Funcionalidades**:
  - Gestión de unidades y propietarios
  - Generación automática de alícuotas
  - Control de pagos y morosidad
  - Contabilidad completa
  - Comunicación con residentes
  - Portal de pagos en línea
- 🔗 **Integraciones**:
  - **AgenteInmobiliario**: Publicación automática de unidades en venta/arriendo
  - **Marketplace**: Productos y servicios para condominios
  - **Sistema Contable Transversal**: Gestión financiera
  - **Firmar**: Validación de documentos oficiales

---

### AgenteInmobiliario (Vertical)
**Plataforma de gestión y publicación inmobiliaria**

- 🏗️ **Estado**: En desarrollo (reemplaza integración con WASI)
- 🎯 **Propósito**: Centralizar la gestión de propiedades para inmobiliarias
- 📋 **Antecedentes**:
  - **Situación actual**: Ecoinmobiliaria usa WASI (plataforma externa)
  - **Problema**: WASI no permite integración nativa con CondoManager
  - **Solución**: Desarrollar AgenteInmobiliario como vertical propio
- 🔗 **Integraciones**:
  - **CondoManager**: Publicación automática de unidades de condominios
  - **Marketplace**: Donde los administradores activan el servicio
  - **Firmar**: Validación de contratos de venta/arriendo
  - **Sistema de Recaudación**: Procesamiento de pagos inmobiliarios

---

### Ecoinmobiliaria (Cliente de AgenteInmobiliario)
**Primer cliente del vertical AgenteInmobiliario**

- 🌐 **Sitio actual**: https://ecoinmobiliaria.inmo.co/
- 📊 **Modelo**: Marketplace inmobiliario
- 🔗 **Funcionamiento**:
  1. **CondoManager** detecta unidad en venta/arriendo
  2. **AgenteInmobiliario** recibe la propiedad automáticamente
  3. **Ecoinmobiliaria** publica en su marketplace
  4. **Marketplace de Sorsabsa** muestra a usuarios finales
- 🎯 **Activación**: Los administradores de condominios activan Ecoinmobiliaria desde el Marketplace

---

### LegalConnect (Vertical)
**Plataforma de conexión legal para Ecuador**

- ⚖️ **Estado**: Operativo (en desarrollo activo)
- 🎯 **Propósito**: Democratizar el acceso a la justicia en Ecuador
- 🌐 **Sitio**: https://lovable.dev/projects/5f89d4f1-0e14-4908-aac4-c0065773ddee
- 📋 **Funcionalidades**:
  - **Directorio de abogados verificados** con perfiles y especialidades
  - **Publicación de casos** mediante texto o audio
  - **Sistema de propuestas privadas** (máximo 3 por caso)
  - **Suscripciones para abogados** con distintos niveles de licencia
  - **Pagos integrados con PayPhone** (pasarela ecuatoriana)
- 📚 **Biblioteca Legal Oficial**:
  - **Fuente**: Scraping automático del Registro Oficial, Asamblea Nacional, Corte Constitucional
  - **Contenido**: Leyes, decretos, resoluciones, suplementos del Registro Oficial
  - **Clasificación**: Sistema tipo Lexis/Ediciones Legales
  - **Acceso**: Catálogo público y buscable con enlaces a PDFs originales
- 🔗 **Integraciones**:
  - **Firmar**: Validación de documentos legales
  - **Scrapling**: Motor de scraping para la biblioteca legal
  - **Sistema de Recaudación**: Procesamiento de pagos de suscripciones
- 🇪🇨 **Localización**: Estrictamente adaptado al contexto ecuatoriano
  - Ciudades, provincias y jurisdicciones del Ecuador
  - Categorías legales alineadas a la legislación nacional
  - Pagos en dólares estadounidenses (moneda oficial)

---

### VetSys System (Vertical)
**Sistema integral para clínicas veterinarias**

- 🏥 **Estado**: Por desarrollar
- 🎯 **Propósito**: Digitalizar y optimizar la gestión de clínicas veterinarias
- 📋 **Funcionalidades esperadas**:
  - Gestión de pacientes (mascotas) y propietarios
  - Historial médico veterinario
  - Agenda de citas y recordatorios
  - Inventario de medicamentos y productos
  - Facturación electrónica
  - Recetas digitales
- 🔗 **Integraciones**:
  - **VetSys Academy**: Plataforma educativa para la comunidad veterinaria
  - **Marketplace**: Productos y servicios para clínicas
  - **Sistema Contable**: Gestión financiera de la clínica
  - **Firmar**: Validación de recetas y documentos médicos

---

### Academy (Vertical)
**Plataforma de comunidades educativas con modelo de marketing sostenible**

- 🎓 **Estado**: Por desarrollar
- 🎯 **Propósito**: Construir comunidades que conectan alumnos, maestros, proveedores y eventos
- 💡 **Modelo de negocio**: Marketing educativo sostenible
  - Incentiva la compra de soluciones/productos dentro de la comunidad
  - Los usuarios aprenden mientras interactúan con la marca
  - Los proveedores financian la plataforma con sus pagos
- 📋 **Características principales**:
  - **Para alumnos**: Creación de flashcards, acceso a contenido educativo
  - **Para proveedores**: Espacio dedicado para publicidad y promoción
  - **Para expertos**: Publicaciones, eventos, charlas magistrales
  - **Para organizaciones**: Posicionamiento de marca a través de la educación
- 🎯 **Clientes potenciales**:
  - Facultades universitarias (ej: veterinaria)
  - Empresas que quieren formar a sus clientes (ej: Procan)
  - Colegios que implementan métodos de estudio
- 🔗 **Integraciones**:
  - **Marketplace**: Donde las organizaciones activan Academy
  - **Sistema de Recaudación**: Pagos de proveedores y suscripciones
  - **Notificaciones**: Recordatorios de eventos y novedades

---

### VetSys Academy (Cliente de Academy)
**Primer caso de uso de Academy - Comunidad veterinaria**

- 🐾 **Estado**: Por desarrollar (será el primer cliente de Academy)
- 🎯 **Propósito**: Apoyar la venta de VetSys System y crear comunidad veterinaria
- 📋 **Funcionalidades específicas**:
  - **Alumnos** (estudiantes de veterinaria):
    - Crear tarjetas de estudio (flashcards)
    - Acceder a novedades sobre veterinaria y tecnología
  - **Proveedores**:
    - Pagan publicidad para llegar a universitarios y médicos veterinarios
    - Promocionan productos y servicios especializados
  - **Médicos veterinarios**:
    - Publican casos y experiencias
    - Organizan eventos y seminarios
    - Comparten conocimiento con la comunidad
- 💡 **Objetivo estratégico**: Herramienta de venta para VetSys System
  - Los usuarios se familiarizan con el ecosistema VetSys
  - Creación de comunidad antes del lanzamiento del sistema principal
  - Generación de leads calificados para VetSys System

---

### Sistema Contable (Vertical de Dominio Compartido)
**Gestión financiera multi-industria**

- ✅ **Estado**: En desarrollo
- 🎯 **Propósito**: Ofrecer un sistema contable completo como producto independiente y como motor para otros verticales.
- 📋 **Características**:
  - Plan de cuentas configurable
  - Movimientos contables
  - Reportes financieros
  - Presupuestos
  - Centros de costo
- 🔗 **Integraciones**: Consumido por CondoManager, Vetsys y otros verticales.

---

### Sistema de Recaudación (Vertical de Dominio Compartido)
**Procesamiento de pagos y cobros**

- ✅ **Estado**: En desarrollo
- 🎯 **Propósito**: Gestionar deudas, facturación y cobranza como producto independiente y como servicio para otros verticales.
- 💳 **Funcionalidades**:
  - Múltiples métodos de pago
  - Reconciliación automática
  - Gestión de morosidad
  - Pasarelas de pago integradas
- 🔗 **Integraciones**: Payphone, Stripe, PayPal, y consumido por CondoManager, LegalConnect, Academy, etc.

---

## 🔧 Transversales (Productos Multipropósito)

Los **transversales** son productos independientes que pueden venderse por separado o integrarse en verticales según las necesidades del cliente.

### Sistema Contable
**Gestión financiera multi-industria**

### Sistema de Recaudación
**Procesamiento de pagos y cobros**

- 💳 **Funcionalidades**:
  - Múltiples métodos de pago
  - Reconciliación automática
  - Gestión de morosidad
  - Pasarelas de pago integradas
### Firmar
**Firma digital y validación documental**

- ✍️ **Capacidades**:
  - Firma digital certificada
  - Validación de documentos
  - Sellado de tiempo
  - Verificación de autenticidad

### Gestión Documental
**Administración inteligente de documentos**

- 📄 **Características**:
  - Almacenamiento seguro
  - Búsqueda full-text
  - Control de versiones
  - Flujo de aprobación

### Marketplace
**Catálogo de productos y servicios integrables**

- 🛒 **Propósito**: Permitir a los usuarios activar servicios adicionales
- 🎯 **Ejemplos**:
  - Servicios de mantenimiento para condominios
  - Seguros para propiedades
  - Servicios de limpieza
  - Seguridad privada

---

## 🎯 Core (Componentes Operativos)

El **core** son componentes necesarios para la operación de cualquier producto Sorsabsa, pero que no son vendibles por separado.

### Autenticación
- Gestión de usuarios y roles
- Single Sign-On (SSO)
- Recuperación de contraseñas
- Verificación en dos pasos

### Notificaciones
- Sistema de alertas
- Emails transaccionales
- Notificaciones push
- SMS y WhatsApp

### Auditoría
- Trazabilidad completa
- Logs de operaciones
- Reportes de actividad
- Cumplimiento normativo

### Backup
- Respaldo automático
- Recuperación de desastres
- Versionado de datos
- Almacenamiento redundante

---

## 🏗️ Arquitectura Técnica

### Docker Global
Este repositorio utiliza una arquitectura de contenedores centralizada para simplificar el desarrollo:

- **Ubicación**: `docker-compose.yml` en la raíz
- **Propósito**: Todos los subproyectos comparten una imagen base pre-configurada
- **Ventajas**:
  - Evita instalación redundante de dependencias
  - Entorno de desarrollo consistente
  - Rápida incorporación de nuevos desarrolladores

### Organización de Unidades
### Stack Tecnológico Principal
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Node.js + Supabase (PostgreSQL + Auth + Storage)
- **Contenedores**: Docker + Docker Compose
- **IA/ML**: Python + Pandas + NumPy
- **Automatización**: n8n + MCP Servers

---

## 📦 Productos y Módulos

### CondoManager SAAS
- **Ubicación**: `condomanager-saas/`
- **Estado**: 45% completado
- **Última actualización**: Sistema de generación de deudas implementado

### Convertidor
- **Ubicación**: `CONVERTIDOR/`
- **Propósito**: Conversión de PDF a texto/Markdown/CSV
- **Tecnología**: Python + OCR + Procesamiento de lenguaje natural

### Firmar
- **Ubicación**: `firmar/`
- **Propósito**: Sistema de firma digital
- **Estado**: Prototipo funcional

### Scrapling
- **Ubicación**: `Scrapling/`
- **Propósito**: Web scraping inteligente
- **Casos de uso**: Extracción de datos para análisis legal

### Conector
- **Ubicación**: `Conector/`
- **Propósito**: Integración con APIs externas
- **Ejemplos**: WhatsApp, Gmail, Meta Ads

### MemoryPalace
- **Ubicación**: `MemoryPalace/`
- **Propósito**: Sistema de gestión de conocimiento con IA
- **Características**: Agentes especializados, orquestación inteligente

---

## 🚀 Uso Rápido

### Ejecutar desarrollo
```bash
# Para levantar servicios específicos (ej: CondoManager e Identity)
docker compose up -d condomanager identity

# PowerShell
```

### Ejecutar recuperación de disco
```bash
./.docker_global/run.sh recuperacion python lector_raw.py
```

### Limpieza
```bash
./clean.ps1  # Windows
./clean.sh   # Linux/Mac
```

---

## 📈 Roadmap Estratégico

### Corto Plazo (Q2 2026)
- [ ] Completar módulo de pagos de CondoManager
- [ ] Integrar Ecoinmobiliaria con CondoManager
- [ ] Lanzar versión beta del Marketplace
- [ ] Implementar sistema de notificaciones core

### Mediano Plazo (Q3-Q4 2026)
- [ ] Completar sistema contable transversal
- [ ] Integrar Firmar con todas las verticales
- [ ] Lanzar sistema de recaudación
- [ ] Implementar gestión documental

### Largo Plazo (2027)
- [ ] Desarrollar nuevas verticales (salud, educación)
- [ ] Implementar IA predictiva en todos los productos
- [ ] Expandir a mercados internacionales
- [ ] Certificaciones de seguridad y cumplimiento

---

## 🤝 Contribución

Este es un repositorio privado de Sorsabsa. Para contribuir:

1. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
2. Commit de cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
3. Push a la rama (`git push origin feature/nueva-funcionalidad`)
4. Crear Pull Request

---

## 📄 Licencia

© 2026 Sorsabsa. Todos los derechos reservados.

Este software es propiedad intelectual de Sorsabsa y su uso está restringido a los términos establecidos en los contratos de licencia correspondientes.

---

## 📞 Contacto

- **Sitio web**: [sorsabsa.com](https://sorsabsa.com)
- **Email**: info@sorsabsa.com
- **Ubicación**: Ecuador

---

**Última actualización**: Mayo 2026  
**Versión del documento**: 2.0