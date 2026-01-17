#!/bin/bash

# Script para configurar automatización del tracking diario
# Uso: ./setup_automation.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}🤖 Configurador de Automatización - ASO Rank Guard${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Elige el método de automatización:"
echo ""
echo "  1) Scheduler integrado (RECOMENDADO)"
echo "     ✓ Fácil de usar"
echo "     ✓ Se mantiene corriendo"
echo "     ✓ Logs automáticos"
echo ""
echo "  2) Launchd (macOS permanente)"
echo "     ✓ Se inicia con el Mac"
echo "     ✓ Reinicio automático si falla"
echo "     ✓ Configuración permanente"
echo ""
echo "  3) Cron (tradicional)"
echo "     ✓ Compatible con cualquier Unix"
echo "     ✓ Configuración simple"
echo ""
echo "  4) Solo mostrar comandos (sin configurar)"
echo ""
echo "  0) Salir"
echo ""

read -p "Selecciona una opción [1-4]: " option

case $option in
    1)
        echo ""
        echo -e "${GREEN}━━━ Opción 1: Scheduler Integrado ━━━${NC}"
        echo ""
        
        # Verificar si ya está corriendo
        if pgrep -f "scheduler.py" > /dev/null; then
            echo -e "${YELLOW}⚠️  El scheduler ya está corriendo${NC}"
            read -p "¿Quieres reiniciarlo? (s/n): " restart
            if [ "$restart" = "s" ]; then
                pkill -f scheduler.py
                sleep 1
            else
                exit 0
            fi
        fi
        
        # Mostrar hora configurada
        CURRENT_TIME=$(grep "daily_check_time:" config/config.yaml | awk '{print $2}' | tr -d '"')
        echo -e "Hora actual configurada: ${BLUE}$CURRENT_TIME${NC}"
        echo ""
        
        read -p "¿Iniciar scheduler en background? (s/n): " start
        if [ "$start" = "s" ]; then
            nohup ./run.sh schedule > logs/scheduler_output.log 2>&1 &
            sleep 2
            
            if pgrep -f "scheduler.py" > /dev/null; then
                echo ""
                echo -e "${GREEN}✅ Scheduler iniciado correctamente${NC}"
                echo ""
                echo "📝 Comandos útiles:"
                echo "  Ver estado:  ps aux | grep scheduler"
                echo "  Ver logs:    tail -f logs/scheduler.log"
                echo "  Detener:     pkill -f scheduler.py"
                echo ""
                echo -e "${BLUE}🎉 El tracking se ejecutará automáticamente a las $CURRENT_TIME${NC}"
            else
                echo -e "${RED}❌ Error al iniciar el scheduler${NC}"
                echo "Revisa los logs: tail logs/scheduler_output.log"
            fi
        fi
        ;;
    
    2)
        echo ""
        echo -e "${GREEN}━━━ Opción 2: Launchd (macOS) ━━━${NC}"
        echo ""
        
        PLIST_FILE="$HOME/Library/LaunchAgents/com.biblenow.rankguard.plist"
        
        if [ -f "$PLIST_FILE" ]; then
            echo -e "${YELLOW}⚠️  Ya existe una configuración de Launchd${NC}"
            read -p "¿Quieres sobrescribirla? (s/n): " overwrite
            if [ "$overwrite" != "s" ]; then
                exit 0
            fi
            launchctl unload "$PLIST_FILE" 2>/dev/null
        fi
        
        # Crear plist
        cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.biblenow.rankguard</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/venv/bin/python3</string>
        <string>$SCRIPT_DIR/src/rank_tracker.py</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/launchd.log</string>
    
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/launchd_error.log</string>
    
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF
        
        # Activar
        launchctl load "$PLIST_FILE"
        
        echo ""
        echo -e "${GREEN}✅ Launchd configurado correctamente${NC}"
        echo ""
        echo "📝 Comandos útiles:"
        echo "  Ver estado:     launchctl list | grep rankguard"
        echo "  Ver logs:       tail -f logs/launchd.log"
        echo "  Desactivar:     launchctl unload $PLIST_FILE"
        echo ""
        echo -e "${BLUE}🎉 El tracking se ejecutará automáticamente a las 9:00 AM todos los días${NC}"
        ;;
    
    3)
        echo ""
        echo -e "${GREEN}━━━ Opción 3: Cron ━━━${NC}"
        echo ""
        echo "Añade esta línea a tu crontab:"
        echo ""
        echo -e "${BLUE}0 9 * * * cd $SCRIPT_DIR && source venv/bin/activate && python3 src/rank_tracker.py >> logs/cron.log 2>&1${NC}"
        echo ""
        read -p "¿Quieres abrir el editor de crontab ahora? (s/n): " edit
        if [ "$edit" = "s" ]; then
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Copia la línea de arriba en el editor que se abrirá"
            echo "Guarda y cierra (Ctrl+X, luego Y, luego Enter)"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            sleep 3
            EDITOR=nano crontab -e
        fi
        ;;
    
    4)
        echo ""
        echo -e "${BLUE}━━━ Comandos de Automatización ━━━${NC}"
        echo ""
        echo -e "${YELLOW}Scheduler integrado:${NC}"
        echo "  nohup ./run.sh schedule > logs/scheduler_output.log 2>&1 &"
        echo ""
        echo -e "${YELLOW}Ver procesos:${NC}"
        echo "  ps aux | grep scheduler"
        echo "  ps aux | grep rank_tracker"
        echo ""
        echo -e "${YELLOW}Detener:${NC}"
        echo "  pkill -f scheduler.py"
        echo "  pkill -f rank_tracker.py"
        echo ""
        echo -e "${YELLOW}Ver logs:${NC}"
        echo "  tail -f logs/scheduler.log"
        echo "  tail -f logs/rank_guard.log"
        echo ""
        ;;
    
    0)
        echo "Saliendo..."
        exit 0
        ;;
    
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
