#!/usr/bin/env python3
"""
A/B Testing Tracker - Sistema de tracking de experimentos ASO
Monitoriza el impacto de cambios en metadata
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class ABTest:
    """Representa un experimento A/B"""
    
    def __init__(self, name: str, hypothesis: str, change_type: str, 
                 description: str, start_date: datetime):
        self.name = name
        self.hypothesis = hypothesis
        self.change_type = change_type  # title, subtitle, screenshots, keywords, description
        self.description = description
        self.start_date = start_date
        self.end_date = None
        self.status = 'running'  # running, completed, cancelled
        
        # Métricas before/after
        self.metrics_before = {}
        self.metrics_after = {}
        self.impact = {}
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        return {
            'name': self.name,
            'hypothesis': self.hypothesis,
            'change_type': self.change_type,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'metrics_before': self.metrics_before,
            'metrics_after': self.metrics_after,
            'impact': self.impact
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crear desde diccionario"""
        test = cls(
            name=data['name'],
            hypothesis=data['hypothesis'],
            change_type=data['change_type'],
            description=data['description'],
            start_date=datetime.fromisoformat(data['start_date'])
        )
        if data.get('end_date'):
            test.end_date = datetime.fromisoformat(data['end_date'])
        test.status = data['status']
        test.metrics_before = data.get('metrics_before', {})
        test.metrics_after = data.get('metrics_after', {})
        test.impact = data.get('impact', {})
        return test


