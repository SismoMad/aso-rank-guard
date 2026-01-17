#!/bin/bash
# =============================================================================
# ASO Rank Guard - Quick Start para Migración a Supabase
# =============================================================================
# Este script te guía paso a paso en la migración
# =============================================================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         ASO Rank Guard - Migración a Supabase                ║
║         Quick Start Guide                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${BLUE}Este script te guiará en 5 pasos para migrar tu sistema a Supabase.${NC}"
echo ""

# -----------------------------------------------------------------------------
# PASO 1: Verificar archivos
# -----------------------------------------------------------------------------
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASO 1: Verificar archivos necesarios${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

FILES_OK=true

# Verificar archivos Python
if [ -f "src/supabase_client.py" ]; then
    echo -e "${GREEN}✅ src/supabase_client.py${NC}"
else
    echo -e "${RED}❌ src/supabase_client.py (FALTA)${NC}"
    FILES_OK=false
fi

if [ -f "src/rank_tracker_supabase.py" ]; then
    echo -e "${GREEN}✅ src/rank_tracker_supabase.py${NC}"
else
    echo -e "${RED}❌ src/rank_tracker_supabase.py (FALTA)${NC}"
    FILES_OK=false
fi

if [ -f "src/supabase_alerts.py" ]; then
    echo -e "${GREEN}✅ src/supabase_alerts.py${NC}"
else
    echo -e "${RED}❌ src/supabase_alerts.py (FALTA)${NC}"
    FILES_OK=false
fi

# Verificar configuración
if [ -f ".env.example" ]; then
    echo -e "${GREEN}✅ .env.example${NC}"
else
    echo -e "${RED}❌ .env.example (FALTA)${NC}"
    FILES_OK=false
fi

if [ -f "requirements-supabase.txt" ]; then
    echo -e "${GREEN}✅ requirements-supabase.txt${NC}"
else
    echo -e "${RED}❌ requirements-supabase.txt (FALTA)${NC}"
    FILES_OK=false
fi

if [ ! "$FILES_OK" = true ]; then
    echo ""
    echo -e "${RED}⚠️  Faltan archivos necesarios. Ejecuta primero:${NC}"
    echo "   Copilot: 'Crea los archivos de migración a Supabase'"
    exit 1
fi

echo ""
read -p "Presiona ENTER para continuar..."

# -----------------------------------------------------------------------------
# PASO 2: Instalación
# -----------------------------------------------------------------------------
clear
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASO 2: Instalación de dependencias${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ ! -f "setup_supabase.sh" ]; then
    echo -e "${RED}❌ setup_supabase.sh no encontrado${NC}"
    exit 1
fi

echo -e "${YELLOW}¿Quieres ejecutar el script de instalación automática?${NC}"
echo ""
echo "Esto hará:"
echo "  1. Crear virtual environment (venv)"
echo "  2. Instalar dependencias Python"
echo "  3. Crear archivo .env desde .env.example"
echo "  4. Verificar conexión a Supabase"
echo ""
read -p "Ejecutar setup? (s/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo ""
    bash setup_supabase.sh
else
    echo -e "${YELLOW}⚠️  Saltando instalación automática${NC}"
    echo ""
    echo "Ejecuta manualmente:"
    echo "  ./setup_supabase.sh"
    echo ""
fi

read -p "Presiona ENTER para continuar..."

# -----------------------------------------------------------------------------
# PASO 3: Configurar credenciales
# -----------------------------------------------------------------------------
clear
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASO 3: Configurar credenciales de Supabase${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Archivo .env no existe${NC}"
    echo ""
    echo "Crea el archivo .env:"
    echo "  cp .env.example .env"
    echo ""
fi

echo -e "${BLUE}📋 Obtén tus credenciales de Supabase:${NC}"
echo ""
echo "1. Ve a tu proyecto en Supabase Dashboard:"
echo -e "   ${CYAN}https://app.supabase.com/project/YOUR_PROJECT/settings/api${NC}"
echo ""
echo "2. Copia estos valores al archivo .env:"
echo ""
echo "   ${YELLOW}SUPABASE_URL${NC} = Project URL"
echo "   ${YELLOW}SUPABASE_ANON_KEY${NC} = anon / public (clave pública)"
echo "   ${YELLOW}SUPABASE_SERVICE_ROLE_KEY${NC} = service_role (⚠️ SECRETA)"
echo ""
echo "3. Configura también:"
echo "   ${YELLOW}TELEGRAM_BOT_TOKEN${NC} = Token de @BotFather"
echo "   ${YELLOW}ADMIN_EMAIL${NC} = Tu email de admin"
echo ""

read -p "¿Quieres editar .env ahora? (s/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    else
        echo "Abre .env con tu editor favorito"
        open -a TextEdit .env 2>/dev/null || echo "Edita manualmente: .env"
    fi
else
    echo -e "${YELLOW}⚠️  Recuerda editar .env antes de continuar${NC}"
fi

echo ""
read -p "Presiona ENTER para continuar..."

# -----------------------------------------------------------------------------
# PASO 4: Crear usuario en Supabase
# -----------------------------------------------------------------------------
clear
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASO 4: Crear usuario en Supabase Dashboard${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}📋 Crear tu usuario admin:${NC}"
echo ""
echo "1. Ve a Authentication en Supabase:"
echo -e "   ${CYAN}https://app.supabase.com/project/YOUR_PROJECT/auth/users${NC}"
echo ""
echo "2. Click en ${YELLOW}\"Add user\"${NC} → ${YELLOW}\"Create new user\"${NC}"
echo ""
echo "3. Completa:"
echo "   Email: ${YELLOW}(el mismo que pusiste en ADMIN_EMAIL)${NC}"
echo "   Password: ${YELLOW}(genera una segura)${NC}"
echo ""
echo "4. Click en ${YELLOW}\"Create user\"${NC}"
echo ""
echo "Esto automáticamente:"
echo "  ✅ Crea usuario en auth.users"
echo "  ✅ Trigger crea perfil en public.profiles"
echo ""

read -p "Presiona ENTER cuando hayas creado el usuario..."

# -----------------------------------------------------------------------------
# PASO 5: Migrar datos
# -----------------------------------------------------------------------------
clear
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASO 5: Migrar datos CSV a Supabase${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ ! -f "supabase/scripts/migrate_csv_to_postgres.py" ]; then
    echo -e "${YELLOW}⚠️  Script de migración no encontrado${NC}"
    echo ""
    echo "El script debería estar en:"
    echo "  supabase/scripts/migrate_csv_to_postgres.py"
    echo ""
    read -p "Presiona ENTER para continuar sin migrar datos..."
else
    echo -e "${BLUE}📊 Migrar rankings de CSV a PostgreSQL${NC}"
    echo ""
    
    if [ -f "data/ranks.csv" ]; then
        LINES=$(wc -l < data/ranks.csv)
        echo "Se encontró data/ranks.csv con ${GREEN}${LINES} líneas${NC}"
    else
        echo -e "${YELLOW}⚠️  No se encontró data/ranks.csv${NC}"
    fi
    
    echo ""
    read -p "¿Ejecutar migración de datos? (s/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo ""
        source venv/bin/activate 2>/dev/null || true
        
        # Cargar email de admin
        if [ -f ".env" ]; then
            export $(cat .env | grep ADMIN_EMAIL | xargs)
        fi
        
        if [ -z "$ADMIN_EMAIL" ]; then
            read -p "Email del usuario admin: " ADMIN_EMAIL
        fi
        
        echo ""
        echo -e "${BLUE}Ejecutando migración...${NC}"
        python3 supabase/scripts/migrate_csv_to_postgres.py --email "$ADMIN_EMAIL"
    else
        echo -e "${YELLOW}⚠️  Migración omitida${NC}"
    fi
fi

echo ""
read -p "Presiona ENTER para ver el resumen final..."

# -----------------------------------------------------------------------------
# RESUMEN FINAL
# -----------------------------------------------------------------------------
clear
echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         ✅ MIGRACIÓN A SUPABASE COMPLETADA                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${GREEN}🎉 ¡Todo listo! Ahora puedes usar el nuevo sistema.${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 PRÓXIMOS PASOS:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "1️⃣  Prueba el tracker con Supabase:"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}python3 src/rank_tracker_supabase.py${NC}"
echo ""

echo "2️⃣  Prueba el sistema de alertas (modo test):"
echo -e "   ${YELLOW}TEST_MODE=true python3 src/supabase_alerts.py${NC}"
echo ""

echo "3️⃣  Verifica tus datos en Supabase Dashboard:"
echo -e "   ${CYAN}https://app.supabase.com/project/YOUR_PROJECT/editor${NC}"
echo ""

echo "4️⃣  Lee la documentación completa:"
echo -e "   ${YELLOW}cat README_SUPABASE.md${NC}"
echo -e "   ${YELLOW}cat docs/ARQUITECTURA_SUPABASE.md${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✨ ¡Disfruta de tu sistema ASO multi-usuario con Supabase!${NC}"
echo ""
