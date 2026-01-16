#!/usr/bin/env python3
"""
Módulo de análisis de tendencias
Predicción de interés en keywords usando Google Trends y análisis de datos
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    logger.warning("⚠️  pytrends no instalado. Instala con: pip install pytrends")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class TrendAnalyzer:
    """Analizador de tendencias para keywords"""
    
    def __init__(self, config: dict):
        """
        Inicializar analizador
        
        Args:
            config: Diccionario de configuración
        """
        self.config = config
        self.google_trends_enabled = config['trends']['google_trends']['enabled']
        self.ai_enabled = config['trends']['ai_analysis']['enabled']
        
        # Inicializar Google Trends
        if self.google_trends_enabled and PYTRENDS_AVAILABLE:
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360)
                logger.info("✅ Google Trends inicializado")
            except Exception as e:
                logger.error(f"❌ Error inicializando Google Trends: {e}")
                self.google_trends_enabled = False
        elif self.google_trends_enabled and not PYTRENDS_AVAILABLE:
            logger.warning("⚠️  Google Trends habilitado pero pytrends no disponible")
            self.google_trends_enabled = False
        
        # Inicializar OpenAI (si está configurado)
        if self.ai_enabled and OPENAI_AVAILABLE:
            api_key = config['trends']['ai_analysis']['api_key']
            if api_key and api_key != "":
                openai.api_key = api_key
                logger.info("✅ OpenAI inicializado")
            else:
                logger.warning("⚠️  OpenAI API key no configurado")
                self.ai_enabled = False
    
    def get_keyword_trend(self, keyword: str, timeframe: str = 'today 3-m', 
                         region: str = 'US') -> Optional[Dict]:
        """
        Obtener tendencia de un keyword usando Google Trends
        
        Args:
            keyword: Keyword a analizar
            timeframe: Período de tiempo ('today 3-m', 'today 1-m', etc.)
            region: Región (US, ES, etc.)
        
        Returns:
            Diccionario con datos de tendencia
        """
        if not self.google_trends_enabled:
            return None
        
        try:
            # Construir payload
            self.pytrends.build_payload(
                kw_list=[keyword],
                cat=0,
                timeframe=timeframe,
                geo=region
            )
            
            # Obtener interés a lo largo del tiempo
            interest_over_time = self.pytrends.interest_over_time()
            
            if interest_over_time.empty:
                logger.warning(f"⚠️  No hay datos de tendencias para '{keyword}' en {region}")
                return None
            
            # Calcular estadísticas
            values = interest_over_time[keyword].values
            current_value = values[-1]
            avg_value = values.mean()
            max_value = values.max()
            min_value = values.min()
            
            # Calcular tendencia (últimos 7 días vs 7 anteriores)
            if len(values) >= 14:
                recent_avg = values[-7:].mean()
                previous_avg = values[-14:-7].mean()
                trend_direction = "rising" if recent_avg > previous_avg else "falling"
                trend_strength = abs(recent_avg - previous_avg) / previous_avg * 100
            else:
                trend_direction = "stable"
                trend_strength = 0
            
            result = {
                'keyword': keyword,
                'region': region,
                'current_interest': int(current_value),
                'avg_interest': round(avg_value, 1),
                'max_interest': int(max_value),
                'min_interest': int(min_value),
                'trend_direction': trend_direction,
                'trend_strength': round(trend_strength, 1),
                'timeframe': timeframe,
                'last_updated': datetime.now()
            }
            
            logger.info(f"📈 Tendencia para '{keyword}' ({region}): "
                       f"{trend_direction} ({trend_strength:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo tendencias para '{keyword}': {e}")
            return None
    
    def analyze_multiple_keywords(self, keywords: List[str], 
                                  region: str = 'US') -> pd.DataFrame:
        """
        Analizar tendencias de múltiples keywords
        
        Args:
            keywords: Lista de keywords
            region: Región a analizar
        
        Returns:
            DataFrame con análisis de todos los keywords
        """
        results = []
        
        for keyword in keywords:
            trend = self.get_keyword_trend(keyword, region=region)
            if trend:
                results.append(trend)
        
        if results:
            df = pd.DataFrame(results)
            df = df.sort_values('current_interest', ascending=False)
            return df
        else:
            return pd.DataFrame()
    
    def predict_seasonal_interest(self, keyword: str, region: str = 'US') -> Dict:
        """
        Predecir interés estacional (útil para keywords religiosos)
        
        Args:
            keyword: Keyword a analizar
            region: Región
        
        Returns:
            Diccionario con predicción estacional
        """
        if not self.google_trends_enabled:
            return {}
        
        try:
            # Obtener datos de último año
            self.pytrends.build_payload(
                kw_list=[keyword],
                timeframe='today 12-m',
                geo=region
            )
            
            interest = self.pytrends.interest_over_time()
            
            if interest.empty:
                return {}
            
            # Detectar picos estacionales
            values = interest[keyword].values
            dates = interest.index
            
            # Encontrar meses con mayor interés
            monthly_avg = []
            for month in range(1, 13):
                month_data = [values[i] for i, d in enumerate(dates) if d.month == month]
                if month_data:
                    monthly_avg.append({
                        'month': month,
                        'month_name': datetime(2000, month, 1).strftime('%B'),
                        'avg_interest': round(sum(month_data) / len(month_data), 1)
                    })
            
            # Ordenar por interés
            monthly_avg.sort(key=lambda x: x['avg_interest'], reverse=True)
            
            # Detectar si es keyword estacional (variación >30%)
            if monthly_avg:
                max_interest = monthly_avg[0]['avg_interest']
                min_interest = monthly_avg[-1]['avg_interest']
                variation = (max_interest - min_interest) / min_interest * 100 if min_interest > 0 else 0
                
                is_seasonal = variation > 30
                
                return {
                    'keyword': keyword,
                    'is_seasonal': is_seasonal,
                    'variation': round(variation, 1),
                    'peak_months': [m['month_name'] for m in monthly_avg[:3]],
                    'low_months': [m['month_name'] for m in monthly_avg[-3:]],
                    'monthly_data': monthly_avg
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error en análisis estacional: {e}")
            return {}
    
    def get_ai_keyword_insights(self, keyword: str, context: str = "") -> Optional[str]:
        """
        Obtener insights cualitativos usando IA
        
        Args:
            keyword: Keyword a analizar
            context: Contexto adicional (ej: "app de biblia para niños")
        
        Returns:
            Texto con insights generados por IA
        """
        if not self.ai_enabled:
            return None
        
        try:
            model = self.config['trends']['ai_analysis']['model']
            
            prompt = f"""Analiza el siguiente keyword para ASO (App Store Optimization) de una app:
            
