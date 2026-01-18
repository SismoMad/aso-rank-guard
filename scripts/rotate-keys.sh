#!/bin/bash
# Script para Rotar Claves de Supabase (POST-BREACH)
# Úsalo DESPUÉS de exponer claves accidentalmente

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║${NC}  🚨 ${YELLOW}ROTACIÓN DE CLAVES SUPABASE${NC} (Post-Breach)      ${RED}║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}⚠️  Este script te guiará para rotar tus claves de Supabase${NC}"
echo -e "${YELLOW}    después de una exposición accidental.${NC}"
echo ""
echo -e "${RED}IMPORTANTE:${NC} Este proceso invalidará TODAS las claves antiguas."
echo -e "             Actualiza TODOS los servicios que usen estas claves."
echo ""

read -p "¿Estás seguro de continuar? (escribe 'SI' para confirmar): " CONFIRM
if [ "$CONFIRM" != "SI" ]; then
    echo "Operación cancelada."
    exit 0
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PASO 1: Rotar claves en Supabase Dashboard${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Ve a: https://app.supabase.com/project/_/settings/api"
echo "2. En la sección 'Project API keys', haz clic en 'Reset':"
echo "   - Reset 'anon' (public) key"
echo "   - Reset 'service_role' (secret) key"
echo ""
echo "3. COPIA LAS NUEVAS CLAVES:"
echo ""

read -p "Presiona ENTER cuando hayas copiado las nuevas claves..."

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PASO 2: Actualizar .env local${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""
echo "Pega las nuevas claves en .env:"
echo ""

# Backup del .env actual
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo -e "${GREEN}✅ Backup de .env creado${NC}"

# Pedir nueva ANON_KEY
echo ""
read -p "Nueva SUPABASE_ANON_KEY: " NEW_ANON_KEY

# Pedir nueva SERVICE_ROLE_KEY
echo ""
read -p "Nueva SUPABASE_SERVICE_ROLE_KEY: " NEW_SERVICE_KEY

# Actualizar .env
if [ -f ".env" ]; then
    # Usar perl en macOS porque sed funciona diferente
    if [[ "$OSTYPE" == "darwin"* ]]; then
        perl -i -pe "s|SUPABASE_ANON_KEY=.*|SUPABASE_ANON_KEY=$NEW_ANON_KEY|g" .env
        perl -i -pe "s|SUPABASE_SERVICE_ROLE_KEY=.*|SUPABASE_SERVICE_ROLE_KEY=$NEW_SERVICE_KEY|g" .env
        perl -i -pe "s|NEXT_PUBLIC_SUPABASE_ANON_KEY=.*|NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEW_ANON_KEY|g" .env
    else
        sed -i "s|SUPABASE_ANON_KEY=.*|SUPABASE_ANON_KEY=$NEW_ANON_KEY|g" .env
        sed -i "s|SUPABASE_SERVICE_ROLE_KEY=.*|SUPABASE_SERVICE_ROLE_KEY=$NEW_SERVICE_KEY|g" .env
        sed -i "s|NEXT_PUBLIC_SUPABASE_ANON_KEY=.*|NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEW_ANON_KEY|g" .env
    fi
    echo -e "${GREEN}✅ .env actualizado${NC}"
fi

# Actualizar web-app/.env.local si existe
if [ -f "web-app/.env.local" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        perl -i -pe "s|NEXT_PUBLIC_SUPABASE_ANON_KEY=.*|NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEW_ANON_KEY|g" web-app/.env.local
    else
        sed -i "s|NEXT_PUBLIC_SUPABASE_ANON_KEY=.*|NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEW_ANON_KEY|g" web-app/.env.local
    fi
    echo -e "${GREEN}✅ web-app/.env.local actualizado${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PASO 3: Actualizar servidor de producción${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""
echo "Actualiza las claves en el servidor:"
echo ""
echo "ssh root@194.164.160.111 << 'EOF'"
echo "cd /root/aso-rank-guard"
echo "perl -i -pe 's|NEXT_PUBLIC_SUPABASE_ANON_KEY=.*|NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEW_ANON_KEY|g' web-app/.env.production"
echo "pm2 restart nextjs-app"
echo "EOF"
echo ""

read -p "¿Actualizar servidor ahora? (y/n): " UPDATE_SERVER
if [ "$UPDATE_SERVER" == "y" ]; then
    ssh -o StrictHostKeyChecking=no root@194.164.160.111 << EOF
cd /root/aso-rank-guard
cp web-app/.env.production web-app/.env.production.backup.\$(date +%Y%m%d_%H%M%S)
perl -i -pe "s|NEXT_PUBLIC_SUPABASE_ANON_KEY=.*|NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEW_ANON_KEY|g" web-app/.env.production
pm2 restart nextjs-app
pm2 save
EOF
    echo -e "${GREEN}✅ Servidor actualizado y reiniciado${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PASO 4: Limpiar historial de Git (OPCIONAL pero recomendado)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""
echo "Si las claves antiguas están en el historial de Git:"
echo ""
echo "1. Instalar BFG Repo Cleaner:"
echo "   brew install bfg"
echo ""
echo "2. Crear archivo con claves antiguas a eliminar:"
echo "   echo 'ANTIGUA_CLAVE_AQUI' > passwords.txt"
echo ""
echo "3. Ejecutar BFG:"
echo "   bfg --replace-text passwords.txt"
echo ""
echo "4. Limpiar y forzar push:"
echo "   git reflog expire --expire=now --all"
echo "   git gc --prune=now --aggressive"
echo "   git push --force"
echo ""
echo -e "${RED}⚠️  ADVERTENCIA: git push --force reescribe el historial!${NC}"
echo -e "${RED}    Solo hazlo si estás seguro.${NC}"
echo ""

read -p "¿Limpiar historial de Git ahora? (y/n): " CLEAN_GIT
if [ "$CLEAN_GIT" == "y" ]; then
    echo ""
    echo "Ejecuta manualmente los comandos de arriba."
    echo "No lo haré automáticamente por seguridad."
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ ROTACIÓN DE CLAVES COMPLETADA${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}CHECKLIST POST-ROTACIÓN:${NC}"
echo "  [ ] Nuevas claves en .env local"
echo "  [ ] Nuevas claves en servidor de producción"
echo "  [ ] Aplicación Next.js reiniciada"
echo "  [ ] Historial de Git limpio (si aplicable)"
echo "  [ ] Todas las aplicaciones funcionando con nuevas claves"
echo ""
echo -e "${YELLOW}BACKUPS CREADOS:${NC}"
ls -lh .env.backup.* 2>/dev/null || echo "  (ninguno)"
echo ""
echo -e "${BLUE}💡 TIP:${NC} Ejecuta ./scripts/security-audit.sh para verificar"
echo ""
