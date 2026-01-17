#!/bin/bash

###############################################################################
# SCRIPT DE DESPLIEGUE - ASO RANK GUARD WEB APP
# Despliega la aplicación Next.js en el servidor 194.164.160.111
###############################################################################

set -e  # Exit on error

SERVER_IP="194.164.160.111"
SERVER_USER="root"
APP_DIR="/root/aso-rank-guard"
WEB_DIR="$APP_DIR/web-app"

echo "🚀 INICIANDO DESPLIEGUE DE ASO RANK GUARD WEB APP"
echo "=================================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Build local (opcional, podemos hacerlo en servidor)
echo -e "${BLUE}📦 Preparando archivos...${NC}"
cd web-app

# 2. Crear tarball con los archivos necesarios
echo -e "${BLUE}📦 Comprimiendo aplicación...${NC}"
tar -czf /tmp/webapp.tar.gz \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='.git' \
  .

# 3. Subir al servidor
echo -e "${BLUE}📤 Subiendo archivos al servidor...${NC}"
scp /tmp/webapp.tar.gz ${SERVER_USER}@${SERVER_IP}:/tmp/

# 4. Conectar y desplegar en servidor
echo -e "${BLUE}🔧 Desplegando en servidor...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

echo "📁 Creando directorios..."
mkdir -p /root/aso-rank-guard/web-app
cd /root/aso-rank-guard/web-app

echo "📦 Descomprimiendo archivos..."
tar -xzf /tmp/webapp.tar.gz
rm /tmp/webapp.tar.gz

echo "📚 Instalando dependencias..."
npm install --production=false

echo "🏗️ Building aplicación Next.js..."
npm run build

echo "🔄 Configurando PM2..."
# Verificar si PM2 está instalado
if ! command -v pm2 &> /dev/null; then
    echo "Instalando PM2..."
    npm install -g pm2
fi

# Detener proceso anterior si existe
pm2 delete nextjs-app 2>/dev/null || true

# Iniciar aplicación con PM2
pm2 start npm --name "nextjs-app" -- start

# Guardar configuración de PM2
pm2 save

# Configurar PM2 para inicio automático
pm2 startup systemd -u root --hp /root

echo "✅ Aplicación desplegada correctamente!"
pm2 status

ENDSSH

# 5. Verificar nginx
echo -e "${BLUE}🔧 Verificando nginx...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
# Verificar configuración de nginx
nginx -t

# Recargar nginx si es necesario
systemctl reload nginx

echo "✅ Nginx configurado correctamente"
ENDSSH

# Limpiar archivos temporales
rm /tmp/webapp.tar.gz

echo ""
echo -e "${GREEN}✅ DESPLIEGUE COMPLETADO!${NC}"
echo "=================================================="
echo ""
echo "🌐 Tu aplicación está disponible en:"
echo "   👉 http://194.164.160.111/"
echo ""
echo "📊 Para ver logs:"
echo "   ssh root@194.164.160.111 'pm2 logs nextjs-app'"
echo ""
echo "🔄 Para reiniciar:"
echo "   ssh root@194.164.160.111 'pm2 restart nextjs-app'"
echo ""
echo "📈 Para ver estado:"
echo "   ssh root@194.164.160.111 'pm2 status'"
echo ""
