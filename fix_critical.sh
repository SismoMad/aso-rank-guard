#!/bin/bash
# Script para arreglar bugs críticos (2 horas)
# Ejecutar: chmod +x fix_critical.sh && ./fix_critical.sh

set -e

echo "🔧 ASO Rank Guard - Fix Critical Issues"
echo "========================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Eliminar keywords duplicadas
echo -e "${YELLOW}[1/8]${NC} Limpiando keywords duplicadas..."
python3 << 'EOF'
import yaml
with open('config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

before = len(config['keywords'])
config['keywords'] = sorted(list(set(config['keywords'])))
after = len(config['keywords'])

with open('config/config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print(f"✅ Eliminados {before - after} duplicados ({before} → {after} keywords)")
EOF

# 2. Crear .gitignore para credenciales
echo -e "${YELLOW}[2/8]${NC} Protegiendo credenciales..."
if ! grep -q "config/config.yaml" .gitignore 2>/dev/null; then
    echo "config/config.yaml" >> .gitignore
    echo "config/credentials.json" >> .gitignore
    echo "config/token.json" >> .gitignore
    echo "*.log" >> .gitignore
    echo ".env" >> .gitignore
    echo -e "${GREEN}✅ .gitignore actualizado${NC}"
else
    echo -e "${GREEN}✅ .gitignore ya configurado${NC}"
fi

# 3. Crear template de configuración
echo -e "${YELLOW}[3/8]${NC} Creando config template..."
cp config/config.yaml config/config.yaml.example
python3 << 'EOF'
import yaml
with open('config/config.yaml.example', 'r') as f:
    config = yaml.safe_load(f)

# Ofuscar credenciales
config['alerts']['telegram']['bot_token'] = "YOUR_BOT_TOKEN_HERE"
config['alerts']['telegram']['chat_id'] = "YOUR_CHAT_ID_HERE"

with open('config/config.yaml.example', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print("✅ Template creado en config/config.yaml.example")
EOF

# 4. Crear .env template
echo -e "${YELLOW}[4/8]${NC} Creando .env template..."
cat > .env.example << 'EOL'
# ASO Rank Guard - Environment Variables
# Copia este archivo a .env y rellena con tus credenciales

# Telegram Bot
BOT_TOKEN=8531462519:AAFvX5PPyB177DUzylwgC8LMIUztrWPYfbI
CHAT_ID=722751828

# Server (si usas autenticación HTTP)
HTTP_USERNAME=asoguard
HTTP_PASSWORD=BibleNow2026

# OpenAI (opcional)
OPENAI_API_KEY=

# Google Trends (opcional)
GOOGLE_TRENDS_REGION=US
EOL
echo -e "${GREEN}✅ .env.example creado${NC}"

# 5. Crear favicon
echo -e "${YELLOW}[5/8]${NC} Creando favicon..."
cat > web/favicon.svg << 'EOL'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#1a1a2e" rx="15"/>
  <text x="50" y="75" text-anchor="middle" font-size="60" fill="#00d4ff">📊</text>
</svg>
EOL
echo -e "${GREEN}✅ Favicon creado${NC}"

# 6. Crear health check endpoint
echo -e "${YELLOW}[6/8]${NC} Añadiendo health check a API..."
if ! grep -q "def health_check" src/api.py; then
    cat >> src/api.py << 'EOL'

@app.get("/health")
async def health_check():
    """Health check endpoint para monitoring"""
    try:
        # Verificar que hay datos
        df = pd.read_csv('data/ranks.csv')
        last_update = df['date'].max() if len(df) > 0 else None
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "keywords_tracked": len(df['keyword'].unique()) if len(df) > 0 else 0,
            "last_update": str(last_update) if last_update else "No data",
            "uptime_seconds": time.time() - start_time
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }
EOL
    echo -e "${GREEN}✅ Health check añadido${NC}"
else
    echo -e "${GREEN}✅ Health check ya existe${NC}"
fi

# 7. Crear script de backup
echo -e "${YELLOW}[7/8]${NC} Creando script de backup..."
cat > backup.sh << 'EOL'
#!/bin/bash
# Backup automático de ASO Rank Guard

BACKUP_DIR="$HOME/aso-backups"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/Users/javi/aso-rank-guard"

mkdir -p "$BACKUP_DIR"

# Backup de datos
tar -czf "$BACKUP_DIR/aso_data_$DATE.tar.gz" \
    -C "$PROJECT_DIR" \
    data/ \
    config/config.yaml \
    logs/

# Mantener solo últimos 7 backups
cd "$BACKUP_DIR"
ls -t | tail -n +8 | xargs -r rm

echo "✅ Backup completado: aso_data_$DATE.tar.gz"
echo "📁 Backups totales: $(ls -1 | wc -l)"
EOL
chmod +x backup.sh
echo -e "${GREEN}✅ Script backup.sh creado${NC}"
echo "   Ejecuta: ./backup.sh"
echo "   O añade a cron: 0 2 * * * $(pwd)/backup.sh"

# 8. Resumen final
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ FIXES CRÍTICOS COMPLETADOS${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "✅ Keywords duplicadas eliminadas"
echo "✅ .gitignore configurado"
echo "✅ Config template creado"
echo "✅ .env template creado"
echo "✅ Favicon generado"
echo "✅ Health check añadido"
echo "✅ Script de backup listo"
echo ""
echo -e "${YELLOW}📋 PRÓXIMOS PASOS MANUALES:${NC}"
echo ""
echo "1. REGENERAR BOT DE TELEGRAM (urgente):"
echo "   - Abre @BotFather en Telegram"
echo "   - Envía: /revoke"
echo "   - Copia el NUEVO token"
echo "   - Actualiza config/config.yaml"
echo ""
echo "2. CONFIGURAR HTTPS (recomendado):"
echo "   - ssh root@194.164.160.111"
echo "   - certbot --nginx"
echo ""
echo "3. GIT COMMIT:"
echo "   - git rm --cached config/config.yaml"
echo "   - git add .gitignore config/config.yaml.example"
echo "   - git commit -m 'Security: Remove credentials from git'"
echo ""
echo "4. CONFIGURAR BACKUPS AUTOMÁTICOS:"
echo "   - crontab -e"
echo "   - Añadir: 0 2 * * * $(pwd)/backup.sh"
echo ""
echo "5. MONITORING:"
echo "   - Registrarse en uptimerobot.com (gratis)"
echo "   - Monitorear: http://194.164.160.111:8447/health"
echo ""
echo -e "${GREEN}🎉 Tu proyecto está mucho más seguro ahora!${NC}"
echo ""
