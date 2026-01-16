#!/usr/bin/env python3
"""
Scheduler automático - Ejecuta checks en horarios configurados
Mantiene el proceso corriendo en background
"""

import schedule
import time
import logging
from datetime import datetime
import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent))

from run_monitor import main as run_monitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def scheduled_check():
    """Función que se ejecuta en cada check programado"""
    logger.info("=" * 60)
    logger.info(f"⏰ Check programado iniciado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        run_monitor()
        logger.info("✅ Check completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error en check programado: {e}", exc_info=True)
    
    logger.info("=" * 60 + "\n")


def send_daily_summary():
    """Enviar resumen diario de cambios menores"""
    logger.info("📊 Generando resumen diario...")
    
    try:
        from daily_summary import DailySummaryManager
        
        manager = DailySummaryManager()
        manager.send_summary()
    except Exception as e:
        logger.error(f"❌ Error enviando daily summary: {e}", exc_info=True)


def load_schedule_config():
    """Cargar configuración de horarios"""
    import yaml
    
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config['schedule']


def main():
    """Iniciar scheduler en background"""
    
    logger.info("🛡️  ASO Rank Guard - Scheduler iniciado")
    logger.info("=" * 60)
    
    try:
        # Cargar configuración
        schedule_config = load_schedule_config()
        daily_time = schedule_config['daily_check_time']
        
        # Programar check diario
        schedule.every().day.at(daily_time).do(scheduled_check)
        logger.info(f"📅 Check diario programado a las {daily_time}")
        
        # Programar daily summary (si está habilitado)
        import yaml
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if config.get('alerts', {}).get('daily_summary', {}).get('enabled', True):
            summary_time = config['alerts']['daily_summary'].get('time', '20:00')
            schedule.every().day.at(summary_time).do(send_daily_summary)
            logger.info(f"📊 Resumen diario programado a las {summary_time}")
        
        logger.info("⏳ Esperando próxima ejecución...")
        logger.info("   (Presiona Ctrl+C para detener)")
        logger.info("=" * 60 + "\n")
        
        # Opcional: ejecutar check inmediato al iniciar
        # logger.info("🚀 Ejecutando check inicial...")
        # scheduled_check()
        
        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check cada minuto si hay tareas pendientes
            
    except KeyboardInterrupt:
        logger.info("\n👋 Scheduler detenido por usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Error crítico en scheduler: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
