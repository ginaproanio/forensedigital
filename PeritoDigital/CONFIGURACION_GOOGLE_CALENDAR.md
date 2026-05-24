# 📅 CONFIGURACIÓN DE GOOGLE CALENDAR PARA PERITO DIGITAL

Esta guía te ayudará a configurar la integración con Google Calendar para que las citas agendadas por WhatsApp se creen automáticamente en tu calendario.

---

## 📋 REQUISITOS PREVIOS

1. **Cuenta de Google** (Gmail o Google Workspace)
2. **Acceso a Google Cloud Console**
3. **Proyecto en Railway** (ya desplegado)

---

## 🔧 PASOS DE CONFIGURACIÓN

### **Paso 1: Crear Proyecto en Google Cloud Console**

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Nombre sugerido: "PeritoDigital-SORSABSA"

### **Paso 2: Habilitar Google Calendar API**

1. En el menú lateral, ve a **APIs y Servicios** → **Biblioteca**
2. Busca "Google Calendar API"
3. Haz click en **Habilitar**

### **Paso 3: Crear Credenciales OAuth 2.0**

1. Ve a **APIs y Servicios** → **Pantalla de consentimiento de OAuth**
2. Selecciona **Externo** (a menos que tengas Google Workspace)
3. Completa el formulario:
   - Nombre de la aplicación: "Perito Digital - SORSABSA"
   - Correo de asistencia: tu email
   - Información de contacto del desarrollador: tu email
4. Guarda y continúa

5. Ve a **Credenciales** → **Crear Credenciales** → **ID de cliente de OAuth**
6. Tipo de aplicación: **Aplicación web**
7. Nombre: "PeritoDigital Web Client"
8. **URIs de redireccionamiento autorizados:**
   ```
   https://peritodigital-production.up.railway.app/oauth/callback
   ```
   (Reemplaza con tu URL real de Railway si es diferente)

9. Haz click en **Crear**
10. **Descarga el JSON** (botón de descarga) → Guárdalo como `client_secret.json`

### **Paso 4: Subir Credenciales a Railway**

**Opción A: Variables de Entorno (Recomendado para producción)**

1. Convierte el contenido de `client_secret.json` a una variable de entorno:
   ```bash
   # En tu terminal local:
   cat client_secret.json | base64
   ```
2. En Railway Dashboard → Tu proyecto → Variables → Nueva variable:
   - Nombre: `GOOGLE_CLIENT_SECRET_JSON`
   - Valor: (el output de base64)

3. Actualiza `calendar.py` para leer de la variable de entorno:
   ```python
   import base64
   import json
   
   # En lugar de leer de archivo:
   json_data = base64.b64decode(os.getenv("GOOGLE_CLIENT_SECRET_JSON"))
   client_secrets = json.loads(json_data)
   
   # Guardar temporalmente para el flujo OAuth
   with open(CLIENT_SECRET_FILE, 'w') as f:
       json.dump(client_secrets, f)
   ```

**Opción B: Subir archivo directamente (Más simple para pruebas)**

1. En Railway Dashboard → Tu proyecto → Files
2. Sube `client_secret.json` a la raíz del proyecto
3. Asegúrate de que el archivo esté en el mismo nivel que `agent/`

### **Paso 5: Autorizar la Aplicación (Primer Uso)**

**Método 1: Local (Recomendado para primera vez)**

1. Ejecuta localmente:
   ```bash
   cd PeritoDigital
   python -c "from agent.calendar import get_calendar_url; print(get_calendar_url())"
   ```
2. Abre la URL en tu navegador
3. Inicia sesión con tu cuenta de Google
4. Autoriza la aplicación
5. Serás redirigido a una URL con un código (ej: `http://localhost?code=4/0AX4XfWh...`)
6. Copia el código (después de `code=`)

7. Ejecuta:
   ```bash
   python -c "from agent.calendar import autorizar_calendar; autorizar_calendar('TU_CODIGO_AQUI')"
   ```
8. Se creará `token.json` en la raíz del proyecto

9. Sube `token.json` a Railway (mismo método que `client_secret.json`)

**Método 2: Usar Railway directamente**

1. Agrega un endpoint en `main.py`:
   ```python
   @app.get("/oauth/start")
   async def oauth_start():
       from .calendar import get_calendar_url
       return {"url": get_calendar_url()}
   
   @app.get("/oauth/callback")
   async def oauth_callback(request: Request):
       from .calendar import autorizar_calendar
       code = request.query_params.get("code")
       if not code:
           return {"error": "No code provided"}
       try:
           autorizar_calendar(code)
           return {"status": "ok", "message": "Google Calendar autorizado"}
       except Exception as e:
           return {"error": str(e)}
   ```

