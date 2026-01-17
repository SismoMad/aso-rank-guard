#!/bin/bash
# Ejecuta esto DIRECTAMENTE en tu servidor 194.164.160.111

echo "🚀 Desplegando Next.js App..."

# Ir al directorio
cd /root/aso-rank-guard/web-app || exit 1

# Instalar dependencias
echo "📦 Instalando dependencias..."
npm install --production

# Build
echo "🏗️ Building app..."
npm run build

# PM2
echo "🔄 Configurando PM2..."
npm install -g pm2

# Detener proceso anterior
pm2 delete nextjs-app 2>/dev/null || true

# Iniciar
pm2 start npm --name "nextjs-app" -- start

# Guardar
pm2 save
pm2 startup

# Ver estado
pm2 list

echo ""
echo "✅ LISTO!"
echo "🌐 http://194.164.160.111/"
