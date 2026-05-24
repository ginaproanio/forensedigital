#!/bin/bash

# SORSABSA - MCP Hub (Conector) - Configuración de Entorno

echo "🚀 Preparando entorno para MCP Hub (Conector)"
echo "================================================"

# Crear estructura de carpetas si no existe
mkdir -p servers/meta-ads servers/gmail servers/whatsapp shared config

# Crear archivo .env base si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde .env.example..."
    printf "# Credenciales Globales Hub\nNODE_ENV=development\nMETA_ACCESS_TOKEN=\nMETA_AD_ACCOUNT_ID=\nGMAIL_CREDENTIALS_JSON=\nWHATSAPP_API_TOKEN=\n" > .env
    echo "✅ .env creado. Por favor edita el archivo con tus credenciales."
else
    echo "ℹ️  .env ya existe."
fi

# Instrucciones finales
echo ""
echo "📋 Próximos pasos:"
echo "=================="
echo "1. Edita el archivo .env con tus credenciales de Meta:"
echo "   - META_ACCESS_TOKEN"
echo "   - GMAIL_CREDENTIALS_JSON"
echo "   - WHATSAPP_API_TOKEN"
echo "   - NODE_PATH=/usr/local/lib/node_modules"
echo ""
echo "2. Configura Claude Desktop usando las rutas en README.md"
echo "   (command: docker exec -i conector ...)"
echo "   Nota: El contenedor ya dispone de las librerías necesarias"
echo "         gracias a la imagen global de SORSABSA."
echo ""
echo "4. Revisa los prompts en la carpeta prompts/ para empezar a usar."
echo ""
echo "✅ ¡Configuración completada!"