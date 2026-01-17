#!/bin/bash

# ASO Rank Guard - Script de ejecución rápida
# Uso: ./run.sh [comando]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_help() {
    echo ""
    echo "🛡️  ASO Rank Guard - Comandos disponibles"
    echo "=========================================="
    echo ""
    echo "  ${BLUE}./run.sh track${NC}       - Ejecutar tracking de keywords"
    echo "  ${BLUE}./run.sh monitor${NC}     - Ejecutar monitor completo (tracking + alertas)"
    echo "  ${BLUE}./run.sh expert${NC}      - 🎓 Análisis experto de ASO (sin tracking)"
    echo "  ${BLUE}./run.sh pro${NC}         - 🚀 Análisis PRO con scoring y evidencia"
    echo "  ${BLUE}./run.sh bot${NC}         - 🤖 Iniciar bot de Telegram (control remoto)"
    echo "  ${BLUE}./run.sh schedule${NC}    - Iniciar scheduler (mantener corriendo)"
    echo "  ${BLUE}./run.sh automate${NC}    - 🤖 Configurar automatización diaria"
    echo "  ${BLUE}./run.sh setup${NC}       - Configuración interactiva"
    echo "  ${BLUE}./run.sh test${NC}        - Test de alertas Telegram"
    echo "  ${BLUE}./run.sh install${NC}     - Instalar dependencias"
    echo "  ${BLUE}./run.sh status${NC}      - Ver últimos resultados"
    echo ""
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}⚠️  Python 3 no encontrado${NC}"
        exit 1
    fi
}

case "$1" in
    track)
        echo -e "${GREEN}🔍 Ejecutando tracking...${NC}"
        python3 src/rank_tracker.py
        ;;
    
    monitor)
        echo -e "${GREEN}🎯 Ejecutando monitor completo...${NC}"
        python3 src/run_monitor.py
        ;;
    
    expert)
        echo -e "${GREEN}🎓 Ejecutando análisis experto de ASO...${NC}"
        python3 src/aso_expert.py
        ;;
    
    pro)
        echo -e "${GREEN}🚀 Ejecutando análisis PRO con scoring...${NC}"
        python3 src/aso_expert_pro.py
        ;;
    
    bot)
        echo -e "${GREEN}🤖 Iniciando bot de Telegram...${NC}"
        echo -e "${YELLOW}(El bot estará activo hasta que presiones Ctrl+C)${NC}"
        echo -e "${BLUE}💡 Envía /start en Telegram para ver los comandos${NC}"
        echo ""
        python3 src/telegram_bot.py
        ;;
    
    schedule)
        echo -e "${GREEN}⏰ Iniciando scheduler...${NC}"
        echo -e "${YELLOW}(Presiona Ctrl+C para detener)${NC}"
        python3 src/scheduler.py
        ;;
    
    automate)
        echo -e "${GREEN}🤖 Configurador de automatización...${NC}"
        ./setup_automation.sh
        ;;
    
    setup)
        echo -e "${GREEN}⚙️  Iniciando configuración...${NC}"
        python3 setup.py
        ;;
    
    test)
        echo -e "${GREEN}🧪 Ejecutando test de Telegram...${NC}"
        python3 src/telegram_alerts.py
        ;;
    
    install)
        echo -e "${GREEN}📦 Instalando dependencias...${NC}"
        pip3 install -r requirements.txt
        ;;
    
    status)
        echo -e "${GREEN}📊 Últimos resultados:${NC}"
        python3 src/view_results.py
        ;;
    
    *)
        show_help
        ;;
esac
