#!/bin/bash

# Quick Start Script para ASO Rank Guard
# Ejecuta setup automático y primer test

echo "🛡️  ASO Rank Guard - Quick Start"
echo "========================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"
echo ""

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠️  Error instalando dependencias. Intentando solo las esenciales..."
    pip3 install requests pandas pyyaml schedule python-telegram-bot
fi

echo ""
echo "✅ Dependencias instaladas"
echo ""

# Ejecutar setup wizard
echo "🔧 Ejecutando wizard de configuración..."
echo ""
python3 setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Configuración completada"
    echo ""
    
    # Preguntar si ejecutar test
    read -p "¿Quieres ejecutar un test ahora? (s/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        echo ""
        echo "🧪 Ejecutando test..."
        python3 src/rank_tracker.py
    fi
else
    echo ""
    echo "⚠️  Setup cancelado o con errores"
fi

echo ""
echo "========================================"
echo "¡Gracias por usar ASO Rank Guard! 🚀"
echo "========================================"
