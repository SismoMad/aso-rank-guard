#!/usr/bin/env python3
"""
Daily Summary - Resumen diario de cambios menores
Envía un resumen consolidado de alertas MEDIUM y LOW
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from typing import List, Dict
import yaml

logger = logging.getLogger(__name__)


class DailySummaryManager:
    """Gestor de resúmenes diarios"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.enabled = self.config.get('alerts', {}).get('daily_summary', {}).get('enabled', True)
        self.min_changes = self.config.get('alerts', {}).get('daily_summary', {}).get('min_changes', 3)
        
        if not self.enabled:
            logger.info("ℹ️ Daily summary deshabilitado")
    
    def should_send_summary(self) -> bool:
        """El resumen mejorado se envía siempre (no requiere mínimo de cambios)"""
        if not self.enabled:
            return False
        
        # El nuevo formato siempre es útil porque muestra TOP keywords
        return True
    
    def generate_summary(self) -> str:
        """Generar mensaje de resumen diario mejorado"""
        try:
            import sys
            from pathlib import Path
            import pandas as pd
            
            # Añadir src al path
            sys.path.insert(0, str(Path(__file__).parent))
            
            from auto_notifier import AutoNotifier
            from smart_alerts import SmartAlertEngine, SmartAlert, AlertPriority
            
            notifier = AutoNotifier(self.config)
            alerts = notifier.check_for_alerts()
            
            # Reconstruir TODAS las alertas (para estadísticas)
            all_smart_alerts = []
            for alert_dict in alerts:
                alert = SmartAlert(
                    alert_dict['type'],
                    alert_dict['keyword'],
                    alert_dict.get('country', 'US'),
                    alert_dict['prev_rank'],
                    alert_dict['current_rank'],
                    alert_dict['diff']
                )
                alert.priority = AlertPriority(alert_dict['priority'])
                all_smart_alerts.append(alert)
            
            # Obtener rankings actuales de todas las keywords
            ranks_file = self.config.get('storage', {}).get('ranks_file', 'data/ranks.csv')
            df = pd.read_csv(ranks_file)
            df['date'] = pd.to_datetime(df['date'])
            df['date_only'] = df['date'].dt.date
            
            # Último día
            latest_day = sorted(df['date_only'].unique())[-1]
            df_latest = df[df['date_only'] == latest_day]
            
            # Lista de todos los rankings actuales
            all_current_ranks = []
            for _, row in df_latest.iterrows():
                all_current_ranks.append({
                    'keyword': row['keyword'],
                    'rank': row['rank'],
                    'country': row['country']
                })
            
            # Formatear con smart engine (versión mejorada)
            engine = SmartAlertEngine(self.config)
            summary = engine.format_enhanced_daily_summary(all_current_ranks, all_smart_alerts)
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generando daily summary: {e}", exc_info=True)
            return None
    
    def send_summary(self):
        """Generar y enviar resumen diario por Telegram"""
        if not self.should_send_summary():
            logger.info("No hay suficientes cambios para enviar resumen diario")
            return
        
        summary = self.generate_summary()
        
        if not summary:
            logger.info("No se pudo generar resumen")
            return
        
        try:
            from telegram_alerts import AlertManager
            
            telegram = AlertManager(self.config)
            success = telegram.send_telegram_message(summary)
            
            if success:
                logger.info("✅ Resumen diario enviado por Telegram")
            else:
                logger.error("❌ Error enviando resumen diario")
        
        except Exception as e:
            logger.error(f"Error enviando resumen: {e}")


def main():
    """Test del daily summary"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    manager = DailySummaryManager()
    
    print("🧪 Testing Daily Summary Manager\n")
    
    if manager.should_send_summary():
        print("✅ Hay suficientes cambios para enviar resumen")
        summary = manager.generate_summary()
        if summary:
            print("\n📱 Resumen generado:\n")
            print(summary)
        else:
            print("❌ Error generando resumen")
    else:
        print("ℹ️ No hay suficientes cambios para resumen diario")


if __name__ == "__main__":
    main()
