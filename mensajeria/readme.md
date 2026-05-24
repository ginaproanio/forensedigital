# Mensajería: Primeros pasos con la API de la nube de WhatsApp

Referencia (Jasper's Market): https://github.com/fbsamples/whatsapp-business-jaspers-market

> Documento original traducido con IA. Puede contener errores; si necesitas precisión, revisa la fuente original.

## Actualizado
1 oct 2025

## Objetivo
Guía para desarrolladores que crean apps en la plataforma **WhatsApp Business**. Incluye:
- Creación de una app de Meta
- Conexión con una cuenta de WhatsApp Business
- Envío/recepción de mensajes
- Webhooks de prueba
- Generación de tokens (temporal/permanente)
- Envío de mensajes con y sin plantilla

## Descarga la app de ejemplo
**Jasper's Market** contiene todos los mensajes y el código usados en la demo. Sirve para aprender a enviar y administrar datos de la API de la nube de WhatsApp.

## Requisitos previos
- Cuenta de Facebook o cuenta de Meta administrada
- Registro de desarrolladores
- Dispositivo con WhatsApp para enviar y recibir mensajes de prueba

---

## Paso 1. Crear una nueva app de Meta con WhatsApp
1. Abre el panel de apps de Meta.
2. Haz clic en **Crear app**.
3. Agrega el nombre de la app y tu correo electrónico.
4. Selecciona el caso de uso **Conectarse con los clientes a través de WhatsApp** y haz clic en **Siguiente**.
5. Selecciona un portfolio comercial o crea uno.
6. Revisa requisitos de publicación y haz clic en **Siguiente**.
7. Confirma detalles y haz clic en **Crear app**.

Tras crear la app, se abre la sección **Personalizar caso de uso > Conectar en WhatsApp > Inicio rápido**.

---

## Paso 2. Comenzar a usar la API
1. En **Inicio rápido**, haz clic en **Comenzar a usar la API**.
2. Agrega un número de teléfono y envía tu primer mensaje.
3. En **Configuración de la API**, conecta la app a una cuenta de **WhatsApp Business**:
   - Cuenta preexistente: selecciónala en el desplegable.
   - Nueva cuenta: usa **Crear una cuenta de WhatsApp Business** y configura el perfil.

Guarda el **identificador** de tu cuenta de WhatsApp Business.

> Nota: si creaste un portfolio comercial nuevo, es posible que se haya creado automáticamente una cuenta de WhatsApp Business; verifica la conexión.

---

## Paso 3. Enviar y recibir mensajes
1. Haz clic en **Generar token de acceso** para un token temporal y envía un mensaje de prueba.
2. Selecciona **De** (número) y agrega **Para** (número receptor).
3. Envía el mensaje con **Enviar mensaje**.
4. Conserva:
   - Identificador del número de prueba
   - Identificador de la cuenta de WhatsApp Business
5. Responde al mensaje para continuar la conversación.

También podrás ajustar permisos y configuración en el menú izquierdo.

---

## Paso 4. Configurar la app de prueba de webhooks
Configura un endpoint webhook para recibir notificaciones (p. ej. *"leído"*/*"entregado"*).

Usa nuestro **servidor de webhook de ejemplo** y, una vez configurada la app de prueba, responde en el chat de WhatsApp. Verás una carga como esta:

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "215589313241560883",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15551797781",
              "phone_number_id": "7794189252778687"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Jessica Laverdetman"
                },
                "wa_id": "13557825698"
              }
            ],
            "messages": [
              {
                "from": "17863559966",
                "id": "wamid.HBgLMTc4NjM1NTk5NjYVAGHAYWYET688aASGNTI1QzZFQjhEMDk2QQA=",
                "timestamp": "1758254144",
                "text": {
                  "body": "Hi!"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

---

## Paso 5. Crear usuario del sistema y generar token permanente
El token temporal caduca rápido (para *hello_world*), por lo que debes crear un token permanente.

1. Ve a **Configuración del negocio > Usuarios del sistema**.
2. Crea un usuario con **Agregar+**.
3. Selecciona el usuario y haz clic en **Asignar activos**.
4. Activa en **Control total**:
   - **Administrar app** (para tu app)
   - **Administrar cuentas de WhatsApp Business** (para tu cuenta)
5. **Asignar activos** > **Generar token**.

Permisos para el token:
- `business_management`
- `whatsapp_business_messaging`
- `whatsapp_business_management`

Copia el token y guárdalo en un lugar seguro.

---

## Paso 6. Enviar un mensaje sin plantilla
Con el intervalo del servicio de atención al cliente (24h), puedes enviar mensajes sin plantilla.

Reemplaza los valores y ejecuta:

```bash
curl 'https://graph.facebook.com/v23.0/<TEST_BUSINESS_PHONE_NUMBER_ID>/messages' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <SYSTEM_USER_ACCESS_TOKEN>' \
  -d '{
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "<WHATSAPP_USER_PHONE_NUMBER>",
    "type": "text",
    "text": {
      "body": "Hello!"
    }
  }'
```

Luego, revisa la app de webhook de prueba para confirmar la recepción.

---

## Paso 7. Finalizar
La API de la nube de WhatsApp permite enviar mensajes y recibir webhooks; además ofrece funcionalidades como grupos y llamadas.

## Más información
- Tipos de mensajes sin plantilla
- Mensajes con plantilla
- Crear y administrar grupos
- Enviar y recibir llamadas
- Agregar un número de teléfono del negocio
- Configurar un servidor de webhook
- Registrar usuarios de WhatsApp Business (registro insertado)
- Convertirte en proveedor de soluciones
- Especificación OpenAPI de la API de WhatsApp

