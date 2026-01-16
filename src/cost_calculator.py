#!/usr/bin/env python3
"""
Cost Calculator - Calculador de impacto económico de rankings ASO
Estima el costo de NO estar en top 10 y el ROI de optimizaciones
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class CostCalculator:
    """Calculador de costos e impacto económico"""
    
    def __init__(self, config: dict):
        self.config = config
        
        # Métricas de negocio (configurables)
        self.business_metrics = {
            'avg_cvr': 0.03,  # 3% conversion rate (visita → descarga)
            'avg_retention_d1': 0.40,  # 40% retención día 1
            'avg_retention_d7': 0.15,  # 15% retención día 7
            'avg_arpu_monthly': 2.5,  # $2.5 ARPU mensual (freemium con IAP)
            'avg_ltv_6months': 12.0,  # $12 LTV a 6 meses
        }
        
        # Cargar métricas personalizadas si existen
        self._load_custom_metrics()
        
        logger.info("✅ CostCalculator inicializado")
    
    def _load_custom_metrics(self):
        """Cargar métricas personalizadas desde config"""
        custom_file = Path('data/business_metrics.json')
        if custom_file.exists():
            try:
                with open(custom_file, 'r') as f:
                    custom = json.load(f)
                self.business_metrics.update(custom)
                logger.info("📂 Métricas de negocio personalizadas cargadas")
            except Exception as e:
                logger.warning(f"⚠️  Error cargando métricas: {e}")
    
    def save_custom_metrics(self, metrics: Dict):
        """Guardar métricas personalizadas"""
        custom_file = Path('data/business_metrics.json')
        custom_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(custom_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            self.business_metrics.update(metrics)
            logger.info("💾 Métricas de negocio guardadas")
        except Exception as e:
            logger.error(f"❌ Error guardando métricas: {e}")
    
    def estimate_impressions_by_rank(self, rank: int, keyword_volume: int) -> int:
        """
        Estimar impresiones diarias según ranking
        
        Basado en datos de la industria:
        - Rank #1: ~40% de impresiones
        - Rank #2: ~20%
        - Rank #3: ~12%
        - Rank #4-5: ~8%
        - Rank #6-10: ~3-5%
        - Rank #11-20: ~1-2%
        - Rank #21-50: ~0.5-1%
        - Rank #51+: <0.5%
        
        Args:
            rank: Posición en el ranking
            keyword_volume: Volumen estimado de búsquedas/día
        
        Returns:
            Impresiones estimadas/día
        """
        if rank == 1:
            share = 0.40
        elif rank == 2:
            share = 0.20
        elif rank == 3:
            share = 0.12
        elif rank <= 5:
            share = 0.08
        elif rank <= 10:
            share = 0.04
        elif rank <= 20:
            share = 0.015
        elif rank <= 50:
            share = 0.007
        elif rank <= 100:
            share = 0.003
        else:
            share = 0.001
        
        return int(keyword_volume * share)
    
    def calculate_revenue_potential(self, daily_impressions: int) -> Dict:
        """
        Calcular potencial de revenue a partir de impresiones
        
        Args:
            daily_impressions: Impresiones diarias estimadas
        
        Returns:
            Dict con métricas de revenue
        """
        cvr = self.business_metrics['avg_cvr']
        arpu = self.business_metrics['avg_arpu_monthly']
        ltv = self.business_metrics['avg_ltv_6months']
        
        # Descargas mensuales
        monthly_downloads = daily_impressions * 30 * cvr
        
        # Revenue mensual
        monthly_revenue = monthly_downloads * arpu
        
        # Revenue a 6 meses (LTV)
        ltv_revenue = monthly_downloads * ltv
        
        return {
            'daily_impressions': daily_impressions,
            'monthly_impressions': daily_impressions * 30,
            'monthly_downloads': int(monthly_downloads),
            'monthly_revenue_usd': round(monthly_revenue, 2),
            'ltv_6months_usd': round(ltv_revenue, 2),
            'yearly_revenue_usd': round(monthly_revenue * 12, 2)
        }
    
    def calculate_opportunity_cost(self, current_rank: int, target_rank: int,
                                  keyword_volume: int) -> Dict:
        """
        Calcular costo de oportunidad de NO mejorar ranking
        
        Args:
            current_rank: Ranking actual
            target_rank: Ranking objetivo (ej: 10 para top 10)
            keyword_volume: Volumen de búsquedas/día
        
        Returns:
            Dict con análisis de costo
        """
        # Impresiones actuales
        current_impressions = self.estimate_impressions_by_rank(current_rank, keyword_volume)
        current_revenue = self.calculate_revenue_potential(current_impressions)
        
        # Impresiones si alcanzas objetivo
        target_impressions = self.estimate_impressions_by_rank(target_rank, keyword_volume)
        target_revenue = self.calculate_revenue_potential(target_impressions)
        
        # Diferencial (lo que estás perdiendo)
        monthly_lost = target_revenue['monthly_revenue_usd'] - current_revenue['monthly_revenue_usd']
        yearly_lost = monthly_lost * 12
        
        return {
            'current_rank': current_rank,
            'target_rank': target_rank,
            'keyword_volume': keyword_volume,
            'current_monthly_revenue': current_revenue['monthly_revenue_usd'],
            'target_monthly_revenue': target_revenue['monthly_revenue_usd'],
            'monthly_opportunity_cost': round(monthly_lost, 2),
            'yearly_opportunity_cost': round(yearly_lost, 2),
            'impressions_gain': target_impressions - current_impressions,
            'downloads_gain': target_revenue['monthly_downloads'] - current_revenue['monthly_downloads']
        }
    
    def calculate_drop_impact(self, keyword: str, prev_rank: int, 
                            current_rank: int, keyword_volume: int) -> Dict:
        """
        Calcular impacto económico de una caída en ranking
        
        Args:
            keyword: Keyword afectada
            prev_rank: Ranking anterior
            current_rank: Ranking actual
            keyword_volume: Volumen estimado
        
        Returns:
            Dict con análisis de impacto
        """
        # Impresiones perdidas
        prev_impressions = self.estimate_impressions_by_rank(prev_rank, keyword_volume)
        current_impressions = self.estimate_impressions_by_rank(current_rank, keyword_volume)
        
        lost_impressions = prev_impressions - current_impressions
        
        # Revenue perdido
        prev_revenue = self.calculate_revenue_potential(prev_impressions)
        current_revenue = self.calculate_revenue_potential(current_impressions)
        
        monthly_loss = prev_revenue['monthly_revenue_usd'] - current_revenue['monthly_revenue_usd']
        
        # Proyección si no se recupera
        yearly_loss = monthly_loss * 12
        
        return {
            'keyword': keyword,
            'rank_drop': current_rank - prev_rank,
            'prev_rank': prev_rank,
            'current_rank': current_rank,
            'lost_impressions_daily': lost_impressions,
            'lost_impressions_monthly': lost_impressions * 30,
            'monthly_revenue_loss': round(monthly_loss, 2),
            'yearly_revenue_loss': round(yearly_loss, 2),
            'severity': 'CRITICAL' if monthly_loss > 100 else 'HIGH' if monthly_loss > 50 else 'MEDIUM'
        }
    
    def estimate_total_portfolio_value(self, ranks_df: pd.DataFrame, 
                                      volume_estimates: Dict[str, int]) -> Dict:
        """
        Estimar valor total del portfolio de keywords
        
        Args:
            ranks_df: DataFrame con rankings actuales
            volume_estimates: Dict {keyword: volumen_estimado}
        
        Returns:
            Dict con valuación del portfolio
        """
        if len(ranks_df) == 0:
            return {}
        
        total_monthly_revenue = 0
        total_impressions = 0
        
        keyword_values = []
        
        # Obtener rankings más recientes
        latest_date = ranks_df['date'].max()
        latest = ranks_df[ranks_df['date'] == latest_date]
        
        for _, row in latest.iterrows():
            keyword = row['keyword']
            rank = int(row['rank'])
            volume = volume_estimates.get(keyword, 100)  # Default 100 si no hay dato
            
            impressions = self.estimate_impressions_by_rank(rank, volume)
            revenue_data = self.calculate_revenue_potential(impressions)
            
            total_monthly_revenue += revenue_data['monthly_revenue_usd']
            total_impressions += impressions
            
            keyword_values.append({
                'keyword': keyword,
                'rank': rank,
                'volume': volume,
                'daily_impressions': impressions,
                'monthly_revenue': revenue_data['monthly_revenue_usd'],
                'yearly_revenue': revenue_data['yearly_revenue_usd']
            })
        
        # Ordenar por revenue (más valiosas primero)
        keyword_values.sort(key=lambda x: x['monthly_revenue'], reverse=True)
        
        return {
            'total_monthly_revenue': round(total_monthly_revenue, 2),
            'total_yearly_revenue': round(total_monthly_revenue * 12, 2),
            'total_daily_impressions': total_impressions,
            'total_monthly_impressions': total_impressions * 30,
            'top_revenue_keywords': keyword_values[:10],
            'keywords_analyzed': len(keyword_values)
        }
    
    def calculate_aso_roi(self, optimization_cost: float, 
                         expected_rank_improvements: List[Dict]) -> Dict:
        """
        Calcular ROI de una inversión ASO
        
        Args:
            optimization_cost: Costo de la optimización (ej: $500 consultor ASO)
            expected_rank_improvements: Lista de mejoras esperadas
                [{'keyword': 'X', 'from': 50, 'to': 20, 'volume': 200}, ...]
        
        Returns:
            Análisis de ROI
        """
        total_monthly_gain = 0
        
        for improvement in expected_rank_improvements:
            keyword = improvement['keyword']
            from_rank = improvement['from']
            to_rank = improvement['to']
            volume = improvement['volume']
            
            # Calcular ganancia
            opp_cost = self.calculate_opportunity_cost(from_rank, to_rank, volume)
            monthly_gain = opp_cost['target_monthly_revenue'] - opp_cost['current_monthly_revenue']
            total_monthly_gain += monthly_gain
        
        # ROI
        yearly_gain = total_monthly_gain * 12
        roi_percentage = (yearly_gain - optimization_cost) / optimization_cost * 100
        
        # Tiempo para recuperar inversión
        months_to_breakeven = optimization_cost / total_monthly_gain if total_monthly_gain > 0 else 999
        
        return {
            'optimization_cost': optimization_cost,
            'monthly_revenue_gain': round(total_monthly_gain, 2),
            'yearly_revenue_gain': round(yearly_gain, 2),
            'roi_percentage': round(roi_percentage, 1),
            'months_to_breakeven': round(months_to_breakeven, 1),
            'verdict': 'EXCELENTE' if roi_percentage > 500 else 'BUENO' if roi_percentage > 200 else 'ACEPTABLE' if roi_percentage > 100 else 'BAJO'
        }
    
    def format_cost_report(self, portfolio_value: Dict, 
                          top_opportunities: List[Dict] = None) -> str:
        """
        Formatear reporte de costos para Telegram
        
        Args:
            portfolio_value: Valuación del portfolio
            top_opportunities: Top oportunidades de mejora
        
        Returns:
            Mensaje formateado
        """
        msg = "💰 *COST & REVENUE ANALYSIS*\n\n"
        
        # Portfolio actual
        msg += "*PORTFOLIO ACTUAL:*\n"
        msg += f"💵 Revenue mensual: ${portfolio_value['total_monthly_revenue']:,.2f}\n"
        msg += f"📅 Revenue anual: ${portfolio_value['total_yearly_revenue']:,.2f}\n"
        msg += f"👁️ Impresiones/día: {portfolio_value['total_daily_impressions']:,}\n\n"
        
        # Top keywords más valiosas
        msg += "*TOP 5 KEYWORDS MÁS VALIOSAS:*\n"
        for i, kw in enumerate(portfolio_value['top_revenue_keywords'][:5], 1):
            msg += f"{i}. `{kw['keyword']}` — #{kw['rank']}\n"
            msg += f"   💰 ${kw['monthly_revenue']:.2f}/mes | 👁️ {kw['daily_impressions']}/día\n"
        
        msg += "\n"
        
        # Oportunidades de mejora
        if top_opportunities:
            msg += "*TOP OPORTUNIDADES ($ PERDIDO):*\n"
            for i, opp in enumerate(top_opportunities[:5], 1):
                msg += f"{i}. `{opp['keyword']}` #{opp['current_rank']}→#{opp['target_rank']}\n"
                msg += f"   💸 Perdiendo ${opp['monthly_opportunity_cost']:.2f}/mes\n"
            msg += "\n"
        
        msg += f"_Basado en CVR {self.business_metrics['avg_cvr']*100:.1f}% y ARPU ${self.business_metrics['avg_arpu_monthly']}_"
        
        return msg


def main():
    """Test del cost calculator"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    calculator = CostCalculator(config)
    
    print("🧪 Testing Cost Calculator\n")
    
    # Test 1: Opportunity cost
    print("1️⃣ Opportunity Cost Analysis:")
    opp = calculator.calculate_opportunity_cost(
        current_rank=35,
        target_rank=10,
        keyword_volume=200
    )
    print(f"   Keyword @ rank #35 → #10 (vol: 200)")
    print(f"   Perdiendo: ${opp['monthly_opportunity_cost']}/mes")
    print(f"   Yearly: ${opp['yearly_opportunity_cost']}/año\n")
    
    # Test 2: Drop impact
    print("2️⃣ Drop Impact:")
    drop = calculator.calculate_drop_impact(
        keyword='bible sleep',
        prev_rank=12,
        current_rank=25,
        keyword_volume=300
    )
    print(f"   Caída: #{drop['prev_rank']} → #{drop['current_rank']}")
    print(f"   Impacto: ${drop['monthly_revenue_loss']}/mes")
    print(f"   Severidad: {drop['severity']}\n")
    
    # Test 3: ASO ROI
    print("3️⃣ ASO Investment ROI:")
    roi = calculator.calculate_aso_roi(
        optimization_cost=500,  # $500 consultor
        expected_rank_improvements=[
            {'keyword': 'bible sleep', 'from': 35, 'to': 15, 'volume': 300},
            {'keyword': 'audio bible', 'from': 60, 'to': 30, 'volume': 200},
        ]
    )
    print(f"   Inversión: ${roi['optimization_cost']}")
    print(f"   Revenue ganado: ${roi['monthly_revenue_gain']}/mes")
    print(f"   ROI: {roi['roi_percentage']}%")
    print(f"   Breakeven: {roi['months_to_breakeven']} meses")
    print(f"   Veredicto: {roi['verdict']}")


if __name__ == "__main__":
    main()
