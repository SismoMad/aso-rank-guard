#!/bin/bash

# =============================================================================
# Script de Actualización Rápida (Quick Deploy)
# Solo actualiza código sin reinstalar dependencias
# =============================================================================

set -e

VPS_HOST="194.164.160.111"
VPS_USER="root"
VPS_DIR="/var/www/aso-rank-guard"
LOCAL_DIR="/Users/javi/aso-rank-guard"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Quick Deploy - Solo actualizando código...${NC}\n"

# 1. Sincronizar solo archivos de código
echo -e "${YELLOW}➤ Sincronizando código...${NC}"
rsync -avz --progress \
    --exclude 'node_modules' \
    --exclude '.next' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'venv' \
    --exclude '.git' \
    --exclude 'data' \
    --exclude 'logs' \
    --exclude '.env' \
    --exclude '.env.local' \
    --exclude '.env.production' \
    --include 'src/' \
    --include 'api/' \
    --include 'web-app/app/' \
    --include 'web-app/components/' \
    --include 'web-app/lib/' \
    ${LOCAL_DIR}/ \
    ${VPS_USER}@${VPS_HOST}:${VPS_DIR}/

# 2. Rebuild Next.js y reiniciar PM2
echo -e "\n${YELLOW}➤ Rebuilding Next.js y reiniciando servicios...${NC}"
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /var/www/aso-rank-guard/web-app
npm run build

# Reiniciar PM2
pm2 restart all

echo "✓ Servicios reiniciados"
ENDSSH

# 3. Verificar estado
echo -e "\n${YELLOW}➤ Estado de servicios:${NC}"
ssh ${VPS_USER}@${VPS_HOST} "pm2 status"

echo -e "\n${GREEN}✓ Quick Deploy completado!${NC}"
echo -e "Ver logs: ${YELLOW}ssh ${VPS_USER}@${VPS_HOST} 'pm2 logs'${NC}\n"
