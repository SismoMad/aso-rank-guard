#!/bin/bash

# =============================================================================
# Script de Monitoreo Remoto
# Ver estado del servidor sin conectarte por SSH
# =============================================================================

VPS_HOST="194.164.160.111"
VPS_USER="root"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ASO Rank Guard - Monitor VPS                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Estado de PM2
echo -e "${YELLOW}═══ Estado de PM2 ═══${NC}"
ssh ${VPS_USER}@${VPS_HOST} "pm2 status"

# 2. Recursos del sistema
echo -e "\n${YELLOW}═══ Recursos del Sistema ═══${NC}"
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
echo "CPU y RAM:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "  CPU: " 100 - $1"%"}'
free -h | awk 'NR==2{printf "  RAM: %s / %s (%.2f%%)\n", $3,$2,$3*100/$2 }'

echo ""
echo "Disco:"
df -h / | awk 'NR==2{printf "  Usado: %s / %s (%s)\n", $3,$2,$5}'
ENDSSH

# 3. Últimos logs (últimas 15 líneas)
echo -e "\n${YELLOW}═══ Últimos Logs API ═══${NC}"
ssh ${VPS_USER}@${VPS_HOST} "tail -n 15 /var/www/aso-rank-guard/logs/api-out.log 2>/dev/null || echo 'Sin logs disponibles'"

echo -e "\n${YELLOW}═══ Últimos Logs Web ═══${NC}"
ssh ${VPS_USER}@${VPS_HOST} "tail -n 15 /var/www/aso-rank-guard/logs/web-out.log 2>/dev/null || echo 'Sin logs disponibles'"

# 4. Health checks
echo -e "\n${YELLOW}═══ Health Checks ═══${NC}"

# API Health
if curl -f -s http://${VPS_HOST}/health > /dev/null 2>&1; then
    echo -e "  API:     ${GREEN}✓ OK${NC}"
else
    echo -e "  API:     ${RED}✗ FAIL${NC}"
fi

# Web Health
if curl -f -s http://${VPS_HOST}/ > /dev/null 2>&1; then
    echo -e "  Web:     ${GREEN}✓ OK${NC}"
else
    echo -e "  Web:     ${RED}✗ FAIL${NC}"
fi

# 5. Último tracking ejecutado
echo -e "\n${YELLOW}═══ Último Tracking ═══${NC}"
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
if [ -f /var/www/aso-rank-guard/logs/last_run_summary.txt ]; then
    echo "$(tail -n 10 /var/www/aso-rank-guard/logs/last_run_summary.txt)"
else
    echo "  No hay tracking reciente"
fi
ENDSSH

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "Para ver logs en tiempo real: ${YELLOW}ssh ${VPS_USER}@${VPS_HOST} 'pm2 logs'${NC}"
echo ""
