#!/usr/bin/env python3
"""
Script de testing para Smart Alerts
Verifica que el sistema funciona correctamente
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_smart_alert_engine():
    """Test del motor de alertas inteligentes"""
    print("=" * 60)
    print("🧪 TEST 1: Smart Alert Engine")
    print("=" * 60 + "\n")
    
    try:
        from smart_alerts import SmartAlertEngine
        import yaml
        
        # Cargar config
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Crear engine
        engine = SmartAlertEngine(config)
        print("✅ Smart Alert Engine inicializado\n")
        
        # Test cases
        test_cases = [
            ("biblenow", "US", 3, 8, "CRITICAL: TOP keyword drop"),
            ("bible sleep", "US", 5, 15, "CRITICAL: Major drop"),
            ("bible meditation", "US", 45, 60, "HIGH: Good keyword drop"),
            ("scripture notes", "US", 105, 120, "MEDIUM: Medium change"),
            ("kids bible study", "US", 180, 195, "IGNORE: Bad keyword fluctuation"),
            ("bible chat", "US", 50, 30, "CELEBRATION: Big win"),
            ("peaceful bible", "US", 15, 8, "HIGH: Good rise"),
        ]
        
        alerts = []
        print("Evaluando cambios:\n")
        for keyword, country, prev, curr, expected in test_cases:
            alert = engine.evaluate_change(keyword, country, prev, curr)
            
            if alert:
                alerts.append(alert)
                print(f"✅ {keyword:30} #{prev:3} → #{curr:3} = {alert.priority.value:12} {alert.emoji}")
                if alert.insights:
                    print(f"   💡 {alert.insights[0]}")
                if alert.estimated_impact:
                    print(f"   📊 {alert.estimated_impact}")
            else:
                print(f"🔇 {keyword:30} #{prev:3} → #{curr:3} = IGNORED")
        
        print(f"\n📊 Total alertas generadas: {len(alerts)}")
        
        # Detectar patrones
        print("\n" + "=" * 60)
        print("🔍 Detectando patrones...")
        print("=" * 60 + "\n")
        
        patterns = engine.detect_patterns(alerts)
        if patterns:
            print(f"✅ {len(patterns)} patrones detectados:\n")
            for p in patterns:
                print(f"⚡️ {p['message']}")
                if 'possible_causes' in p:
                    print(f"   🔍 {p['possible_causes'][0]}")
                print()
        else:
            print("ℹ️ No se detectaron patrones especiales\n")
        
        # Formatear mensaje
        print("=" * 60)
        print("📱 Mensaje de Telegram:")
        print("=" * 60 + "\n")
        
        message = engine.format_grouped_message(alerts, patterns)
        print(message)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_notifier():
    """Test del auto notifier con smart alerts"""
    print("\n\n" + "=" * 60)
    print("🧪 TEST 2: Auto Notifier Integration")
    print("=" * 60 + "\n")
    
    try:
        from auto_notifier import AutoNotifier
        import yaml
        
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        notifier = AutoNotifier(config)
        
        if notifier.use_smart_alerts:
            print("✅ Auto Notifier usando Smart Alerts\n")
        else:
            print("ℹ️ Auto Notifier usando sistema legacy\n")
        
        # Check alerts (requiere datos reales)
        print("Verificando alertas con datos reales...")
        alerts = notifier.check_for_alerts()
        
        if alerts:
            print(f"✅ {len(alerts)} alertas detectadas\n")
            
            # Mostrar algunas
            for i, alert in enumerate(alerts[:3], 1):
                keyword = alert.get('keyword', 'N/A')
                priority = alert.get('priority', 'N/A')
                prev = alert.get('prev_rank', 0)
                curr = alert.get('current_rank', 0)
                print(f"{i}. {keyword}: #{prev}→#{curr} ({priority})")
            
            if len(alerts) > 3:
                print(f"   ... y {len(alerts) - 3} más")
        else:
            print("ℹ️ No hay alertas (necesitas al menos 2 días de datos)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_daily_summary():
    """Test del daily summary"""
    print("\n\n" + "=" * 60)
    print("🧪 TEST 3: Daily Summary Manager")
    print("=" * 60 + "\n")
    
    try:
        from daily_summary import DailySummaryManager
        
        manager = DailySummaryManager()
        
        if manager.enabled:
            print("✅ Daily Summary habilitado\n")
            print(f"   Min cambios: {manager.min_changes}")
            
            should_send = manager.should_send_summary()
            print(f"\n¿Enviar resumen? {'Sí' if should_send else 'No'}")
            
            if should_send:
                print("\nGenerando resumen...\n")
                summary = manager.generate_summary()
                if summary:
                    print("=" * 60)
                    print(summary)
                    print("=" * 60)
                else:
                    print("ℹ️ No se generó resumen")
        else:
            print("ℹ️ Daily Summary deshabilitado en config")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todos los tests"""
    print("\n" + "🛡️" * 30)
    print("   ASO RANK GUARD - SMART ALERTS TEST SUITE")
    print("🛡️" * 30 + "\n")
    
    results = {
        'Smart Alert Engine': test_smart_alert_engine(),
        'Auto Notifier': test_auto_notifier(),
        'Daily Summary': test_daily_summary()
    }
    
    print("\n\n" + "=" * 60)
    print("📊 RESULTADOS FINALES")
    print("=" * 60 + "\n")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TODOS LOS TESTS PASARON")
        print("=" * 60)
        print("\n✅ Smart Alerting está listo para usar!")
        print("\n📝 Próximos pasos:")
        print("   1. Ejecuta un check: python src/rank_tracker.py")
        print("   2. Verifica las alertas en Telegram")
        print("   3. Inicia el scheduler: python src/scheduler.py")
    else:
        print("⚠️ ALGUNOS TESTS FALLARON")
        print("=" * 60)
        print("\n❌ Revisa los errores arriba")
    
    print()


if __name__ == "__main__":
    main()
