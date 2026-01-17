#!/bin/bash

###############################################################################
# DESPLIEGUE RÁPIDO - ASO RANK GUARD
# Despliega Next.js app en producción
###############################################################################

set -e

echo "🚀 Desplegando ASO Rank Guard Web App"
echo "======================================"

SERVER="root@194.164.160.111"
LOCAL_DIR="/Users/javi/aso-rank-guard/web-app"
REMOTE_DIR="/root/aso-rank-guard/web-app"

# 1. Crear build local
echo "📦 Creando build de producción..."
cd "$LOCAL_DIR"
npm run build

# 2. Comprimir archivos
echo "📦 Comprimiendo archivos..."
tar --exclude='node_modules' --exclude='.git' -czf /tmp/webapp.tar.gz .

# 3. Subir al servidor
echo "📤 Subiendo al servidor..."
scp /tmp/webapp.tar.gz $SERVER:/tmp/

# 4. Desplegar en servidor
echo "🔧 Desplegando en servidor..."
ssh $SERVER bash << 'EOF'
set -e

# Crear directorio si no existe
mkdir -p /root/aso-rank-guard/web-app
cd /root/aso-rank-guard/web-app

# Descomprimir
echo "📦 Descomprimiendo..."
tar -xzf /tmp/webapp.tar.gz
rm /tmp/webapp.tar.gz

# Instalar dependencias
echo "📚 Instalando dependencias..."
npm install --production

# Instalar PM2 si no está
if ! command -v pm2 &> /dev/null; then
    echo "📥 Instalando PM2..."
    npm install -g pm2
fi

# Reiniciar aplicación
echo "🔄 Reiniciando aplicación..."
pm2 delete nextjs-app 2>/dev/null || true
pm2 start npm --name "nextjs-app" -- start
pm2 save

echo "✅ Despliegue completado!"
pm2 list

EOF

# Limpiar
rm /tmp/webapp.tar.gz

echo ""
echo "✅ ¡LISTO!"
echo "=========="
echo ""
echo "🌐 Visita: http://194.164.160.111/"
echo "📊 Logs:   ssh root@194.164.160.111 'pm2 logs nextjs-app'"
echo ""
