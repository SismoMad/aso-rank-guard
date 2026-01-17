#!/bin/bash
# Script para configurar automatización en el servidor
# Ejecutar UNA VEZ desde tu Mac

set -e

SERVER="root@194.164.160.111"
REMOTE_PATH="/root/aso-rank-guard"

echo "🚀 Desplegando proyecto completo al servidor..."

# 1. Crear estructura en servidor
ssh $SERVER "mkdir -p $REMOTE_PATH/{src,config,data,logs,web,backups}"

# 2. Subir todo el código
echo "📦 Subiendo código fuente..."
scp -r src/* $SERVER:$REMOTE_PATH/src/
scp config/config.yaml $SERVER:$REMOTE_PATH/config/
scp requirements.txt $SERVER:$REMOTE_PATH/

# 3. Subir datos existentes
echo "📊 Subiendo datos históricos..."
scp data/*.csv $SERVER:$REMOTE_PATH/data/ 2>/dev/null || echo "No hay datos CSV todavía"

# 4. Crear script de actualización en servidor
echo "📝 Creando script de actualización remoto..."
ssh $SERVER 'cat > /root/aso-rank-guard/update_dashboard.sh << '\''EOF'\''
#!/bin/bash
# Script de actualización automática (servidor)
set -e

cd /root/aso-rank-guard

echo "🔄 $(date): Iniciando actualización..."

# Activar virtualenv si existe, o usar python3 global
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 1. Tracking de rankings
echo "📊 Rastreando rankings..."
python3 src/rank_tracker.py

# 2. Análisis PRO
echo "🔍 Analizando competidores..."
python3 src/aso_expert_pro.py

# 3. Generar dashboard
echo "🎨 Generando dashboard..."
python3 -c "
from src.dashboard_generator import InteractiveDashboard
import yaml

with open('\''config/config.yaml'\'') as f:
    config = yaml.safe_load(f)

dash = InteractiveDashboard(config)
html = dash.generate_html()

with open('\''web/dashboard-interactive.html'\'', '\''w'\'', encoding='\''utf-8'\'') as f:
    f.write(html)

print('\''✅ Dashboard generado'\'')
"

# 4. Copiar a /var/www
echo "📤 Actualizando dashboard público..."
cp web/dashboard-interactive.html /var/www/aso-rank-guard/index.html
chmod 644 /var/www/aso-rank-guard/index.html
restorecon -v /var/www/aso-rank-guard/index.html 2>/dev/null || true

echo "✅ $(date): Actualización completada"
echo "🌐 Dashboard disponible en http://194.164.160.111/"
EOF
'

# 5. Dar permisos de ejecución
ssh $SERVER "chmod +x $REMOTE_PATH/update_dashboard.sh"

# 6. Instalar dependencias en servidor
echo "📚 Instalando dependencias Python..."
ssh $SERVER "cd $REMOTE_PATH && python3 -m pip install -r requirements.txt --user"

# 7. Configurar cron en servidor
echo "⏰ Configurando cron en servidor..."
ssh $SERVER "(crontab -l 2>/dev/null | grep -v 'aso-rank-guard'; echo '0 17 * * * /root/aso-rank-guard/update_dashboard.sh >> /root/aso-rank-guard/logs/cron.log 2>&1') | crontab -"

# 8. Configurar alertas Telegram (scheduler) en servidor
echo "📱 Configurando alertas Telegram..."
ssh $SERVER "(crontab -l 2>/dev/null | grep -v 'scheduler.py'; echo '0 16 * * * cd /root/aso-rank-guard && python3 src/scheduler.py >> /root/aso-rank-guard/logs/alerts.log 2>&1') | crontab -"

echo ""
echo "✅ ========================================="
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "✅ ========================================="
echo ""
echo "🤖 El servidor ahora ejecuta automáticamente:"
echo "   • 16:00 - Alertas Telegram (scheduler.py)"
echo "   • 17:00 - Actualización Dashboard"
echo ""
echo "📋 Para verificar:"
echo "   ssh $SERVER 'crontab -l'"
echo ""
echo "📊 Para ver logs:"
echo "   ssh $SERVER 'tail -f /root/aso-rank-guard/logs/cron.log'"
echo "   ssh $SERVER 'tail -f /root/aso-rank-guard/logs/alerts.log'"
echo ""
echo "🧪 Para ejecutar manualmente:"
echo "   ssh $SERVER '/root/aso-rank-guard/update_dashboard.sh'"
echo ""