class ABTestingTracker:
    """Tracker de experimentos A/B"""
    
    def __init__(self, config: dict):
        self.config = config
        self.experiments_file = Path('data/ab_experiments.json')
        self.experiments_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar experimentos
        self.experiments = self._load_experiments()
        
        logger.info("✅ ABTestingTracker inicializado")
    
    def _load_experiments(self) -> List[ABTest]:
        """Cargar experimentos desde JSON"""
        if self.experiments_file.exists():
            try:
                with open(self.experiments_file, 'r') as f:
                    data = json.load(f)
                experiments = [ABTest.from_dict(exp) for exp in data]
                logger.info(f"📂 Cargados {len(experiments)} experimentos")
                return experiments
            except Exception as e:
                logger.warning(f"⚠️  Error cargando experimentos: {e}")
                return []
        return []
    
    def _save_experiments(self):
        """Guardar experimentos a JSON"""
        try:
            data = [exp.to_dict() for exp in self.experiments]
            with open(self.experiments_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Experimentos guardados")
        except Exception as e:
            logger.error(f"❌ Error guardando experimentos: {e}")
    
    def create_experiment(self, name: str, hypothesis: str, change_type: str,
                         description: str, baseline_metrics: Dict) -> ABTest:
        """
        Crear nuevo experimento
        
        Args:
            name: Nombre del experimento
            hypothesis: Hipótesis a probar
            change_type: Tipo de cambio (title, subtitle, etc.)
            description: Descripción detallada del cambio
            baseline_metrics: Métricas actuales (antes del cambio)
        
        Returns:
            ABTest creado
        """
        experiment = ABTest(
            name=name,
            hypothesis=hypothesis,
            change_type=change_type,
            description=description,
            start_date=datetime.now()
        )
        
        experiment.metrics_before = baseline_metrics
        
        self.experiments.append(experiment)
        self._save_experiments()
        
        logger.info(f"🧪 Experimento creado: {name}")
        return experiment
    
    def get_baseline_metrics(self, ranks_df: pd.DataFrame, 
                           keywords: List[str] = None) -> Dict:
        """
        Obtener métricas baseline para un experimento
        
        Args:
            ranks_df: DataFrame con histórico de rankings
            keywords: Keywords a incluir (None = todas)
        
        Returns:
            Dict con métricas baseline
        """
        if len(ranks_df) == 0:
            return {}
        
        # Últimos 7 días
        cutoff = datetime.now() - timedelta(days=7)
        recent = ranks_df[ranks_df['date'] >= cutoff]
        
        if keywords:
            recent = recent[recent['keyword'].isin(keywords)]
        
        # Calcular métricas
        visible = recent[recent['rank'] < 250]
        
        metrics = {
            'period_start': (datetime.now() - timedelta(days=7)).isoformat(),
            'period_end': datetime.now().isoformat(),
            'keywords_tracked': len(recent['keyword'].unique()),
            'avg_rank': float(visible['rank'].mean()) if len(visible) > 0 else 0,
            'top_10_count': len(recent[recent['rank'] <= 10]),
            'top_30_count': len(recent[recent['rank'] <= 30]),
            'top_100_count': len(recent[recent['rank'] <= 100]),
            'visibility_rate': len(visible) / len(recent) * 100 if len(recent) > 0 else 0,
            'keyword_ranks': recent.groupby('keyword')['rank'].mean().to_dict()
        }
        
        return metrics
    
    def complete_experiment(self, experiment_name: str, 
                          final_metrics: Dict, notes: str = "") -> Dict:
        """
        Completar un experimento y calcular impacto
        
        Args:
            experiment_name: Nombre del experimento
            final_metrics: Métricas finales (después del cambio)
            notes: Notas adicionales
        
        Returns:
            Análisis de impacto
        """
        experiment = next((e for e in self.experiments if e.name == experiment_name), None)
        
        if not experiment:
            logger.error(f"❌ Experimento '{experiment_name}' no encontrado")
            return {}
        
        if experiment.status != 'running':
            logger.warning(f"⚠️  Experimento '{experiment_name}' ya está {experiment.status}")
            return {}
        
        # Guardar métricas finales
        experiment.metrics_after = final_metrics
        experiment.end_date = datetime.now()
        experiment.status = 'completed'
        
        # Calcular impacto
        impact = self._calculate_impact(experiment)
        experiment.impact = impact
        
        self._save_experiments()
        
        logger.info(f"✅ Experimento completado: {experiment_name}")
        return impact
    
    def _calculate_impact(self, experiment: ABTest) -> Dict:
        """Calcular impacto de un experimento"""
        before = experiment.metrics_before
        after = experiment.metrics_after
        
        impact = {
            'duration_days': (experiment.end_date - experiment.start_date).days,
            'avg_rank_change': after.get('avg_rank', 0) - before.get('avg_rank', 0),
            'top_10_change': after.get('top_10_count', 0) - before.get('top_10_count', 0),
            'top_30_change': after.get('top_30_count', 0) - before.get('top_30_count', 0),
            'top_100_change': after.get('top_100_count', 0) - before.get('top_100_count', 0),
            'visibility_change': after.get('visibility_rate', 0) - before.get('visibility_rate', 0),
        }
        
        # Calcular cambios por keyword
        keyword_impacts = {}
        before_ranks = before.get('keyword_ranks', {})
        after_ranks = after.get('keyword_ranks', {})
        
        for keyword in set(list(before_ranks.keys()) + list(after_ranks.keys())):
            before_rank = before_ranks.get(keyword, 999)
            after_rank = after_ranks.get(keyword, 999)
            diff = before_rank - after_rank  # Positivo = mejoró
            
            if abs(diff) >= 3:  # Cambio significativo
                keyword_impacts[keyword] = {
                    'before': before_rank,
                    'after': after_rank,
                    'change': diff
                }
        
        impact['keyword_impacts'] = keyword_impacts
        
        # Determinar si fue exitoso
        success_criteria = (
            impact['avg_rank_change'] < 0 or  # Mejor ranking
            impact['top_10_change'] > 0 or
            impact['visibility_change'] > 0
        )
        
        impact['success'] = success_criteria
        impact['verdict'] = self._generate_verdict(impact)
        
        return impact
    
    def _generate_verdict(self, impact: Dict) -> str:
        """Generar veredicto del experimento"""
        if impact['success']:
            if impact['top_10_change'] > 0:
                return f"✅ ÉXITO - {impact['top_10_change']} keywords nuevas en top 10"
            elif impact['avg_rank_change'] < -5:
                return f"✅ ÉXITO - Mejora promedio de {abs(impact['avg_rank_change']):.1f} posiciones"
            else:
                return "✅ ÉXITO MODERADO - Mejora detectada"
        else:
            if impact['avg_rank_change'] > 5:
                return f"❌ NEGATIVO - Caída promedio de {impact['avg_rank_change']:.1f} posiciones"
            else:
                return "⚠️ NEUTRO - Sin cambio significativo"
    
    def get_active_experiments(self) -> List[ABTest]:
        """Obtener experimentos activos"""
        return [e for e in self.experiments if e.status == 'running']
    
    def get_completed_experiments(self) -> List[ABTest]:
        """Obtener experimentos completados"""
        return [e for e in self.experiments if e.status == 'completed']
    
    def get_experiment_report(self, experiment_name: str) -> str:
        """
        Generar reporte de un experimento
        
        Args:
            experiment_name: Nombre del experimento
        
        Returns:
            Reporte formateado
        """
        experiment = next((e for e in self.experiments if e.name == experiment_name), None)
        
        if not experiment:
            return f"❌ Experimento '{experiment_name}' no encontrado"
        
        report = f"🧪 *EXPERIMENTO: {experiment.name}*\n\n"
        report += f"**Hipótesis:** {experiment.hypothesis}\n"
        report += f"**Cambio:** {experiment.change_type}\n"
        report += f"**Descripción:** {experiment.description}\n\n"
        
        report += f"📅 **Período:**\n"
        report += f"Inicio: {experiment.start_date.strftime('%d/%m/%Y')}\n"
        if experiment.end_date:
            report += f"Fin: {experiment.end_date.strftime('%d/%m/%Y')}\n"
            report += f"Duración: {experiment.impact.get('duration_days', 0)} días\n"
        report += f"Status: {experiment.status.upper()}\n\n"
        
        if experiment.status == 'completed':
            impact = experiment.impact
            report += f"📊 **RESULTADOS:**\n"
            report += f"{impact.get('verdict', 'N/A')}\n\n"
            
            report += f"**Métricas:**\n"
            report += f"• Rank promedio: {impact.get('avg_rank_change', 0):+.1f} posiciones\n"
            report += f"• Top 10: {impact.get('top_10_change', 0):+d} keywords\n"
            report += f"• Top 30: {impact.get('top_30_change', 0):+d} keywords\n"
            report += f"• Visibilidad: {impact.get('visibility_change', 0):+.1f}%\n\n"
            
            # Keywords destacadas
            kw_impacts = impact.get('keyword_impacts', {})
            if kw_impacts:
                report += f"**Keywords con mayor cambio:**\n"
                sorted_kws = sorted(kw_impacts.items(), 
                                   key=lambda x: abs(x[1]['change']), 
                                   reverse=True)[:5]
                for kw, data in sorted_kws:
                    emoji = '📈' if data['change'] > 0 else '📉'
                    report += f"{emoji} {kw}: #{data['before']}→#{data['after']} ({data['change']:+d})\n"
        
        return report
    
    def get_summary_report(self) -> str:
        """Generar resumen de todos los experimentos"""
        total = len(self.experiments)
        active = len(self.get_active_experiments())
        completed = self.get_completed_experiments()
        
        report = f"🧪 *A/B TESTING SUMMARY*\n\n"
        report += f"**Total experimentos:** {total}\n"
        report += f"**Activos:** {active}\n"
        report += f"**Completados:** {len(completed)}\n\n"
        
        if completed:
            successful = [e for e in completed if e.impact.get('success', False)]
            report += f"**Tasa de éxito:** {len(successful)}/{len(completed)} ({len(successful)/len(completed)*100:.1f}%)\n\n"
            
            report += f"**Últimos 3 experimentos:**\n"
            for exp in sorted(completed, key=lambda x: x.end_date, reverse=True)[:3]:
                report += f"• {exp.name}: {exp.impact.get('verdict', 'N/A')}\n"
        
        return report


def main():
    """Test del A/B testing tracker"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    tracker = ABTestingTracker(config)
    
    print("🧪 Testing A/B Tracker\n")
    
    # Crear experimento de ejemplo
    baseline = {
        'avg_rank': 45.5,
        'top_10_count': 2,
        'top_30_count': 5,
        'visibility_rate': 75.0,
        'keyword_ranks': {
            'bible sleep': 12,
            'bedtime bible': 35,
            'audio bible': 48
        }
    }
    
    exp = tracker.create_experiment(
        name="Subtitle Test - Add 'Sleep' Focus",
        hypothesis="Adding 'Sleep' to subtitle will improve sleep-related keyword ranks",
        change_type="subtitle",
        description="Changed subtitle from 'Bible Stories & Chat' to 'Bible Stories for Better Sleep & Chat'",
        baseline_metrics=baseline
    )
    
    print(f"✅ Experimento creado: {exp.name}")
    print(f"📊 Baseline: {baseline['avg_rank']} avg rank")
    
    # Simular métricas finales (después de 7 días)
    final_metrics = {
        'avg_rank': 38.2,  # Mejoró
        'top_10_count': 3,
        'top_30_count': 7,
        'visibility_rate': 82.0,
        'keyword_ranks': {
            'bible sleep': 8,  # Mejoró mucho
            'bedtime bible': 28,  # Mejoró
            'audio bible': 50  # Empeoró ligeramente
        }
    }
    
    impact = tracker.complete_experiment(exp.name, final_metrics)
    
    print(f"\n✅ Experimento completado")
    print(f"Veredicto: {impact['verdict']}")
    
    # Mostrar reporte
    print("\n" + "="*60)
    print(tracker.get_experiment_report(exp.name))


if __name__ == "__main__":
    main()
