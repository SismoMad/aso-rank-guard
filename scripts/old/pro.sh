#!/bin/bash
# ASO Rank Guard PRO - Helper Script
# Comandos rápidos para usar las nuevas features

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# Activar venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment no encontrado${NC}"
    echo "Ejecuta: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Función de ayuda
show_help() {
    echo -e "${BLUE}┌────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${NC}  🚀 ${GREEN}ASO RANK GUARD PRO${NC} - Helper Script              ${BLUE}│${NC}"
    echo -e "${BLUE}└────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    echo -e "${YELLOW}Uso:${NC} ./pro.sh [comando]"
    echo ""
    echo -e "${YELLOW}Comandos Disponibles:${NC}"
    echo ""
    echo -e "  ${GREEN}run${NC}              - Ejecutar monitoring completo PRO"
    echo -e "  ${GREEN}dashboard${NC}        - Abrir dashboard interactivo"
    echo -e "  ${GREEN}discoveries${NC}      - Ver top 20 keyword discoveries"
    echo -e "  ${GREEN}competitors${NC}      - Ver competidores principales"
    echo -e "  ${GREEN}summary${NC}          - Ver resumen última ejecución"
    echo -e "  ${GREEN}test${NC}             - Ejecutar tests de PRO features"
    echo -e "  ${GREEN}experiments${NC}      - Gestionar experimentos A/B"
    echo -e "  ${GREEN}patterns${NC}         - Analizar patrones estacionales"
    echo -e "  ${GREEN}costs${NC}            - Calcular revenue & opportunity costs"
    echo -e "  ${GREEN}help${NC}             - Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  ./pro.sh run             # Run complete monitoring"
    echo "  ./pro.sh dashboard       # Open dashboard"
    echo "  ./pro.sh discoveries     # See new keyword opportunities"
    echo ""
}

# Comando: run
cmd_run() {
    echo -e "${GREEN}🚀 Ejecutando ASO Rank Guard PRO...${NC}"
    python run_pro.py
    
    echo ""
    echo -e "${GREEN}✅ Completado!${NC}"
    echo -e "Ver resumen: ${YELLOW}./pro.sh summary${NC}"
    echo -e "Abrir dashboard: ${YELLOW}./pro.sh dashboard${NC}"
}

# Comando: dashboard
cmd_dashboard() {
    if [ -f "web/dashboard-interactive.html" ]; then
        echo -e "${GREEN}📊 Abriendo dashboard...${NC}"
        open web/dashboard-interactive.html
    else
        echo -e "${RED}❌ Dashboard no encontrado${NC}"
        echo "Ejecuta primero: ./pro.sh run"
    fi
}

# Comando: discoveries
cmd_discoveries() {
    if [ -f "data/keyword_discoveries.csv" ]; then
        echo -e "${GREEN}🔍 Top 20 Keyword Discoveries:${NC}"
        echo ""
        head -21 data/keyword_discoveries.csv | column -t -s ','
        echo ""
        total=$(wc -l < data/keyword_discoveries.csv)
        echo -e "${YELLOW}Total discoveries: $((total - 1))${NC}"
        echo "Ver todos: cat data/keyword_discoveries.csv | less"
    else
        echo -e "${RED}❌ No hay discoveries todavía${NC}"
        echo "Ejecuta: ./pro.sh run"
    fi
}

# Comando: competitors
cmd_competitors() {
    if [ -f "data/competitors.csv" ]; then
        echo -e "${GREEN}🎯 Competidores Principales:${NC}"
        echo ""
        head -21 data/competitors.csv | column -t -s ','
        echo ""
        total=$(wc -l < data/competitors.csv)
        echo -e "${YELLOW}Total competitors tracked: $((total - 1))${NC}"
        echo "Ver todos: cat data/competitors.csv | less"
    else
        echo -e "${RED}❌ No hay datos de competidores todavía${NC}"
        echo "Ejecuta: ./pro.sh run"
    fi
}

# Comando: summary
cmd_summary() {
    if [ -f "logs/last_run_summary.txt" ]; then
        echo -e "${GREEN}📋 Resumen Última Ejecución:${NC}"
        echo ""
        cat logs/last_run_summary.txt
    else
        echo -e "${RED}❌ No hay resumen todavía${NC}"
        echo "Ejecuta: ./pro.sh run"
    fi
}

# Comando: test
cmd_test() {
    echo -e "${GREEN}🧪 Ejecutando tests PRO...${NC}"
    python test_pro_features.py
}