Keyword: "{keyword}"
Contexto: {context if context else "App de historias bíblicas en audio"}

Proporciona:
1. ¿Es un buen keyword para ASO? (relevancia, volumen potencial)
2. ¿Tiene estacionalidad? (Navidad, Semana Santa, etc.)
3. ¿Qué tipo de usuarios lo buscarían?
4. Sugerencias para optimizar este keyword

Responde de forma concisa (máx 200 palabras)."""
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Eres un experto en ASO y marketing de apps."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            insights = response.choices[0].message.content.strip()
            logger.info(f"🤖 Insights IA generados para '{keyword}'")
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo insights IA: {e}")
            return None
    
    def analyze_rank_history(self, history_df: pd.DataFrame, 
                            keyword: str, country: str) -> Dict:
        """
        Analizar histórico de rankings para un keyword específico
        
        Args:
            history_df: DataFrame con histórico completo
            keyword: Keyword a analizar
            country: País
        
        Returns:
            Diccionario con análisis
        """
        # Filtrar datos
        data = history_df[
            (history_df['keyword'] == keyword) &
            (history_df['country'] == country) &
            (history_df['rank'] < 250)  # Solo rankings visibles
        ].sort_values('date')
        
        if len(data) < 2:
            return {'error': 'Datos insuficientes'}
        
        # Calcular estadísticas
        ranks = data['rank'].values
        current_rank = ranks[-1]
        best_rank = ranks.min()
        worst_rank = ranks.max()
        avg_rank = ranks.mean()
        
        # Tendencia (últimos 7 días)
        if len(ranks) >= 7:
            recent_trend = ranks[-7:].mean()
            previous_trend = ranks[-14:-7].mean() if len(ranks) >= 14 else avg_rank
            trend = "improving" if recent_trend < previous_trend else "declining"
        else:
            trend = "stable"
        
        # Volatilidad (desviación estándar)
        volatility = ranks.std()
        
        return {
            'keyword': keyword,
            'country': country,
            'current_rank': int(current_rank),
            'best_rank': int(best_rank),
            'worst_rank': int(worst_rank),
            'avg_rank': round(avg_rank, 1),
            'trend': trend,
            'volatility': round(volatility, 1),
            'data_points': len(data),
            'first_tracked': data.iloc[0]['date'],
            'last_tracked': data.iloc[-1]['date']
        }
    
    def get_recommendations(self, history_df: pd.DataFrame, 
                           trends_enabled: bool = False) -> List[str]:
        """
        Generar recomendaciones basadas en análisis
        
        Args:
            history_df: DataFrame con histórico
            trends_enabled: Si están habilitados los análisis de tendencias
        
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        if len(history_df) == 0:
            return ["⚠️ No hay suficientes datos históricos para generar recomendaciones"]
        
        # Analizar últimos datos
        latest = history_df.sort_values('date', ascending=False).iloc[0]['date']
        latest_data = history_df[history_df['date'] == latest]
        
        # Recomendación 1: Keywords invisibles
        invisible = latest_data[latest_data['rank'] >= 250]
        if len(invisible) > 0:
            recommendations.append(
                f"🔍 Tienes {len(invisible)} keywords no visibles en top 250. "
                f"Considera reemplazarlos o mejorar metadata para: {', '.join(invisible['keyword'].head(3).values)}"
            )
        
        # Recomendación 2: Keywords con buen ranking
        visible = latest_data[latest_data['rank'] < 100]
        if len(visible) > 0:
            top_kw = visible.nsmallest(1, 'rank').iloc[0]
            recommendations.append(
                f"🏆 '{top_kw['keyword']}' está en posición #{int(top_kw['rank'])}. "
                f"Considera reforzarlo en title/subtitle."
            )
        
        # Recomendación 3: Keywords volátiles
        for kw in latest_data['keyword'].unique():
            kw_data = history_df[history_df['keyword'] == kw]['rank']
            if len(kw_data) >= 7:
                volatility = kw_data.std()
                if volatility > 20:
                    recommendations.append(
                        f"⚠️ '{kw}' tiene alta volatilidad (±{volatility:.0f} posiciones). "
                        f"Monitoriza competencia o cambios de algoritmo."
                    )
        
        if len(recommendations) == 0:
            recommendations.append("✅ Todo parece estable. Continúa monitorizando.")
        
        return recommendations[:5]  # Máximo 5 recomendaciones


def test_analyzer():
    """Función de test para probar el analizador"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    analyzer = TrendAnalyzer(config)
    
    # Test con un keyword
    test_keyword = "bible stories"
    
    print(f"\n🧪 Analizando tendencias para: '{test_keyword}'")
    
    if analyzer.google_trends_enabled:
        trend = analyzer.get_keyword_trend(test_keyword, region='US')
        if trend:
            print(f"\n📊 Resultados:")
            print(f"   Interés actual: {trend['current_interest']}/100")
            print(f"   Promedio: {trend['avg_interest']}/100")
            print(f"   Tendencia: {trend['trend_direction']} ({trend['trend_strength']}%)")
        
        # Análisis estacional
        seasonal = analyzer.predict_seasonal_interest(test_keyword, region='US')
        if seasonal:
            print(f"\n📅 Análisis estacional:")
            print(f"   ¿Es estacional? {'Sí' if seasonal['is_seasonal'] else 'No'}")
            print(f"   Variación: {seasonal['variation']}%")
            print(f"   Meses pico: {', '.join(seasonal['peak_months'])}")
    else:
        print("⚠️ Google Trends no disponible")


if __name__ == "__main__":
    test_analyzer()
