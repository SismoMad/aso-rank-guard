#!/bin/bash

# =============================================================================
# Script de Despliegue Automático a VPS
# ASO Rank Guard - Deploy to Production Server
# =============================================================================

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración del servidor
VPS_HOST="194.164.160.111"
VPS_USER="root"
VPS_DIR="/var/www/aso-rank-guard"
LOCAL_DIR="/Users/javi/aso-rank-guard"

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ASO Rank Guard - Deploy to VPS                        ║${NC}"
echo -e "${GREEN}║   Destino: ${VPS_HOST}                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# Función para mostrar progreso
# =============================================================================
function step() {
    echo -e "\n${YELLOW}➤ $1${NC}"
}

function success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# =============================================================================
# 1. Verificar conexión al servidor
# =============================================================================
step "1/8 Verificando conexión al servidor..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes ${VPS_USER}@${VPS_HOST} exit 2>/dev/null; then
    success "Conexión SSH establecida"
else
    error "No se puede conectar al servidor. Verifica la IP y que tengas configurada la clave SSH."
fi

# =============================================================================
# 2. Crear directorio en servidor (si no existe)
# =============================================================================
step "2/8 Creando directorio en servidor..."
ssh ${VPS_USER}@${VPS_HOST} "mkdir -p ${VPS_DIR}"
success "Directorio creado: ${VPS_DIR}"

# =============================================================================
# 3. Sincronizar archivos (rsync)
# =============================================================================
step "3/8 Sincronizando archivos con rsync..."
rsync -avz --progress \
    --exclude 'node_modules' \
    --exclude '.next' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'venv' \
    --exclude '.git' \
    --exclude 'data/*.csv' \
    --exclude 'logs/*.log' \
    --exclude '.env.local' \
    --exclude '.DS_Store' \
    ${LOCAL_DIR}/ \
    ${VPS_USER}@${VPS_HOST}:${VPS_DIR}/

success "Archivos sincronizados correctamente"

# =============================================================================
# 4. Crear archivo .env en servidor
# =============================================================================
step "4/8 Configurando variables de entorno..."
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /var/www/aso-rank-guard

# Crear .env para backend (solo si no existe)
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://bidqxydrybpuwyskrarh.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg2NjE3MjYsImV4cCI6MjA4NDIzNzcyNn0.jpMJgqjErP3u7XlzulGg7sMmBEH1Q8SbkVTFcXreaXE
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODY2MTcyNiwiZXhwIjoyMDg0MjM3NzI2fQ.LzvaXJDvE7nipsmnl-maaKcUzZkeRbnuccgw08gwOB8

# Telegram Bot
TELEGRAM_BOT_TOKEN=8531462519:AAFvX5PPyB177DUzylwgC8LMIUztrWPYfbI

# Admin Configuration
ADMIN_EMAIL=gutierrezjavier1989@gmail.com

# API Settings
ITUNES_API_DELAY=1.5
ITUNES_API_MAX_RETRIES=3
TEST_MODE=false
LOG_LEVEL=INFO
LOG_FILE=/var/www/aso-rank-guard/logs/rank_guard.log
EOF
    chmod 600 .env
    echo "✓ Archivo .env creado"
else
    echo "ℹ .env ya existe, no se sobrescribe"
fi

# Crear .env.production para Next.js
cd web-app
if [ ! -f .env.production ]; then
    cat > .env.production << 'EOF'
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://bidqxydrybpuwyskrarh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg2NjE3MjYsImV4cCI6MjA4NDIzNzcyNn0.jpMJgqjErP3u7XlzulGg7sMmBEH1Q8SbkVTFcXreaXE

# Backend API
NEXT_PUBLIC_API_URL=http://194.164.160.111:8000

# App
NEXT_PUBLIC_APP_NAME=ASO Rank Guard
NEXT_PUBLIC_APP_URL=http://194.164.160.111
EOF
    chmod 600 .env.production
    echo "✓ Archivo .env.production creado"
else
    echo "ℹ .env.production ya existe, no se sobrescribe"
fi
ENDSSH

success "Variables de entorno configuradas"

# =============================================================================
# 5. Instalar dependencias Python
# =============================================================================
step "5/8 Instalando dependencias Python..."
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /var/www/aso-rank-guard

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Entorno virtual creado"
fi

# Activar entorno e instalar dependencias
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "✓ Dependencias Python instaladas"
ENDSSH

success "Python configurado correctamente"

