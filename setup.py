#!/usr/bin/env python3
"""
Setup interactivo - Configurar ASO Rank Guard paso a paso
"""

import sys
import yaml
from pathlib import Path


def print_header(title):
    """Mostrar header bonito"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def print_step(number, title):
    """Mostrar número de paso"""
    print(f"\n📍 Paso {number}: {title}")
    print("-" * 60)


def get_input(prompt, default=None):
    """Obtener input del usuario con default opcional"""
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    else:
        while True:
            response = input(f"{prompt}: ").strip()
            if response:
                return response
            print("⚠️  Este campo es obligatorio")


def confirm(prompt):
    """Confirmar sí/no"""
    response = input(f"{prompt} (s/n): ").strip().lower()
    return response in ['s', 'si', 'sí', 'y', 'yes']


def setup_wizard():
    """Wizard de configuración interactivo"""
    
    print_header("🛡️  ASO RANK GUARD - Setup Wizard")
    
    print("Bienvenido al asistente de configuración de ASO Rank Guard")
    print("Vamos a configurar tu herramienta en 5 minutos.\n")
    
    config = {}
    
    # ===== 1. APP CONFIGURATION =====
    print_step(1, "Configuración de tu App")
    
    config['app'] = {}
    config['app']['id'] = int(get_input(
        "App ID de tu app en App Store",
        "6749528117"  # BibleNow
    ))
    config['app']['name'] = get_input(
        "Nombre de tu app",
        "Audio Bible Stories & Chat"
    )
    config['app']['bundle_id'] = get_input(
        "Bundle ID (opcional)",
        "com.biblenow.app"
    )
    
    # ===== 2. KEYWORDS =====
    print_step(2, "Keywords a monitorizar")
    
    print("\nEjemplos de keywords:")
    print("  - audio bible stories")
    print("  - christian bedtime prayer")
    print("  - cuentos biblicos audio")
    print("\n💡 Recomendamos 10-20 keywords máximo\n")
    
    config['keywords'] = []
    
    if confirm("¿Quieres usar keywords por defecto para BibleNow?"):
        config['keywords'] = [
            "audio bible stories",
            "christian bedtime prayer",
            "bible chat ai",
            "sleep bible stories",
            "bible stories for sleep",
            "cuentos biblicos audio",
            "oracion para dormir cristiana"
        ]
    else:
        print("\nIngresa keywords uno por uno (escribe 'fin' cuando termines):")
        while True:
            kw = input(f"Keyword #{len(config['keywords']) + 1}: ").strip()
            if kw.lower() == 'fin':
                break
            if kw:
                config['keywords'].append(kw)
        
        if not config['keywords']:
            print("⚠️  Usando keywords por defecto")
            config['keywords'] = ["audio bible stories", "bible chat ai"]
    
    print(f"\n✅ {len(config['keywords'])} keywords configurados")
    
    # ===== 3. COUNTRIES =====
    print_step(3, "Países a monitorizar")
    
    print("\nCódigos de país (ISO 3166-1):")
    print("  ES - España")
    print("  US - Estados Unidos")
    print("  MX - México")
    print("  AR - Argentina")
    print("  CO - Colombia")
    print("  etc.\n")
    
    countries_input = get_input(
        "Países separados por comas (ej: ES,US,MX)",
        "ES,US"
    )
    config['countries'] = [c.strip().upper() for c in countries_input.split(',')]
    
    print(f"✅ Monitorizando en: {', '.join(config['countries'])}")
    
    # ===== 4. TELEGRAM ALERTS =====
    print_step(4, "Alertas de Telegram")
    
    print("\nPara configurar Telegram:")
    print("1. Abre Telegram y busca @BotFather")
    print("2. Envía /newbot y sigue las instrucciones")
    print("3. Copia el BOT_TOKEN que te da")
    print("4. Busca @userinfobot y envía un mensaje para obtener tu CHAT_ID\n")
    
    if confirm("¿Quieres configurar Telegram ahora?"):
        bot_token = get_input("BOT_TOKEN de Telegram")
        chat_id = get_input("Tu CHAT_ID")
        
        config['alerts'] = {
            'drop_threshold': 5,
            'rise_threshold': 10,
            'telegram': {
                'enabled': True,
                'bot_token': bot_token,
                'chat_id': chat_id
            },
            'slack': {
                'enabled': False,
                'webhook_url': ''
            }
        }
    else:
        print("⚠️  Telegram no configurado. Podrás hacerlo después en config.yaml")
        config['alerts'] = {
            'drop_threshold': 5,
            'rise_threshold': 10,
            'telegram': {
                'enabled': False,
                'bot_token': 'TU_BOT_TOKEN_AQUI',
                'chat_id': 'TU_CHAT_ID_AQUI'
            },
            'slack': {
                'enabled': False,
                'webhook_url': ''
            }
        }
    
    # ===== 5. SCHEDULE =====
    print_step(5, "Horario de ejecución")
    
    daily_time = get_input(
        "Hora diaria para check (formato 24h, ej: 09:00)",
        "09:00"
    )
    
    config['schedule'] = {
        'daily_check_time': daily_time,
        'post_update_checks': [1, 6, 24, 72]
    }
    
    # ===== CONFIGURACIONES POR DEFECTO =====
    
    config['google_calendar'] = {
        'enabled': False,
        'credentials_file': 'config/credentials.json',
        'token_file': 'config/token.json',
        'calendar_id': 'primary',
        'update_keywords': ['app update', 'app-update', 'nueva version']
    }
    
    config['trends'] = {
        'google_trends': {
            'enabled': False,
            'region': 'US'
        },
        'ai_analysis': {
            'enabled': False,
            'api_key': '',
            'model': 'gpt-4o-mini'
        }
    }
    
    config['storage'] = {
        'ranks_file': 'data/ranks.csv',
        'log_file': 'logs/rank_guard.log',
        'retention_days': 90
    }
    
    config['api'] = {
        'itunes': {
            'base_url': 'https://itunes.apple.com/search',
            'limit': 250,
            'timeout': 10
        },
        'rate_limit': {
            'requests_per_minute': 20,
            'delay_between_requests': 3
        }
    }
    
    config['debug'] = {
        'enabled': False,
        'verbose_logs': False,
        'test_mode': False
    }
    
    # ===== GUARDAR CONFIGURACIÓN =====
    print_step(6, "Guardando configuración")
    
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Configuración guardada en: {config_path}")
    
    # ===== RESUMEN =====
    print_header("✅ Setup Completado")
    
    print("Resumen de tu configuración:\n")
    print(f"📱 App: {config['app']['name']} (ID: {config['app']['id']})")
    print(f"🔤 Keywords: {len(config['keywords'])} configurados")
    print(f"🌍 Países: {', '.join(config['countries'])}")
    print(f"🔔 Alertas Telegram: {'✅ Configurado' if config['alerts']['telegram']['enabled'] else '❌ No configurado'}")
    print(f"⏰ Check diario: {config['schedule']['daily_check_time']}")
    
    print("\n" + "=" * 60)
    print("🚀 Próximos pasos:")
    print("=" * 60 + "\n")
    
    print("1. Instalar dependencias:")
    print("   pip install -r requirements.txt\n")
    
    print("2. Hacer primer test:")
    print("   python src/rank_tracker.py\n")
    
    if config['alerts']['telegram']['enabled']:
        print("3. Verificar alertas Telegram:")
        print("   python src/telegram_alerts.py\n")
    
    print("4. Ejecutar scheduler automático:")
    print("   python src/scheduler.py")
    print("   (mantener corriendo en background)\n")
    
    print("O usar cron para ejecución diaria (ver README.md)\n")
    
    print("=" * 60)
    print("¡Listo! 🎉")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        setup_wizard()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelado por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error durante setup: {e}")
        sys.exit(1)
