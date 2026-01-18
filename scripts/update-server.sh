#!/bin/bash

###############################################################################
# ACTUALIZAR SERVIDOR - ASO Rank Guard
# Ejecuta esto EN EL SERVIDOR (después de ssh root@194.164.160.111)
###############################################################################

set -e

echo "🔄 Actualizando ASO Rank Guard en servidor"
echo "==========================================="

# Verificar si existe el proyecto
if [ -d "aso-rank-guard" ]; then
    echo "✅ Proyecto encontrado, actualizando..."
    cd aso-rank-guard
    
    # Actualizar código desde GitHub
    echo "📥 Descargando últimos cambios..."
    git pull origin main
    
else
    echo "📦 Proyecto no encontrado, clonando..."
    git clone https://github.com/SismoMad/aso-rank-guard.git
    cd aso-rank-guard
fi

# Actualizar web-app
echo ""
echo "🔧 Actualizando Next.js app..."
cd web-app

# Instalar/actualizar dependencias
echo "📚 Instalando dependencias..."
npm install

# Crear build de producción
echo "🏗️  Creando build..."
npm run build

# Reiniciar con PM2
echo "🔄 Reiniciando aplicación..."
if pm2 list | grep -q "nextjs-app"; then
    pm2 restart nextjs-app
    pm2 save
else
    pm2 start npm --name "nextjs-app" -- start
    pm2 save
fi

echo ""
echo "✅ ¡ACTUALIZACIÓN COMPLETADA!"
echo ""
echo "🌐 Tu app está en: http://194.164.160.111"
echo "📊 Ver logs: pm2 logs nextjs-app"
echo "📈 Ver estado: pm2 list"
echo ""