2. Deploy a Railway
3. Visita `https://tu-app.up.railway.app/oauth/start`
4. Autoriza y copia el código de la URL de redireccionamiento
5. Visita `https://tu-app.up.railway.app/oauth/callback?code=TU_CODIGO`

### **Paso 6: Verificar Funcionamiento**

1. Revisa los logs de Railway después de una cita agendada
2. Deberías ver:
   ```
   📅 Cita detectada para [Nombre] — procesando...
   ✅ Cita agendada en Google Calendar para [Nombre] — [Fecha] [Hora]
   ✅ Evento creado: https://calendar.google.com/calendar/event?eid=...
   ```

3. Revisa tu Google Calendar → Debería aparecer el evento

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### **Problema 1: "No hay credenciales de Google Calendar"**
**Causa:** Falta `client_secret.json` o `token.json`

**Solución:**
```bash
# Verifica que los archivos existen en Railway
# Railway Dashboard → Files → Deberías ver:
# - client_secret.json
# - token.json (después de la primera autorización)
```

### **Problema 2: Error 401/403 de Google API**
**Causa:** Credenciales inválidas o API no habilitada

**Solución:**
1. Verifica que Google Calendar API esté habilitada en Google Cloud Console
2. Revisa que el `client_secret.json` sea correcto
3. Elimina `token.json` y vuelve a autorizar

### **Problema 3: Error "redirect_uri_mismatch"**
**Causa:** El redirect URI en Google Cloud no coincide con el de Railway

**Solución:**
1. En Google Cloud Console → Credenciales
2. Edita el cliente OAuth
3. Agrega el redirect URI correcto: `https://tu-app.up.railway.app/oauth/callback`

### **Problema 4: Eventos no se crean**
**Causa:** Problema de permisos o zona horaria

**Solución:**
1. Verifica logs de Railway para errores específicos
2. Asegúrate de que la cuenta de Google tenga permisos de calendario
3. Revisa que la zona horaria sea "America/Guayaquil"

---

## 🛡️ SEGURIDAD

### **Archivos Sensibles:**
- `client_secret.json` - Credenciales de la aplicación (públicas, no críticas)
- `token.json` - Token de acceso del usuario (CRÍTICO - no compartir)

### **Recomendaciones:**
1. **Nunca** subas `token.json` a GitHub
2. Usa variables de entorno en Railway para producción
3. Rota las credenciales periódicamente
4. Limita los scopes al mínimo necesario (ya estamos usando solo Calendar)

---

## 📊 MONITOREO

### **Métricas a revisar:**
- **Tasa de éxito de agendamiento:** % de citas que se crean exitosamente
- **Tiempo de creación:** Cuánto tarda en crearse el evento después de la confirmación
- **Errores comunes:** Revisa logs por patrones de error

### **Comandos útiles:**
```bash
# Ver logs de citas en Railway
Railway Dashboard → Logs → Filtrar por "Cita detectada"

# Ver eventos creados
Railway Dashboard → Logs → Filtrar por "Evento creado"

# Ver errores
Railway Dashboard → Logs → Filtrar por "Error"
```

---

## 🔄 MANTENIMIENTO

### **Cada 3 meses:**
1. Revisa que el token no haya expirado
2. Verifica que los eventos se siguen creando
3. Limpia logs antiguos

### **Si cambias de cuenta de Google:**
1. Elimina `token.json` de Railway
2. Vuelve a autorizar con la nueva cuenta
3. Actualiza el email en Google Cloud Console si es necesario

---

## 📞 SOPORTE

Si tienes problemas después de seguir esta guía:

1. **Revisa los logs de Railway** - La mayoría de errores están ahí
2. **Verifica Google Cloud Console** - API habilitada y credenciales válidas
3. **Prueba localmente** - Ejecuta `python -c "from agent.calendar import calendario_autorizado; print(calendario_autorizado())"`

---

## ✅ CHECKLIST DE CONFIGURACIÓN

- [ ] Proyecto creado en Google Cloud Console
- [ ] Google Calendar API habilitada
- [ ] Credenciales OAuth creadas
- [ ] `client_secret.json` descargado
- [ ] `client_secret.json` subido a Railway
- [ ] Primera autorización completada
- [ ] `token.json` subido a Railway
- [ ] Evento de prueba creado exitosamente
- [ ] Logs verificados en Railway

---

**Estado:** Listo para configurar  
**Próximo paso:** Seguir Pasos 1-5 de esta guía  
**Tiempo estimado:** 15-20 minutos