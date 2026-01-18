#!/bin/bash
# EMERGENCIA: Limpieza de claves expuestas

set -e

echo "🚨 LIMPIANDO CLAVES EXPUESTAS DE GITHUB..."

# 1. Eliminar archivo con service key hardcodeada
echo "🗑️  Eliminando deploy-to-vps.sh (tiene claves hardcodeadas)..."
git rm scripts/deployment/deploy-to-vps.sh
git rm scripts/deployment/deploy-server.sh 2>/dev/null || true

# 2. Eliminar otros archivos con claves
git rm deploy-server.sh 2>/dev/null || true

# 3. Asegurar que .env NUNCA se suba
echo "" >> .gitignore
echo "# NUNCA subir archivos con secrets" >> .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.production" >> .gitignore
echo "**/.env" >> .gitignore
echo "**/.env.*" >> .gitignore

echo "✅ Archivos eliminados"
echo ""
echo "⚠️  IMPORTANTE: Ahora debes:"
echo "1. Ir a Supabase y RESETEAR las API keys"
echo "2. Actualizar .env local con las NUEVAS keys"
echo "3. Commit y push estos cambios:"
echo ""
echo "   git add ."
echo "   git commit -m 'security: remove exposed secrets'"
echo "   git push origin main"
echo ""
echo "4. Después, limpia el historial de Git (BFG Repo-Cleaner):"
echo "   brew install bfg"
echo "   bfg --replace-text secrets.txt"
echo ""
