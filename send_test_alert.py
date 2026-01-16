#!/usr/bin/env python3
"""Enviar alerta de test directamente a Telegram"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from telegram_alerts import AlertManager
import yaml

# Cargar config
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Mensaje de test simulando smart alerts
message = """🔔 *SMART ALERTS* (TEST)
📅 15/01/2026 20:45

🚨 *CRÍTICO* (acción inmediata)
🚨 *bible sleep* (US)
   #5 → #19 (-14)
   📊 Impacto: ~700 impresiones/día
   💡 Keyword TOP perdiendo visibilidad crítica
   ✅ 1. Revisa reviews últimas 24-48h
   ✅ 2. Verifica metadata sigue optimizada

🚨 *bible sleep stories* (US)
   #6 → #16 (-10)
   📊 Impacto: ~500 impresiones/día
   💡 Keyword TOP perdiendo visibilidad crítica
   ✅ 1. Revisa reviews últimas 24-48h

🚨 *bedtime bible stories* (US)
   #10 → #21 (-11)
   📊 Impacto: ~550 impresiones/día
   💡 ⚠️ SALIÓ DEL TOP 10
   ✅ 1. Revisa reviews últimas 24-48h

🎉 *CELEBREMOS*
🎉 *bible for sleep* (US)
   #50 → #31 (+19)
   📊 Impacto: +950 impresiones/día
   💡 Subida excepcional, capitalizar ahora
   ✅ 1. Asegúrate que keyword está en TITLE

_Total: 4 alertas | ✅ Smart Alerting funcionando_"""

print("📤 Enviando mensaje de TEST a Telegram...\n")
print("="*60)
print(message)
print("="*60)
print()

telegram = AlertManager(config)
success = telegram.send_telegram_message(message)

if success:
    print("✅ ¡MENSAJE ENVIADO!")
    print("🔔 Revisa tu Telegram AHORA 📱")
    print()
    print("Este es un ejemplo de cómo se verán las Smart Alerts.")
    print("Mañana cuando ejecutes un check real, verás alertas así.")
else:
    print("❌ Error enviando mensaje")
    print("Verifica tu bot_token y chat_id en config.yaml")
