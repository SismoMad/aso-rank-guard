#!/bin/bash
# Script de Auditoría de Seguridad - ASO Rank Guard
# Detecta y reporta problemas de seguridad críticos

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  🔒 ${YELLOW}ASO RANK GUARD${NC} - Auditoría de Seguridad      ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

ISSUES_FOUND=0

# 1. Verificar que .env NO esté en Git
echo -e "${BLUE}[1/7]${NC} Verificando que .env no esté trackeado en Git..."
if git ls-files | grep -q "^\.env$"; then
    echo -e "${RED}❌ CRÍTICO: .env está trackeado en Git!${NC}"
    echo -e "   ${YELLOW}Solución:${NC} git rm --cached .env && git commit -m 'Remove .env from git'"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ .env no está en Git${NC}"
fi

# 2. Verificar archivos HTML con credenciales hardcodeadas
echo ""
echo -e "${BLUE}[2/7]${NC} Buscando credenciales hardcodeadas en archivos HTML..."
if grep -r "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" web/*.html 2>/dev/null; then
    echo -e "${RED}❌ CRÍTICO: Claves Supabase hardcodeadas en HTML!${NC}"
    echo -e "   ${YELLOW}Archivos afectados:${NC}"
    grep -l "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" web/*.html | sed 's/^/     - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ No se encontraron claves en HTML${NC}"
fi

# 3. Verificar claves en scripts bash
echo ""
echo -e "${BLUE}[3/7]${NC} Buscando credenciales en scripts bash..."
if grep -r "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" scripts/*.sh 2>/dev/null | grep -v ".env"; then
    echo -e "${RED}❌ ADVERTENCIA: Posibles claves en scripts bash${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ Scripts bash limpios${NC}"
fi

# 4. Verificar que SERVICE_ROLE_KEY no esté en web-app/
echo ""
echo -e "${BLUE}[4/7]${NC} Verificando que SERVICE_ROLE_KEY no esté en frontend..."
if grep -r "SERVICE_ROLE_KEY" web-app/app web-app/components web-app/lib 2>/dev/null | grep -v "NEXT_PUBLIC"; then
    echo -e "${RED}❌ CRÍTICO: SERVICE_ROLE_KEY en código frontend!${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ Frontend solo usa ANON_KEY${NC}"
fi

# 5. Verificar que .gitignore incluya .env
echo ""
echo -e "${BLUE}[5/7]${NC} Verificando .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo -e "${GREEN}✅ .env está en .gitignore${NC}"
else
    echo -e "${RED}❌ CRÍTICO: .env NO está en .gitignore!${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 6. Verificar permisos de archivos sensibles
echo ""
echo -e "${BLUE}[6/7]${NC} Verificando permisos de archivos sensibles..."
for file in .env config/config.yaml; do
    if [ -f "$file" ]; then
        PERMS=$(stat -f "%Lp" "$file" 2>/dev/null || stat -c "%a" "$file" 2>/dev/null)
        if [ "$PERMS" != "600" ] && [ "$PERMS" != "400" ]; then
            echo -e "${YELLOW}⚠️  $file tiene permisos $PERMS (recomendado: 600)${NC}"
            echo -e "   ${YELLOW}Solución:${NC} chmod 600 $file"
        else
            echo -e "${GREEN}✅ $file tiene permisos seguros ($PERMS)${NC}"
        fi
    fi
done

# 7. Buscar claves en el historial de Git (últimos 10 commits)
echo ""
echo -e "${BLUE}[7/7]${NC} Buscando claves en historial de Git (últimos 10 commits)..."
if git log --all --oneline -n 10 -p | grep -i "service_role_key.*eyJ" > /dev/null 2>&1; then
    echo -e "${RED}❌ CRÍTICO: Claves encontradas en historial de Git!${NC}"
    echo -e "   ${YELLOW}Solución:${NC} Usar git filter-repo o BFG Repo Cleaner para limpiar historial"
    echo -e "   ${YELLOW}Ver:${NC} scripts/fix-security-breach.sh"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ Historial reciente limpio${NC}"
fi

# Resumen
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ TODOS LOS CHECKS PASARON${NC}"
    echo -e "   Tu repositorio está seguro 🔒"
else
    echo -e "${RED}❌ SE ENCONTRARON $ISSUES_FOUND PROBLEMAS DE SEGURIDAD${NC}"
    echo ""
    echo -e "${YELLOW}ACCIONES RECOMENDADAS:${NC}"
    echo -e "  1. Revisar y corregir los problemas listados arriba"
    echo -e "  2. Rotar las claves expuestas en Supabase"
    echo -e "  3. Si hay claves en Git, ejecutar: ./scripts/fix-security-breach.sh"
    echo -e "  4. Volver a ejecutar este script para verificar"
fi
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

exit $ISSUES_FOUND
