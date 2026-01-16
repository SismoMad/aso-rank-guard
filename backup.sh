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
