#!/bin/bash
# Script para actualizar dashboard con datos frescos
# Ejecutar diariamente con cron

set -e  # Salir si hay error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🔄 $(date): Iniciando actualización de dashboard..."

# 1. Tracking de rankings (genera ranks.csv actualizado)
echo "📊 Rastreando rankings..."
python3 src/rank_tracker.py

# 2. Análisis PRO (genera competitors, discoveries, patterns)
echo "🔍 Analizando competidores y descubrimientos..."
python3 src/aso_expert_pro.py

# 3. Generar dashboard HTML
echo "🎨 Generando dashboard..."
python3 -c "
from src.dashboard_generator import InteractiveDashboard
import yaml

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

dash = InteractiveDashboard(config)
html = dash.generate_html()

with open('web/dashboard-interactive.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ Dashboard generado')
"

# 4. Subir a servidor (opcional, comenta si no quieres auto-deploy)
echo "📤 Desplegando en servidor..."
scp -o StrictHostKeyChecking=no web/dashboard-interactive.html root@194.164.160.111:/var/www/aso-rank-guard/index.html
ssh -o StrictHostKeyChecking=no root@194.164.160.111 'chmod 644 /var/www/aso-rank-guard/index.html && restorecon -v /var/www/aso-rank-guard/index.html'

echo "✅ $(date): Dashboard actualizado y desplegado"
echo "🌐 http://194.164.160.111/"
