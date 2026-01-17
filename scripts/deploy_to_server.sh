#!/bin/bash
# Deploy ASO Rank Guard PRO Dashboard to Server
# Usage: ./deploy_to_server.sh

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración del servidor
SERVER_IP="194.164.160.111"
SERVER_USER="root"
REMOTE_PATH="/var/www/aso-rank-guard"

echo -e "${BLUE}┌────────────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│${NC}  🚀 ${GREEN}ASO RANK GUARD PRO${NC} - Deploy to Server          ${BLUE}│${NC}"
echo -e "${BLUE}└────────────────────────────────────────────────────────────┘${NC}"
echo ""

# Verificar que el dashboard existe
if [ ! -f "web/dashboard-interactive.html" ]; then
    echo -e "${RED}❌ Dashboard no encontrado${NC}"
    echo "Genera primero el dashboard: ./pro.sh run"
    exit 1
fi

echo -e "${YELLOW}📊 Archivos a desplegar:${NC}"
echo "  • web/dashboard-interactive.html (Dashboard PRO)"
echo "  • data/ranks.csv (Rankings)"
echo "  • data/competitors.csv (Competidores)"
echo "  • data/keyword_discoveries.csv (Discoveries)"
echo ""

read -p "¿Continuar con el deploy? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deploy cancelado"
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 Desplegando archivos...${NC}"

# 1. Copiar dashboard principal como dashboard.html (el que sirve nginx)
echo -e "${BLUE}1.${NC} Copiando dashboard..."
scp web/dashboard-interactive.html ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/dashboard.html

# 2. Copiar datos necesarios
echo -e "${BLUE}2.${NC} Copiando datos..."
ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_PATH}/data"

if [ -f "data/ranks.csv" ]; then
    scp data/ranks.csv ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/data/
fi

if [ -f "data/competitors.csv" ]; then
    scp data/competitors.csv ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/data/
fi

if [ -f "data/keyword_discoveries.csv" ]; then
    scp data/keyword_discoveries.csv ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/data/
fi

if [ -f "data/ab_experiments.json" ]; then
    scp data/ab_experiments.json ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/data/
fi

if [ -f "data/seasonal_patterns.json" ]; then
    scp data/seasonal_patterns.json ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/data/
fi

# 3. Ajustar permisos
echo -e "${BLUE}3.${NC} Ajustando permisos..."
ssh ${SERVER_USER}@${SERVER_IP} "chmod 644 ${REMOTE_PATH}/dashboard.html ${REMOTE_PATH}/data/*.{csv,json} 2>/dev/null || true"

echo ""
echo -e "${GREEN}✅ Deploy completado!${NC}"
echo ""
echo -e "${YELLOW}Accede al dashboard en:${NC}"
echo "  🌐 http://${SERVER_IP}/"
echo ""
echo -e "${YELLOW}Nota:${NC} El dashboard ahora tiene todas las PRO features:"
echo "  • Rankings Overview"
echo "  • Competitors Analysis"
echo "  • Keyword Discoveries"
echo "  • Cost Analysis"
echo "  • Seasonal Patterns"
echo "  • A/B Testing"
echo ""