# Comando: experiments
cmd_experiments() {
    echo -e "${GREEN}🧪 Gestión de Experimentos A/B${NC}"
    echo ""
    
    if [ -f "data/ab_experiments.json" ]; then
        python -c "
import json
import sys
from datetime import datetime

with open('data/ab_experiments.json', 'r') as f:
    data = json.load(f)
    exps = data.get('experiments', [])
    
    if not exps:
        print('No hay experimentos todavía')
        sys.exit(0)
    
    active = [e for e in exps if e['status'] == 'active']
    completed = [e for e in exps if e['status'] == 'completed']
    
    print(f'📊 Total: {len(exps)} experimentos')
    print(f'✅ Activos: {len(active)}')
    print(f'🏁 Completados: {len(completed)}')
    print()
    
    if active:
        print('🔄 ACTIVOS:')
        for exp in active:
            print(f\"  • {exp['name']} (desde {exp['start_date'][:10]})\")
        print()
    
    if completed:
        print('✅ COMPLETADOS:')
        for exp in completed[:5]:
            verdict = exp.get('verdict', 'unknown')
            emoji = '🎉' if verdict == 'success' else '❌' if verdict == 'failure' else '⚠️'
            print(f\"  {emoji} {exp['name']} - {verdict}\")
"
    else
        echo "No hay experimentos todavía"
        echo ""
        echo -e "${YELLOW}Crear nuevo experimento:${NC}"
        echo "python -c \"from src.ab_testing_tracker import ABTestingTracker; import yaml; config=yaml.safe_load(open('config/config.yaml')); tracker=ABTestingTracker(config); tracker.create_experiment('Test Name', 'Hypothesis', 'subtitle', 'Description')\""
    fi
}

# Comando: patterns
cmd_patterns() {
    echo -e "${GREEN}📅 Análisis de Patrones Estacionales${NC}"
    echo ""
    
    python -c "
from src.seasonal_patterns import SeasonalPatternsDetector
import yaml

config = yaml.safe_load(open('config/config.yaml'))
detector = SeasonalPatternsDetector(config)

analysis = detector.analyze_all_keywords(min_history_days=1)

if 'error' in analysis:
    print(f\"⚠️  {analysis['error']}\")
else:
    print(f\"📊 Keywords analizados: {analysis['analyzed_keywords']}\")
    print(f\"📈 Patrones semanales: {analysis['weekly_patterns_found']}\")
    print(f\"📆 Patrones mensuales: {analysis['monthly_patterns_found']}\")
    print(f\"📉 Tendencias detectadas: {analysis['trends_detected']}\")
    
    if analysis.get('insights'):
        print('\n💡 Insights:')
        for insight in analysis['insights'][:5]:
            print(f\"  • {insight}\")
"
}

# Comando: costs
cmd_costs() {
    echo -e "${GREEN}💰 Análisis de Costos y Revenue${NC}"
    echo ""
    
    python -c "
from src.cost_calculator import CostCalculator
import yaml
import pandas as pd

config = yaml.safe_load(open('config/config.yaml'))
calc = CostCalculator(config)

# Cargar ranks
try:
    ranks_df = pd.read_csv('data/ranks.csv')
    
    # Estimar volúmenes (placeholder)
    keywords = ranks_df['keyword'].unique()
    volume_estimates = {kw: 100 for kw in keywords}
    
    # Portfolio value
    portfolio = calc.estimate_total_portfolio_value(ranks_df, volume_estimates)
    
    if not portfolio:
        print('❌ No hay datos suficientes')
    else:
        print(f\"📊 PORTFOLIO VALUE:\")
        print(f\"  Monthly Revenue:  \${portfolio['total_monthly_revenue']:.2f}\")
        print(f\"  Yearly Revenue:   \${portfolio['total_yearly_revenue']:.2f}\")
        print(f\"  Daily Impressions: {portfolio['total_daily_impressions']:,}\")
        print(f\"  Keywords Analyzed: {portfolio['keywords_analyzed']}\")
        print()
        
        # Top keywords
        print(f\"💎 TOP 10 REVENUE KEYWORDS:\")
        for kw in portfolio['top_revenue_keywords']:
            print(f\"  • {kw['keyword'][:35]:35} Rank #{kw['rank']:3} → \${kw['monthly_revenue']:.2f}/month\")
        
        # Opportunity costs
        print()
        print(f\"⚠️  OPPORTUNITY COSTS (Keywords > Rank 10):\")
        latest = ranks_df.groupby('keyword').last().reset_index()
        below_10 = latest[latest['rank'] > 10].copy()
        
        opportunities = []
        for _, row in below_10.iterrows():
            opp = calc.calculate_opportunity_cost(
                current_rank=int(row['rank']),
                target_rank=10,
                keyword_volume=100
            )
            opportunities.append({
                'keyword': row['keyword'],
                'rank': int(row['rank']),
                'cost': opp['monthly_opportunity_cost']
            })
        
        opportunities.sort(key=lambda x: x['cost'], reverse=True)
        
        for opp in opportunities[:10]:
            print(f\"  • {opp['keyword'][:35]:35} Rank #{opp['rank']:3} → \${opp['cost']:.2f}/month lost\")
        
except FileNotFoundError:
    print('❌ No hay datos de ranks todavía')
    print('Ejecuta: ./pro.sh run')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
}

# Main
case "${1:-help}" in
    run)
        cmd_run
        ;;
    dashboard)
        cmd_dashboard
        ;;
    discoveries)
        cmd_discoveries
        ;;
    competitors)
        cmd_competitors
        ;;
    summary)
        cmd_summary
        ;;
    test)
        cmd_test
        ;;
    experiments)
        cmd_experiments
        ;;
    patterns)
        cmd_patterns
        ;;
    costs)
        cmd_costs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconocido: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
