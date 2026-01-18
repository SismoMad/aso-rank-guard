#!/bin/bash
# Deploy automático al servidor IONOS

set -e

SERVER="root@194.164.160.111"
APP_DIR="/root/aso-rank-guard"

echo "🚀 Desplegando a producción..."

# 1. Asegurar que los cambios están en GitHub
echo "📤 Subiendo cambios a GitHub..."
git add .
read -p "Mensaje del commit: " COMMIT_MSG
git commit -m "$COMMIT_MSG" || echo "Sin cambios para commitear"
git push origin main

# 2. Actualizar servidor
echo "🔄 Actualizando servidor..."
ssh $SERVER << 'ENDSSH'
cd /root/aso-rank-guard

# Pull últimos cambios
git pull origin main

# Actualizar Next.js
cd web-app
npm install
npm run build

# Reiniciar app
pm2 restart nextjs-app || pm2 start npm --name "nextjs-app" -- start

echo "✅ Deploy completado"
pm2 status
ENDSSH

echo ""
echo "✅ ¡Desplegado con éxito!"
echo "🌐 Visita: http://194.164.160.111:3000"
