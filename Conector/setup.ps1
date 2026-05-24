# Conector Meta Ads - Script de Configuración Inicial (PowerShell)
# Este script ayuda a configurar el entorno para usar el Conector de Meta Ads

Write-Host "🚀 Configuración inicial del Conector Meta Ads" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Verificar si Node.js está instalado
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js detectado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js no está instalado. Por favor instálalo primero." -ForegroundColor Red
    exit 1
}

# Verificar si npm está instalado
try {
    $npmVersion = npm --version
    Write-Host "✅ npm detectado: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm no está instalado." -ForegroundColor Red
    exit 1
}

# Crear archivo .env si no existe
if (-not (Test-Path .env)) {
    Write-Host "📝 Creando archivo .env desde .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env creado. Por favor edita el archivo con tus credenciales." -ForegroundColor Green
} else {
    Write-Host "ℹ️  .env ya existe." -ForegroundColor Cyan
}

# Preguntar si instalar Meta Ads CLI globalmente
$installCLI = Read-Host "¿Deseas instalar el Meta Ads CLI globalmente? (s/n)"
if ($installCLI -eq 's' -or $installCLI -eq 'S') {
    Write-Host "📦 Instalando @meta-llc/meta-ads-cli..." -ForegroundColor Yellow
    npm install -g @meta-llc/meta-ads-cli
    
    try {
        $metaVersion = meta ads --version
        Write-Host "✅ Meta Ads CLI instalado: $metaVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  La instalación pudo haber fallado. Verifica manualmente." -ForegroundColor Yellow
    }
}

# Instrucciones finales
Write-Host ""
Write-Host "📋 Próximos pasos:" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host "1. Edita el archivo .env con tus credenciales de Meta:" -ForegroundColor White
Write-Host "   - META_ACCESS_TOKEN (tu token de acceso)" -ForegroundColor Cyan
Write-Host "   - META_AD_ACCOUNT_ID (tu ID de cuenta de anuncios)" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Configura el MCP en Claude:" -ForegroundColor White
Write-Host "   - URL: https://mcp.facebook.com/ads" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Prueba la conexión:" -ForegroundColor White
Write-Host "   meta ads campaign list --status ACTIVE" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Revisa los prompts en la carpeta prompts/ para empezar a usar." -ForegroundColor White
Write-Host ""
Write-Host "✅ ¡Configuración completada!" -ForegroundColor Green