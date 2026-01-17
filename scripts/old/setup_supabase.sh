#!/bin/bash
# =============================================================================
# ASO Rank Guard - Setup Script para Migración a Supabase
# =============================================================================

set -e  # Exit on error

echo "🚀 ASO Rank Guard - Setup Supabase"
echo "===================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# 1. Verificar Python
# -----------------------------------------------------------------------------
echo -e "${BLUE}[1/6]${NC} Verificando Python..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION}${NC}"

# -----------------------------------------------------------------------------
# 2. Crear virtual environment
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}[2/6]${NC} Configurando virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment creado${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment ya existe${NC}"
fi

# Activar venv
source venv/bin/activate

# -----------------------------------------------------------------------------
# 3. Instalar dependencias
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}[3/6]${NC} Instalando dependencias..."

if [ -f "requirements-supabase.txt" ]; then
    pip install --upgrade pip -q
    pip install -r requirements-supabase.txt -q
    echo -e "${GREEN}✅ Dependencias instaladas${NC}"
else
    echo -e "${RED}❌ requirements-supabase.txt no encontrado${NC}"
    exit 1
fi

# -----------------------------------------------------------------------------
# 4. Configurar .env
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}[4/6]${NC} Configurando variables de entorno..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Archivo .env creado desde .env.example${NC}"
        echo -e "${YELLOW}    ⚡ IMPORTANTE: Edita .env con tus credenciales${NC}"
    else
        echo -e "${RED}❌ .env.example no encontrado${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Archivo .env ya existe${NC}"
fi

# -----------------------------------------------------------------------------
# 5. Verificar conexión a Supabase
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}[5/6]${NC} Verificando conexión a Supabase..."

# Cargar variables de .env
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Verificar que existan las variables
if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" = "https://xxxxxxxxxxxxx.supabase.co" ]; then
    echo -e "${YELLOW}⚠️  SUPABASE_URL no configurado${NC}"
    echo -e "${YELLOW}    Edita .env con tus credenciales antes de continuar${NC}"
else
    echo -e "${GREEN}✅ Variables de entorno configuradas${NC}"
    
    # Test de conexión con Python
    python3 -c "
from src.supabase_client import get_supabase_client
try:
    client = get_supabase_client(use_service_role=True)
    if client.health_check():
        print('${GREEN}✅ Conexión a Supabase exitosa${NC}')
    else:
        print('${RED}❌ No se pudo conectar a Supabase${NC}')
        exit(1)
except Exception as e:
    print(f'${RED}❌ Error: {e}${NC}')
    exit(1)
" || echo -e "${YELLOW}⚠️  No se pudo verificar conexión (revisa credenciales)${NC}"
fi

# -----------------------------------------------------------------------------
# 6. Crear directorios necesarios
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}[6/6]${NC} Creando directorios..."

mkdir -p logs
mkdir -p data/backups

echo -e "${GREEN}✅ Directorios creados${NC}"

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ SETUP COMPLETADO${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}📋 PRÓXIMOS PASOS:${NC}"
echo ""
echo "1️⃣  Edita .env con tus credenciales:"
echo "   nano .env"
echo ""
echo "2️⃣  Crea tu primer usuario en Supabase Dashboard:"
echo "   https://app.supabase.com/project/_/auth/users"
echo ""
echo "3️⃣  Migra datos CSV a Supabase:"
echo "   source venv/bin/activate"
echo "   python3 supabase/scripts/migrate_csv_to_postgres.py --email tu@email.com"
echo ""
echo "4️⃣  Prueba el tracker con Supabase:"
echo "   python3 src/rank_tracker_supabase.py"
echo ""
echo "5️⃣  Prueba el sistema de alertas:"
echo "   python3 src/supabase_alerts.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}📖 Documentación:${NC}"
echo "   - Arquitectura: docs/ARQUITECTURA_SUPABASE.md"
echo "   - Schema: supabase/SCHEMA_DESIGN.md"
echo "   - Migration Plan: supabase/MIGRATION_PLAN.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
