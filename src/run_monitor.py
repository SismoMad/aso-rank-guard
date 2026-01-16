#!/usr/bin/env python3
"""
Script completo de monitorización con integración de alertas
Combina tracking + alertas + análisis en un solo workflow
"""

import sys
import logging
import pandas as pd
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent))

from rank_tracker import RankTracker
from telegram_alerts import AlertManager
from report_formatter import ReportFormatter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Ejecutar workflow completo: track → analyze → alert"""
    
    try:
        logger.info("🚀 Iniciando ASO Rank Guard - Workflow completo")
        
        # 1. Inicializar componentes
        logger.info("📦 Cargando configuración...")
        tracker = RankTracker()
        alert_manager = AlertManager(tracker.config)
        formatter = ReportFormatter()
        
        # 2. Enviar mensaje de inicio a Telegram
        logger.info("📢 Enviando notificación de inicio...")
        alert_manager.send_telegram_message("🔄 *Tracking automático iniciado*\n\n⏳ Rastreando 83 keywords...\n_Esto tardará ~4 minutos_")
        
        # 3. Ejecutar tracking (con alertas automáticas integradas)
        logger.info("🔍 Ejecutando tracking de keywords...")
        report = tracker.run_daily_check()
        
        # 4. Generar y enviar reporte de tracking con TODAS las keywords
        logger.info("📊 Generando reporte completo de tracking...")
        
        # Cargar datos históricos
        ranks_file = Path(tracker.config['storage']['ranks_file'])
        df_all = pd.read_csv(ranks_file)
        df_all['date'] = pd.to_datetime(df_all['date'])
        df_all['date_only'] = df_all['date'].dt.date
        unique_dates = sorted(df_all['date_only'].unique())
        has_previous = len(unique_dates) > 1
        
        # Generar reporte con todas las keywords (igual que /track)
        message = formatter.format_tracking_report(
            df_results=report['results'],
            df_all=df_all,
            has_previous=has_previous
        )
        
        # Enviar reporte dividido si es necesario
        messages = formatter.split_long_message(message)
        for msg in messages:
            alert_manager.send_telegram_message(msg)
        
        logger.info("✅ Workflow completado exitosamente\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrumpido por usuario")
        return 1
    except Exception as e:
        logger.error(f"💥 Error en workflow: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
