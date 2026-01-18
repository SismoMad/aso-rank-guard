#!/bin/bash
# Setup completo para servidor IONOS (Ubuntu 24.04 + Plesk)
# Ejecutar: bash server-full-setup.sh

set -e

SERVER="root@194.164.160.111"

echo "🚀 Setup completo del servidor Ubuntu 24.04 + Plesk..."

# Conectar y ejecutar todo el setup
ssh $SERVER 'bash -s' << 'ENDSSH'

echo "📦 Actualizando sistema..."
apt update -y && apt upgrade -y

echo "🔧 Instalando herramientas básicas..."
apt install -y git curl wget build-essential

echo "📦 Instalando Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

echo "🔧 Instalando PM2..."
npm install -g pm2

echo "🔥 Configurando firewall..."
firewall-cmd --permanent --add (UFW)..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3000/tcp
ufw allow 8443/tcp  # Plesk
echo "y" | ufw enable || true
echo "📂 Clonando repositorio..."
cd /root
git clone https://github.com/javi/aso-rank-guard.git || (cd aso-rank-guard && git pull)

echo "📦 Instalando dependencias Next.js..."
cd /root/aso-rank-guard/web-app
npm install

echo "🏗️ Compilando Next.js..."
npm run build

echo "🚀 Iniciando con PM2..."
pm2 delete nextjs-app 2>/dev/null || true
pm2 start npm --name "nextjs-app" -- start
pm2 save
pm2 startup

echo "✅ ¡LISTO!"
echo "🌐 App disponible en: http://194.164.160.111:3000"

ENDSSH

echo ""
echo "✅ Setup completado!"
echo "🌐 Visita: http://194.164.160.111:3000"
