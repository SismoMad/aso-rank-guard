#!/bin/bash

# 🧹 Script para limpiar credenciales del historial de Git
# ⚠️ PELIGRO: Reescribe TODO el historial. Hacer backup antes.

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       🧹 LIMPIEZA DE CREDENCIALES DEL HISTORIAL GIT       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  ADVERTENCIA: Este proceso:"
echo "   • Reescribe TODO el historial de commits"
echo "   • Requiere force push (reescribe origin)"
echo "   • Colaboradores necesitarán re-clonar el repo"
echo "   • No se puede deshacer fácilmente"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -d ".git" ]; then
    echo "❌ Error: No estás en un repositorio Git"
    exit 1
fi

# Verificar que no hay cambios sin commitear
if ! git diff-index --quiet HEAD --; then
    echo "❌ Error: Tienes cambios sin commitear"
    echo "   Ejecuta 'git stash' o 'git commit' primero"
    exit 1
fi

# Confirmar antes de proceder
echo "¿Estás SEGURO que quieres continuar? (escribe 'SI ESTOY SEGURO')"
read -r confirmation

if [ "$confirmation" != "SI ESTOY SEGURO" ]; then
    echo "❌ Cancelado. No se realizaron cambios."
    exit 0
fi

echo ""
echo "📋 Paso 1/6: Creando backup del repositorio..."
BACKUP_DIR="../aso-rank-guard-backup-$(date +%Y%m%d_%H%M%S)"
cp -r . "$BACKUP_DIR"
echo "✅ Backup creado en: $BACKUP_DIR"

echo ""
echo "📋 Paso 2/6: Verificando herramientas necesarias..."

# Verificar git-filter-repo
if ! command -v git-filter-repo &> /dev/null; then
    echo "⚙️  Instalando git-filter-repo..."
    
    if command -v brew &> /dev/null; then
        brew install git-filter-repo
    elif command -v pip3 &> /dev/null; then
        pip3 install git-filter-repo
    else
        echo "❌ No se pudo instalar git-filter-repo"
        echo "   Instala manualmente: https://github.com/newren/git-filter-repo"
        exit 1
    fi
fi

echo "✅ git-filter-repo disponible"

echo ""
echo "📋 Paso 3/6: Creando lista de secretos a eliminar..."

# Crear archivo temporal con patrones a buscar
SECRETS_FILE="/tmp/git-secrets-$(date +%s).txt"

cat > "$SECRETS_FILE" << 'EOF'
# Supabase keys conocidas (reemplazar con regex)
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwNTQ1OTksImV4cCI6MjA1MjYzMDU5OX0.SnJvVF7nz8k1OI-1UY-FMUvUJD_qW8gZNEbpP_4Xy6Q
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzA1NDU5OSwiZXhwIjoyMDUyNjMwNTk5fQ.yWn-8-EuE4K8xd0UZQrRY9TVLtjsb5S5Pl4AqDNnUZs
EOF

echo "✅ Lista de secretos creada"
echo ""
echo "🔍 Secretos que se eliminarán:"
cat "$SECRETS_FILE" | grep -v '^#' | sed 's/^/   • /'

echo ""
echo "📋 Paso 4/6: Buscando commits afectados..."

AFFECTED_COMMITS=$(git log --all --source -S "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" --oneline | wc -l)
echo "📊 Encontrados $AFFECTED_COMMITS commits con credenciales"

if [ "$AFFECTED_COMMITS" -eq 0 ]; then
    echo "✅ No se encontraron credenciales en el historial"
    rm "$SECRETS_FILE"
    exit 0
fi

echo ""
echo "📋 Commits afectados:"
git log --all --source -S "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" --oneline | sed 's/^/   • /'

echo ""
echo "📋 Paso 5/6: Limpiando historial con git-filter-repo..."
echo "⏳ Esto puede tardar varios minutos..."
echo ""

# Opción 1: Eliminar archivos completos que contenían secretos
echo "🗑️  Eliminando archivos que expusieron credenciales..."

git-filter-repo --force --invert-paths \
    --path scripts/deployment/deploy-server.sh \
    --path scripts/deployment/deploy-to-vps.sh \
    2>&1 | grep -v "^Parsed" || true

