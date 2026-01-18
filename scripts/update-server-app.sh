#!/bin/bash
# Script para actualizar la aplicación Next.js en el servidor
# Uso: ./scripts/update-server-app.sh

set -e

SERVER="root@194.164.160.111"
REMOTE_PATH="/root/aso-rank-guard"

echo "🚀 Actualizando aplicación en servidor..."

# 1. Copiar archivos de Next.js
echo "📦 Copiando archivos de Next.js..."
rsync -avz --delete \
  --exclude 'node_modules' \
  --exclude '.next' \
  --exclude '.env.local' \
  -e "ssh -o StrictHostKeyChecking=no" \
  ./web-app/ $SERVER:$REMOTE_PATH/web-app/

# 2. Copiar archivo de configuración de producción
echo "⚙️ Copiando configuración de producción..."
scp -o StrictHostKeyChecking=no \
  ./web-app/.env.production \
  $SERVER:$REMOTE_PATH/web-app/.env.production

# 3. Reinstalar dependencias y recompilar en servidor
echo "🏗️ Recompilando en servidor..."
ssh -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
cd /root/aso-rank-guard/web-app
npm install --production
npm run build
pm2 restart nextjs-app
pm2 save
ENDSSH

echo ""
echo "✅ ¡Actualización completada!"
echo "🌐 Aplicación disponible en: http://194.164.160.111:3000"
echo ""
echo "📊 Para ver logs:"
echo "   ssh $SERVER 'pm2 logs nextjs-app'"
echo ""
echo "📊 Para ver estado:"
echo "   ssh $SERVER 'pm2 list'"
