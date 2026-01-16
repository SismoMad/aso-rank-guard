#!/usr/bin/env python3
"""Test de alertas y envío a Telegram"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from auto_notifier import AutoNotifier
from telegram_alerts import AlertManager
import yaml

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

print('🔍 Detectando alertas...')
print()

notifier = AutoNotifier(config)
alerts = notifier.check_for_alerts()

if alerts:
    print(f'✅ {len(alerts)} alertas detectadas!')
    print()
    
    message = notifier.format_alert_message(alerts)
    print('📱 Mensaje que se enviará a Telegram:')
    print('='*60)
    print(message)
    print('='*60)
    print()
    
    print('📤 Enviando a Telegram...')
    telegram = AlertManager(config)
    success = telegram.send_telegram_message(message)
    
    if success:
        print('✅ ¡MENSAJE ENVIADO A TELEGRAM!')
        print('   🔔 Revisa tu Telegram ahora 📱')
    else:
        print('❌ Error enviando a Telegram')
else:
    print('ℹ️ No se detectaron alertas')
