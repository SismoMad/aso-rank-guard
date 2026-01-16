#!/usr/bin/env python3
"""
ASO Rank Guard PRO - Monitor completo con todas las features
Ejecuta tracking + competidores + discoveries + patrones + dashboard
"""

import sys
import yaml
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rank_guard_pro.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """Cargar configuración"""
    try:
        with open('config/config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"❌ Error cargando config: {e}")
        sys.exit(1)


def run_pro_monitor():
    """Ejecutar monitoring completo PRO"""
    
    config = load_config()
    pro_config = config.get('pro_features', {})
    
    print("="*80)
    print("🚀 ASO RANK GUARD PRO - MONITORING COMPLETO")
    print("="*80)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    results = {}
    
    # ============================================================
    # 1. RANK TRACKING (core)
    # ============================================================
    print("\n" + "="*80)
    print("1️⃣  RANK TRACKING")
    print("="*80)
    
    try:
        from src.rank_tracker import RankTracker
        
        tracker = RankTracker('config/config.yaml')
        report = tracker.run_daily_check()
        
        results['ranks'] = {
            'status': 'success',
            'keywords_tracked': len(report['results']),
            'changes': len(report['changes'])
        }
        
        print(f"✅ Rankings actualizados: {len(report['results'])} checks")
        print(f"📊 Cambios detectados: {len(report['changes'])}")
        
    except Exception as e:
        logger.error(f"❌ Error en rank tracking: {e}")
        results['ranks'] = {'status': 'error', 'error': str(e)}
    
    # ============================================================
    # 2. COMPETITOR TRACKING
    # ============================================================
    if pro_config.get('competitor_tracking', {}).get('enabled'):
        print("\n" + "="*80)
        print("2️⃣  COMPETITOR TRACKING")
        print("="*80)
        
        try:
            from src.competitor_tracker import CompetitorTracker
            
            comp_tracker = CompetitorTracker(config)
            
            # Track solo top keywords para no saturar (primeras 10)
            top_keywords = config['keywords'][:10]
            comp_results = comp_tracker.track_all_competitors(
                keywords=top_keywords,
                countries=config['countries']
            )
            
            comp_tracker.save_results(comp_results)
            
            # Detectar cambios
            changes = comp_tracker.detect_competitor_changes()
            
            results['competitors'] = {
                'status': 'success',
                'competitors_tracked': len(comp_results),
                'changes': len(changes)
            }
            
            print(f"✅ Competidores rastreados: {len(comp_results)}")
            print(f"🔍 Cambios detectados: {len(changes)}")
            
            if changes:
                print("\nCambios importantes:")
                for change in changes[:5]:
                    print(f"  • {change['message']}")
            
        except Exception as e:
            logger.error(f"❌ Error en competitor tracking: {e}")
            results['competitors'] = {'status': 'error', 'error': str(e)}
    else:
        print("\n⏭️  Competitor tracking deshabilitado")
        results['competitors'] = {'status': 'skipped'}
    
    # ============================================================
    # 3. KEYWORD DISCOVERY
    # ============================================================
    if pro_config.get('keyword_discovery', {}).get('enabled'):
        print("\n" + "="*80)
        print("3️⃣  KEYWORD DISCOVERY")
        print("="*80)
        
        try:
            from src.keyword_discovery import KeywordDiscoveryEngine
            import pandas as pd
            
            discovery = KeywordDiscoveryEngine(config)
            
            # Pasar datos de competidores si existen
            comp_data = None
            if results['competitors'].get('status') == 'success':
                try:
                    comp_data = pd.read_csv('data/competitors.csv')
                except:
                    pass
            
            summary = discovery.run_full_discovery(competitor_data=comp_data)
            
            results['discovery'] = {
                'status': 'success',
                'total_discovered': summary['total_discovered'],
                'top_opportunities': len(summary['top_opportunities'])
            }
            
            print(f"✅ Keywords descubiertas: {summary['total_discovered']}")
            print(f"🎯 Top oportunidades: {len(summary['top_opportunities'])}")
            
            if summary['top_opportunities']:
                print("\nTop 5 oportunidades:")
                for opp in summary['top_opportunities'][:5]:
                    print(f"  • {opp['keyword']} (score: {opp['opportunity_score']}/100)")
            
        except Exception as e:
            logger.error(f"❌ Error en keyword discovery: {e}")
            results['discovery'] = {'status': 'error', 'error': str(e)}
    else:
        print("\n⏭️  Keyword discovery deshabilitado")
        results['discovery'] = {'status': 'skipped'}
    
    # ============================================================
    # 4. SEASONAL PATTERNS
    # ============================================================
    if pro_config.get('seasonal_analysis', {}).get('enabled'):
        print("\n" + "="*80)
        print("4️⃣  SEASONAL PATTERNS ANALYSIS")
        print("="*80)
        
        try:
            from src.seasonal_patterns import SeasonalPatternsDetector
            
            detector = SeasonalPatternsDetector(config)
            min_days = pro_config.get('seasonal_analysis', {}).get('min_history_days', 14)
            
            analysis = detector.analyze_all_keywords(min_history_days=min_days)
            
            if 'error' not in analysis:
                results['patterns'] = {
                    'status': 'success',
                    'keywords_analyzed': analysis['analyzed_keywords'],
                    'weekly_patterns': len(analysis['weekly_patterns']),
                    'monthly_patterns': len(analysis['monthly_patterns']),
                    'trends': len(analysis['trends'])
                }
                
                print(f"✅ Keywords analizadas: {analysis['analyzed_keywords']}")
                print(f"📆 Patrones semanales: {len(analysis['weekly_patterns'])}")
                print(f"📅 Patrones mensuales: {len(analysis['monthly_patterns'])}")
                print(f"📈 Tendencias: {len(analysis['trends'])}")
                
                # Mostrar tendencias destacadas
                if analysis['trends']:
                    improving = [t for t in analysis['trends'] if t['trend'] == 'improving']
                    if improving:
                        print(f"\n🟢 Mejorando: {len(improving)} keywords")
                        for t in improving[:3]:
                            print(f"  • {t['keyword']}: {t['description']}")
            else:
                results['patterns'] = {'status': 'error', 'error': analysis['error']}
                print(f"⚠️  {analysis['error']}")
                
        except Exception as e:
            logger.error(f"❌ Error en seasonal patterns: {e}")
            results['patterns'] = {'status': 'error', 'error': str(e)}
    else:
        print("\n⏭️  Seasonal analysis deshabilitado")
        results['patterns'] = {'status': 'skipped'}
    
    # ============================================================
    # 5. COST ANALYSIS
    # ============================================================
    if pro_config.get('cost_analysis', {}).get('enabled'):
        print("\n" + "="*80)
        print("5️⃣  COST & REVENUE ANALYSIS")
        print("="*80)
        
        try:
            from src.cost_calculator import CostCalculator
            import pandas as pd
            
            calculator = CostCalculator(config)
            
            # Cargar rankings
            ranks_df = pd.read_csv('data/ranks.csv')
            ranks_df['date'] = pd.to_datetime(ranks_df['date'])
            
            # Estimar volúmenes (simplificado - puedes mejorar esto)
            volume_estimates = {}
            for keyword in config['keywords']:
                # Volumen basado en longitud (simplificado)
                word_count = len(keyword.split())
                if word_count >= 5:
                    volume = 20
                elif word_count == 4:
                    volume = 50
                elif word_count == 3:
                    volume = 150
                else:
                    volume = 300
                volume_estimates[keyword] = volume
            
            portfolio = calculator.estimate_total_portfolio_value(ranks_df, volume_estimates)
            
            results['costs'] = {
                'status': 'success',
                'monthly_revenue': portfolio['total_monthly_revenue'],
                'yearly_revenue': portfolio['total_yearly_revenue'],
                'daily_impressions': portfolio['total_daily_impressions']
            }
            
            print(f"✅ Portfolio analizado")
            print(f"💵 Revenue mensual estimado: ${portfolio['total_monthly_revenue']:,.2f}")
            print(f"📅 Revenue anual estimado: ${portfolio['total_yearly_revenue']:,.2f}")
            print(f"👁️  Impresiones diarias: {portfolio['total_daily_impressions']:,}")
            
            if portfolio['top_revenue_keywords']:
                print("\nTop 3 keywords más valiosas:")
                for kw in portfolio['top_revenue_keywords'][:3]:
                    print(f"  • {kw['keyword']}: ${kw['monthly_revenue']:.2f}/mes")
            
        except Exception as e:
            logger.error(f"❌ Error en cost analysis: {e}")
            results['costs'] = {'status': 'error', 'error': str(e)}
    else:
        print("\n⏭️  Cost analysis deshabilitado")
        results['costs'] = {'status': 'skipped'}
    
    # ============================================================
    # 6. GENERATE DASHBOARD
    # ============================================================
    if pro_config.get('dashboard', {}).get('enabled'):
        print("\n" + "="*80)
        print("6️⃣  INTERACTIVE DASHBOARD")
        print("="*80)
        
        try:
            from src.dashboard_generator import InteractiveDashboard
            
            dashboard = InteractiveDashboard(config)
            file_path = dashboard.save_dashboard()
            
            if file_path:
                results['dashboard'] = {
                    'status': 'success',
                    'file_path': file_path
                }
                
                print(f"✅ Dashboard generado")
                print(f"📊 Abre en tu navegador: file://{Path(file_path).absolute()}")
            else:
                results['dashboard'] = {'status': 'error', 'error': 'Failed to generate'}
                
        except Exception as e:
            logger.error(f"❌ Error generando dashboard: {e}")
            results['dashboard'] = {'status': 'error', 'error': str(e)}
    else:
        print("\n⏭️  Dashboard generation deshabilitado")
        results['dashboard'] = {'status': 'skipped'}
    
    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    print("\n" + "="*80)
    print("📊 RESUMEN FINAL")
    print("="*80)
    
    success_count = sum(1 for r in results.values() if r.get('status') == 'success')
    error_count = sum(1 for r in results.values() if r.get('status') == 'error')
    skipped_count = sum(1 for r in results.values() if r.get('status') == 'skipped')
    
    print(f"\n✅ Exitosos: {success_count}")
    print(f"❌ Errores: {error_count}")
    print(f"⏭️  Omitidos: {skipped_count}")
    
    # Guardar resumen
    summary_file = Path('logs/last_run_summary.txt')
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(summary_file, 'w') as f:
        f.write(f"ASO Rank Guard PRO - Run Summary\n")
        f.write(f"Date: {datetime.now()}\n\n")
        for module, result in results.items():
            f.write(f"{module}: {result}\n")
    
    print(f"\n💾 Resumen guardado en: {summary_file}")
    
    print("\n" + "="*80)
    print("🎉 MONITOREO COMPLETADO")
    print("="*80)
    
    return results


if __name__ == "__main__":
    try:
        results = run_pro_monitor()
        
        # Exit code basado en errores
        error_count = sum(1 for r in results.values() if r.get('status') == 'error')
        sys.exit(1 if error_count > 0 else 0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por usuario")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}", exc_info=True)
        sys.exit(1)