# Opción 2: Reemplazar secretos en archivos que queremos mantener
echo ""
echo "🔄 Reemplazando secretos en archivos restantes..."

# Crear expresiones de reemplazo
cat > /tmp/replacements.txt << 'EOF'
regex:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+==>***REMOVED_JWT_TOKEN***
regex:NEXT_PUBLIC_SUPABASE_ANON_KEY=[A-Za-z0-9._-]+==>NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
regex:SUPABASE_SERVICE_ROLE_KEY=[A-Za-z0-9._-]+==>SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
EOF

git-filter-repo --force --replace-text /tmp/replacements.txt 2>&1 | grep -v "^Parsed" || true

echo "✅ Historial limpiado"

# Limpiar archivos temporales
rm -f "$SECRETS_FILE" /tmp/replacements.txt

echo ""
echo "📋 Paso 6/6: Forzando garbage collection..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ LIMPIEZA COMPLETADA                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Estadísticas:"
echo "   • Commits originales: $(git -C "$BACKUP_DIR" rev-list --count HEAD)"
echo "   • Commits después de limpieza: $(git rev-list --count HEAD)"
echo "   • Backup guardado en: $BACKUP_DIR"
echo ""
echo "⚠️  SIGUIENTE PASO CRÍTICO:"
echo ""
echo "   Para aplicar los cambios al servidor remoto:"
echo ""
echo "   git remote add origin-clean <tu-repo-url>  # Si no tienes remote"
echo "   git push origin-clean --force --all"
echo "   git push origin-clean --force --tags"
echo ""
echo "   ⚠️  ADVERTENCIA: Esto REESCRIBIRÁ el repositorio remoto"
echo "   ⚠️  Todos los colaboradores deberán RE-CLONAR el repositorio"
echo ""
echo "📧 Notifica a tu equipo ANTES de hacer force push:"
echo ""
echo "   Asunto: [URGENTE] Reescritura de historial Git - Re-clonar necesario"
echo "   "
echo "   Hola equipo,"
echo "   "
echo "   He limpiado credenciales expuestas del historial de Git."
echo "   TODOS deben:"
echo "   1. Hacer backup de su trabajo local (git stash / commits)"
echo "   2. Eliminar su copia local"
echo "   3. Re-clonar desde GitHub"
echo "   4. Aplicar sus cambios locales"
echo "   "
echo "   Fecha de force push: $(date)"
echo ""
echo "🔒 DESPUÉS del force push:"
echo "   1. Verifica que las credenciales no están en GitHub"
echo "   2. Rota TODAS las claves expuestas en Supabase"
echo "   3. Ejecuta ./scripts/rotate-keys.sh"
echo "   4. Monitorea logs de accesos sospechosos"
echo ""
echo "💾 Restaurar si algo sale mal:"
echo "   cd .."
echo "   rm -rf aso-rank-guard"
echo "   mv $BACKUP_DIR aso-rank-guard"
echo ""

# Verificar que se limpiaron las credenciales
echo "🔍 Verificación final..."
if git log --all -S "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpZHF4eWRyeWJwdXd5c2tyYXJoIg" --oneline | grep -q .; then
    echo "⚠️  ADVERTENCIA: Todavía se encontraron algunas credenciales"
    echo "   Revisa manualmente con:"
    echo "   git log --all -S 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' -p"
else
    echo "✅ Verificación exitosa: No se encontraron credenciales"
fi

echo ""
echo "¿Continuar con force push a origin? (escribe 'PUSH' para continuar)"
read -r push_confirm

if [ "$push_confirm" = "PUSH" ]; then
    echo "🚀 Haciendo force push..."
    git push origin --force --all
    git push origin --force --tags
    echo "✅ Force push completado"
    echo ""
    echo "🎉 ¡Todo listo! Ahora rota las claves en Supabase:"
    echo "   ./scripts/rotate-keys.sh"
else
    echo "⏸️  Force push cancelado. Puedes hacerlo manualmente cuando estés listo:"
    echo "   git push origin --force --all"
    echo "   git push origin --force --tags"
fi