# =============================================================================
# 6. Instalar dependencias Node.js y buildear Next.js
# =============================================================================
step "6/8 Instalando dependencias Node.js y buildeando Next.js..."
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /var/www/aso-rank-guard/web-app

# Instalar dependencias
npm install

# Build de producción
npm run build

echo "✓ Next.js buildeado correctamente"
ENDSSH

success "Next.js configurado correctamente"

# =============================================================================
# 7. Configurar y reiniciar PM2
# =============================================================================
step "7/8 Configurando PM2..."
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /var/www/aso-rank-guard

# Crear directorio de logs si no existe
mkdir -p logs

# Detener aplicaciones existentes (si están corriendo)
pm2 delete aso-api 2>/dev/null || true
pm2 delete aso-web 2>/dev/null || true

# Crear archivo de configuración PM2 si no existe
if [ ! -f ecosystem.config.js ]; then
    cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'aso-api',
      cwd: '/var/www/aso-rank-guard',
      script: '/var/www/aso-rank-guard/venv/bin/uvicorn',
      args: 'api.main:app --host 0.0.0.0 --port 8000',
      env: {
        PYTHONPATH: '/var/www/aso-rank-guard',
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/var/www/aso-rank-guard/logs/api-error.log',
      out_file: '/var/www/aso-rank-guard/logs/api-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    },
    {
      name: 'aso-web',
      cwd: '/var/www/aso-rank-guard/web-app',
      script: 'npm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/var/www/aso-rank-guard/logs/web-error.log',
      out_file: '/var/www/aso-rank-guard/logs/web-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    },
  ],
};
EOF
fi

# Iniciar aplicaciones con PM2
pm2 start ecosystem.config.js

# Guardar configuración PM2
pm2 save

echo "✓ PM2 configurado y aplicaciones iniciadas"
ENDSSH

success "PM2 configurado correctamente"

# =============================================================================
# 8. Verificar despliegue
# =============================================================================
step "8/8 Verificando despliegue..."

# Esperar 5 segundos para que arranquen los servicios
sleep 5

# Verificar estado de PM2
echo -e "\nEstado de PM2:"
ssh ${VPS_USER}@${VPS_HOST} "pm2 status"

# Verificar endpoints
echo -e "\nVerificando endpoints..."

# Health check API
if curl -f -s http://${VPS_HOST}/health > /dev/null 2>&1; then
    success "API Health Check: OK"
else
    echo -e "${YELLOW}⚠ API Health Check no responde aún (puede tardar unos segundos)${NC}"
fi

# Next.js homepage
if curl -f -s http://${VPS_HOST}/ > /dev/null 2>&1; then
    success "Next.js Homepage: OK"
else
    echo -e "${YELLOW}⚠ Next.js no responde aún (puede tardar unos segundos)${NC}"
fi

# =============================================================================
# Resumen final
# =============================================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   🎉 DESPLIEGUE COMPLETADO CON ÉXITO                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📍 URLs de tu aplicación:"
echo -e "   Web App:     ${GREEN}http://${VPS_HOST}${NC}"
echo -e "   API:         ${GREEN}http://${VPS_HOST}/api${NC}"
echo -e "   Health:      ${GREEN}http://${VPS_HOST}/health${NC}"
echo -e "   API Docs:    ${GREEN}http://${VPS_HOST}/docs${NC}"
echo ""
echo -e "📊 Comandos útiles:"
echo -e "   Ver logs:    ${YELLOW}ssh ${VPS_USER}@${VPS_HOST} 'pm2 logs'${NC}"
echo -e "   Ver estado:  ${YELLOW}ssh ${VPS_USER}@${VPS_HOST} 'pm2 status'${NC}"
echo -e "   Reiniciar:   ${YELLOW}ssh ${VPS_USER}@${VPS_HOST} 'pm2 restart all'${NC}"
echo ""
echo -e "⚠️  ${YELLOW}Próximos pasos:${NC}"
echo -e "   1. Configurar Nginx reverse proxy (ver DEPLOY_VPS_GUIA.md paso 6)"
echo -e "   2. Configurar cron jobs para tracking (ver DEPLOY_VPS_GUIA.md paso 7)"
echo -e "   3. Configurar SSL/HTTPS con Let's Encrypt (ver DEPLOY_VPS_GUIA.md paso 8)"
echo ""
echo -e "📖 Documentación completa: ${YELLOW}DEPLOY_VPS_GUIA.md${NC}"
echo ""
