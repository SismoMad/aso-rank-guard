#!/bin/bash

###############################################################################
# ACTUALIZAR SERVIDOR AUTOMÁTICAMENTE
# Conecta al servidor y actualiza el código desde GitHub
###############################################################################

set -e

SERVER="root@194.164.160.111"

echo "🚀 Actualizando servidor..."
echo "======================================"

# Conectar al servidor y ejecutar comandos
ssh $SERVER << 'ENDSSH'
    set -e
    
    echo "📂 Navegando al proyecto..."
    cd aso-rank-guard || { echo "❌ Proyecto no encontrado"; exit 1; }
    
    echo "📥 Descargando últimos cambios de GitHub..."
    git pull origin main
    
    echo "📦 Instalando dependencias..."
    cd web-app
    npm install
    
    echo "🏗️  Compilando aplicación..."
    npm run build
    
    echo "🔄 Reiniciando servidor..."
    if pm2 list | grep -q "nextjs-app"; then
        pm2 restart nextjs-app
    else
        pm2 start npm --name "nextjs-app" -- start
    fi
    
    pm2 save
    
    echo ""
    echo "✅ ¡ACTUALIZACIÓN COMPLETADA!"
    echo "🌐 Visita: http://194.164.160.111"
    
ENDSSH

echo ""
echo "✅ Todo listo!"
