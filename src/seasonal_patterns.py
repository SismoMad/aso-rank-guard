#!/usr/bin/env python3
"""
Seasonal Patterns Detector - Detección de patrones estacionales en rankings
Identifica tendencias temporales y predice movimientos futuros
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class SeasonalPattern:
    """Representa un patrón estacional detectado"""
    
    def __init__(self, keyword: str, pattern_type: str, 
                 description: str, confidence: float):
        self.keyword = keyword
        self.pattern_type = pattern_type  # daily, weekly, monthly, yearly
        self.description = description
        self.confidence = confidence  # 0-1
        self.predictions = []
    
    def to_dict(self) -> Dict:
        return {
            'keyword': self.keyword,
            'pattern_type': self.pattern_type,
            'description': self.description,
            'confidence': self.confidence,
            'predictions': self.predictions
        }


class SeasonalPatternsDetector:
    """Detector de patrones estacionales"""
    
    def __init__(self, config: dict):
        self.config = config
        self.ranks_file = Path(config['storage']['ranks_file'])
        self.patterns_file = Path('data/seasonal_patterns.json')
        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar patrones conocidos
        self.known_patterns = self._load_patterns()
        
        logger.info("✅ SeasonalPatternsDetector inicializado")
    
    def _load_patterns(self) -> List[SeasonalPattern]:
        """Cargar patrones guardados"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                patterns = [
                    SeasonalPattern(
                        keyword=p['keyword'],
                        pattern_type=p['pattern_type'],
                        description=p['description'],
                        confidence=p['confidence']
                    ) for p in data
                ]
                logger.info(f"📂 Cargados {len(patterns)} patrones")
                return patterns
            except Exception as e:
                logger.warning(f"⚠️  Error cargando patrones: {e}")
                return []
        return []
    
    def _save_patterns(self):
        """Guardar patrones detectados"""
        try:
            data = [p.to_dict() for p in self.known_patterns]
            with open(self.patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Patrones guardados")
        except Exception as e:
            logger.error(f"❌ Error guardando patrones: {e}")
    
    def detect_weekly_patterns(self, df: pd.DataFrame, keyword: str) -> Optional[SeasonalPattern]:
        """
        Detectar patrones semanales (ej: mejor en domingos)
        
        Args:
            df: DataFrame con histórico de rankings
            keyword: Keyword a analizar
        
        Returns:
            SeasonalPattern si se detecta algo significativo
        """
        kw_data = df[df['keyword'] == keyword].copy()
        
        if len(kw_data) < 14:  # Necesitamos al menos 2 semanas
            return None
        
        # Añadir día de la semana (0=Monday, 6=Sunday)
        kw_data['day_of_week'] = pd.to_datetime(kw_data['date']).dt.dayofweek
        kw_data['rank'] = pd.to_numeric(kw_data['rank'], errors='coerce')
        
        # Agrupar por día de la semana
        weekly_avg = kw_data.groupby('day_of_week')['rank'].agg(['mean', 'count']).reset_index()
        
        if len(weekly_avg) < 7:  # No hay datos de todos los días
            return None
        
        # Encontrar mejor y peor día
        best_day = weekly_avg.loc[weekly_avg['mean'].idxmin()]
        worst_day = weekly_avg.loc[weekly_avg['mean'].idxmax()]
        
        diff = worst_day['mean'] - best_day['mean']
        
        # Solo reportar si la diferencia es significativa (>10 posiciones)
        if diff > 10:
            day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            
            pattern = SeasonalPattern(
                keyword=keyword,
                pattern_type='weekly',
                description=f"Mejor en {day_names[int(best_day['day_of_week'])]} (avg #{best_day['mean']:.1f}), "
                           f"peor en {day_names[int(worst_day['day_of_week'])]} (avg #{worst_day['mean']:.1f})",
                confidence=min(diff / 20, 1.0)  # Más diferencia = más confianza
            )
            
            return pattern
        
        return None
    
    def detect_monthly_patterns(self, df: pd.DataFrame, keyword: str) -> Optional[SeasonalPattern]:
        """
        Detectar patrones mensuales (ej: mejor en diciembre)
        
        Args:
            df: DataFrame con histórico
            keyword: Keyword a analizar
        
        Returns:
            SeasonalPattern si se detecta
        """
        kw_data = df[df['keyword'] == keyword].copy()
        
        if len(kw_data) < 30:  # Necesitamos al menos un mes
            return None
        
        # Añadir mes
        kw_data['month'] = pd.to_datetime(kw_data['date']).dt.month
        kw_data['rank'] = pd.to_numeric(kw_data['rank'], errors='coerce')
        
        # Agrupar por mes
        monthly_avg = kw_data.groupby('month')['rank'].agg(['mean', 'count']).reset_index()
        
        if len(monthly_avg) < 2:  # Necesitamos al menos 2 meses
            return None
        
        # Encontrar mejor y peor mes
        best_month = monthly_avg.loc[monthly_avg['mean'].idxmin()]
        worst_month = monthly_avg.loc[monthly_avg['mean'].idxmax()]
        
        diff = worst_month['mean'] - best_month['mean']
        
        # Solo si diferencia significativa (>15 posiciones)
        if diff > 15:
            month_names = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            
            pattern = SeasonalPattern(
                keyword=keyword,
                pattern_type='monthly',
                description=f"Mejor en {month_names[int(best_month['month'])]} (#{best_month['mean']:.1f}), "
                           f"peor en {month_names[int(worst_month['month'])]} (#{worst_month['mean']:.1f})",
                confidence=min(diff / 30, 1.0)
            )
            
            return pattern
        
        return None
    
    def detect_trend_direction(self, df: pd.DataFrame, keyword: str, 
                             days: int = 14) -> Optional[Dict]:
        """
        Detectar tendencia direccional (subiendo/bajando)
        
        Args:
            df: DataFrame con histórico
            keyword: Keyword a analizar
            days: Número de días a analizar
        
        Returns:
            Dict con tendencia detectada
        """
        kw_data = df[df['keyword'] == keyword].copy()
        
        if len(kw_data) < days:
            return None
        
        # Últimos N días
        cutoff = datetime.now() - timedelta(days=days)
        recent = kw_data[pd.to_datetime(kw_data['date']) >= cutoff].sort_values('date')
        
        if len(recent) < 5:
            return None
        
        recent['rank'] = pd.to_numeric(recent['rank'], errors='coerce')
        
        # Calcular tendencia simple (comparar primera mitad vs segunda mitad)
        mid = len(recent) // 2
        first_half_avg = recent.iloc[:mid]['rank'].mean()
        second_half_avg = recent.iloc[mid:]['rank'].mean()
        
        diff = first_half_avg - second_half_avg  # Positivo = mejoró
        
        if abs(diff) > 5:  # Cambio significativo
            if diff > 0:
                trend = 'improving'
                emoji = '📈'
                desc = f"Tendencia alcista últimos {days}d (+{diff:.1f} posiciones)"
            else:
                trend = 'declining'
                emoji = '📉'
                desc = f"Tendencia bajista últimos {days}d ({diff:.1f} posiciones)"
            
            return {
                'keyword': keyword,
                'trend': trend,
                'change': diff,
                'emoji': emoji,
                'description': desc,
                'confidence': min(abs(diff) / 20, 1.0)
            }
        
        return None
    
    def predict_next_movement(self, df: pd.DataFrame, keyword: str) -> Optional[Dict]:
        """
        Predecir próximo movimiento basado en patrones históricos
        
        Args:
            df: DataFrame con histórico
            keyword: Keyword a predecir
        
        Returns:
            Dict con predicción
        """
        # Buscar patrón conocido
        known_pattern = next((p for p in self.known_patterns 
                            if p.keyword == keyword), None)
        
        if not known_pattern:
            return None
        
        now = datetime.now()
        
        # Predicción basada en tipo de patrón
        if known_pattern.pattern_type == 'weekly':
            # Predecir basado en día de la semana
            current_day = now.weekday()
            
            # Simplificado: si conocemos que es mejor en domingo (6)
            # TODO: Mejorar con datos reales del patrón
            if current_day < 6:
                days_to_sunday = 6 - current_day
                return {
                    'keyword': keyword,
                    'prediction': f"Posible mejora en {days_to_sunday} días (domingo)",
                    'confidence': known_pattern.confidence,
                    'type': 'weekly_pattern'
                }
        
        elif known_pattern.pattern_type == 'monthly':
            # Predecir basado en mes
            # TODO: Implementar predicción mensual
            pass
        
        return None
    
    def analyze_all_keywords(self, min_history_days: int = 14) -> Dict:
        """
        Analizar todos los keywords buscando patrones
        
        Args:
            min_history_days: Días mínimos de histórico necesarios
        
        Returns:
            Resumen de patrones detectados
        """
        if not self.ranks_file.exists():
            return {'error': 'No hay datos históricos'}
        
        logger.info("🔍 Analizando patrones estacionales...")
        
        df = pd.read_csv(self.ranks_file)
        df['date'] = pd.to_datetime(df['date'])
        
        # Filtrar keywords con suficiente histórico
        cutoff = datetime.now() - timedelta(days=min_history_days)
        recent = df[df['date'] >= cutoff]
        
        keywords = recent['keyword'].unique()
        
        weekly_patterns = []
        monthly_patterns = []
        trends = []
        predictions = []
        
        for keyword in keywords:
            # Patrones semanales
            weekly = self.detect_weekly_patterns(df, keyword)
            if weekly:
                weekly_patterns.append(weekly)
            
            # Patrones mensuales (solo si hay suficiente data)
            if len(df[df['keyword'] == keyword]) >= 30:
                monthly = self.detect_monthly_patterns(df, keyword)
                if monthly:
                    monthly_patterns.append(monthly)
            
            # Tendencias
            trend = self.detect_trend_direction(df, keyword, days=14)
            if trend:
                trends.append(trend)
            
            # Predicciones (basadas en patrones conocidos)
            prediction = self.predict_next_movement(df, keyword)
            if prediction:
                predictions.append(prediction)
        
        # Guardar nuevos patrones
        new_patterns = weekly_patterns + monthly_patterns
        if new_patterns:
            self.known_patterns = new_patterns
            self._save_patterns()
        
        summary = {
            'analyzed_keywords': len(keywords),
            'weekly_patterns': [p.to_dict() for p in weekly_patterns],
            'monthly_patterns': [p.to_dict() for p in monthly_patterns],
            'trends': trends,
            'predictions': predictions
        }
        
        logger.info(f"✅ Análisis completado: {len(weekly_patterns)} patrones semanales, "
                   f"{len(monthly_patterns)} mensuales, {len(trends)} tendencias")
        
        return summary
    
    def format_patterns_report(self, analysis: Dict) -> str:
        """Formatear reporte de patrones para Telegram"""
        msg = "📅 *SEASONAL PATTERNS REPORT*\n\n"
        
        # Tendencias actuales
        trends = analysis.get('trends', [])
        if trends:
            msg += "📈 *TENDENCIAS ACTUALES (14 días):*\n"
            
            improving = [t for t in trends if t['trend'] == 'improving']
            declining = [t for t in trends if t['trend'] == 'declining']
            
            if improving:
                msg += f"\n🟢 Mejorando ({len(improving)}):\n"
                for t in improving[:5]:
                    msg += f"  • `{t['keyword']}`: {t['description']}\n"
            
            if declining:
                msg += f"\n🔴 Declinando ({len(declining)}):\n"
                for t in declining[:5]:
                    msg += f"  • `{t['keyword']}`: {t['description']}\n"
            
            msg += "\n"
        
        # Patrones semanales
        weekly = analysis.get('weekly_patterns', [])
        if weekly:
            msg += f"📆 *PATRONES SEMANALES:* ({len(weekly)} detectados)\n"
            for p in weekly[:3]:
                msg += f"  • `{p['keyword']}`\n"
                msg += f"    {p['description']}\n"
            msg += "\n"
        
        # Patrones mensuales
        monthly = analysis.get('monthly_patterns', [])
        if monthly:
            msg += f"📅 *PATRONES MENSUALES:* ({len(monthly)} detectados)\n"
            for p in monthly[:3]:
                msg += f"  • `{p['keyword']}`\n"
                msg += f"    {p['description']}\n"
            msg += "\n"
        
        # Predicciones
        predictions = analysis.get('predictions', [])
        if predictions:
            msg += f"🔮 *PREDICCIONES:*\n"
            for pred in predictions[:3]:
                msg += f"  • {pred['prediction']}\n"
            msg += "\n"
        
        if not trends and not weekly and not monthly:
            msg += "ℹ️ No hay patrones significativos detectados aún.\n"
            msg += "Necesitas más histórico (recomendado: 30+ días)\n"
        
        msg += f"\n_Analizadas {analysis['analyzed_keywords']} keywords_"
        
        return msg


def main():
    """Test del detector de patrones"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    detector = SeasonalPatternsDetector(config)
    
    print("🧪 Testing Seasonal Patterns Detector\n")
    
    analysis = detector.analyze_all_keywords(min_history_days=7)
    
    if 'error' in analysis:
        print(f"❌ {analysis['error']}")
        return
    
    print(f"✅ Análisis completado:")
    print(f"   Keywords analizadas: {analysis['analyzed_keywords']}")
    print(f"   Patrones semanales: {len(analysis['weekly_patterns'])}")
    print(f"   Patrones mensuales: {len(analysis['monthly_patterns'])}")
    print(f"   Tendencias: {len(analysis['trends'])}")
    
    # Mostrar reporte
    print("\n" + "="*60)
    print(detector.format_patterns_report(analysis))


if __name__ == "__main__":
    main()
