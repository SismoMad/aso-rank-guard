#!/usr/bin/env python3
"""
Competitor Tracker - Monitorización de competidores
Rastrea los top 5 competidores por keyword y detecta cambios
"""

import requests
import pandas as pd
import time
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

logger = logging.getLogger(__name__)


class CompetitorTracker:
    """Rastreador de competidores en App Store"""
    
    def __init__(self, config: dict):
        self.config = config
        self.app_id = config['app']['id']
        self.competitors_file = Path('data/competitors.csv')
        self.competitors_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar histórico de competidores
        self.history_df = self._load_history()
        
        logger.info("✅ CompetitorTracker inicializado")
    
    def _load_history(self) -> pd.DataFrame:
        """Cargar histórico de competidores"""
        if self.competitors_file.exists():
            try:
                df = pd.read_csv(self.competitors_file)
                df['date'] = pd.to_datetime(df['date'])
                logger.info(f"📂 Histórico competidores: {len(df)} registros")
                return df
            except Exception as e:
                logger.warning(f"⚠️  Error cargando histórico: {e}")
                return self._create_empty_history()
        return self._create_empty_history()
    
    def _create_empty_history(self) -> pd.DataFrame:
        """Crear DataFrame vacío"""
        return pd.DataFrame(columns=[
            'date', 'keyword', 'country', 'position', 'app_id', 
            'app_name', 'developer', 'rating', 'rating_count', 'price'
        ])
    
    def get_top_competitors(self, keyword: str, country: str, limit: int = 5) -> List[Dict]:
        """
        Obtener top N apps para un keyword
        
        Args:
            keyword: Keyword a buscar
            country: País (US, ES, etc.)
            limit: Número de apps a obtener
        
        Returns:
            Lista de competidores con metadata
        """
        try:
            base_url = self.config['api']['itunes']['base_url']
            timeout = self.config['api']['itunes']['timeout']
            
            params = {
                'term': keyword,
                'country': country,
                'entity': 'software',
                'limit': 250  # Buscar amplio para encontrar competidores
            }
            
            # Rate limiting
            time.sleep(random.uniform(2, 4))
            
            response = requests.get(base_url, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            results = data.get('results', [])
            
            competitors = []
            position = 0
            
            for app in results:
                position += 1
                
                # Extraer metadata
                app_id = app.get('trackId')
                app_name = app.get('trackName', 'Unknown')
                developer = app.get('artistName', 'Unknown')
                rating = app.get('averageUserRating', 0)
                rating_count = app.get('userRatingCount', 0)
                price = app.get('price', 0)
                
                competitors.append({
                    'position': position,
                    'app_id': app_id,
                    'app_name': app_name,
                    'developer': developer,
                    'rating': rating,
                    'rating_count': rating_count,
                    'price': price,
                    'is_own_app': app_id == self.app_id
                })
                
                # Parar cuando tengamos suficientes competidores (excluyendo nuestra app)
                competitor_count = len([c for c in competitors if not c['is_own_app']])
                if competitor_count >= limit:
                    break
            
            logger.debug(f"✅ Obtenidos {len(competitors)} competidores para '{keyword}' ({country})")
            return competitors
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo competidores para '{keyword}': {e}")
            return []
    
    def track_all_competitors(self, keywords: List[str] = None, countries: List[str] = None) -> pd.DataFrame:
        """
        Rastrear competidores para todas las keywords
        
        Args:
            keywords: Lista de keywords (None = usar config)
            countries: Lista de países (None = usar config)
        
        Returns:
            DataFrame con resultados actuales
        """
        if keywords is None:
            keywords = self.config['keywords']
        if countries is None:
            countries = self.config['countries']
        
        logger.info(f"🚀 Rastreando competidores para {len(keywords)} keywords...")
        
        results = []
        total = len(keywords) * len(countries)
        current = 0
        
        for keyword in keywords:
            for country in countries:
                current += 1
                logger.info(f"[{current}/{total}] Analizando '{keyword}' en {country}...")
                
                competitors = self.get_top_competitors(keyword, country, limit=5)
                
                for comp in competitors:
                    results.append({
                        'date': datetime.now(),
                        'keyword': keyword,
                        'country': country,
                        'position': comp['position'],
                        'app_id': comp['app_id'],
                        'app_name': comp['app_name'],
                        'developer': comp['developer'],
                        'rating': comp['rating'],
                        'rating_count': comp['rating_count'],
                        'price': comp['price']
                    })
        
        results_df = pd.DataFrame(results)
        logger.info(f"✅ Rastreo completado: {len(results)} competidores registrados")
        
        return results_df
    
    def save_results(self, results_df: pd.DataFrame):
        """Guardar resultados en histórico"""
        try:
            # Eliminar duplicados del mismo día
            today = datetime.now().date()
            
            if len(self.history_df) > 0:
                self.history_df['date'] = pd.to_datetime(self.history_df['date'])
                self.history_df['date_only'] = self.history_df['date'].dt.date
                
                before_count = len(self.history_df)
                self.history_df = self.history_df[self.history_df['date_only'] != today]
                removed = before_count - len(self.history_df)
                
                if removed > 0:
                    logger.info(f"🧹 Eliminados {removed} registros duplicados del mismo día")
                
                self.history_df = self.history_df.drop(columns=['date_only'], errors='ignore')
            
            # Concatenar nuevos resultados
            self.history_df = pd.concat([self.history_df, results_df], ignore_index=True)
            
            # Guardar
            self.history_df.to_csv(self.competitors_file, index=False)
            logger.info(f"💾 Competidores guardados en {self.competitors_file}")
            
        except Exception as e:
            logger.error(f"❌ Error guardando competidores: {e}")
    
    def detect_competitor_changes(self) -> List[Dict]:
        """
        Detectar cambios significativos en competidores
        
        Returns:
            Lista de insights sobre competidores
        """
        if len(self.history_df) < 2:
            return []
        
        insights = []
        
        # Obtener últimas 2 mediciones
        unique_dates = sorted(self.history_df['date'].dt.date.unique())
        if len(unique_dates) < 2:
            return []
        
        latest_date = unique_dates[-1]
        previous_date = unique_dates[-2]
        
        latest = self.history_df[self.history_df['date'].dt.date == latest_date]
        previous = self.history_df[self.history_df['date'].dt.date == previous_date]
        
        # Detectar nuevos entrantes en top 5
        for keyword in latest['keyword'].unique():
            latest_kw = latest[latest['keyword'] == keyword]
            previous_kw = previous[previous['keyword'] == keyword]
            
            if len(previous_kw) == 0:
                continue
            
            # Apps que están ahora en top 5 pero no estaban antes
            latest_apps = set(latest_kw['app_id'].values)
            previous_apps = set(previous_kw['app_id'].values)
            
            new_apps = latest_apps - previous_apps
            left_apps = previous_apps - latest_apps
            
            for app_id in new_apps:
                app_data = latest_kw[latest_kw['app_id'] == app_id].iloc[0]
                insights.append({
                    'type': 'new_entrant',
                    'keyword': keyword,
                    'app_name': app_data['app_name'],
                    'position': int(app_data['position']),
                    'rating': float(app_data['rating']),
                    'message': f"🆕 '{app_data['app_name']}' entró en top 5 de '{keyword}' (#{app_data['position']})"
                })
            
            for app_id in left_apps:
                app_data = previous_kw[previous_kw['app_id'] == app_id].iloc[0]
                insights.append({
                    'type': 'left_top5',
                    'keyword': keyword,
                    'app_name': app_data['app_name'],
                    'message': f"👋 '{app_data['app_name']}' salió del top 5 de '{keyword}'"
                })
            
            # Detectar movimientos grandes dentro del top 5
            for app_id in latest_apps & previous_apps:
                latest_pos = latest_kw[latest_kw['app_id'] == app_id].iloc[0]['position']
                previous_pos = previous_kw[previous_kw['app_id'] == app_id].iloc[0]['position']
                diff = previous_pos - latest_pos  # Positivo = subió
                
                if abs(diff) >= 3:  # Cambio significativo
                    app_name = latest_kw[latest_kw['app_id'] == app_id].iloc[0]['app_name']
                    emoji = '📈' if diff > 0 else '📉'
                    insights.append({
                        'type': 'position_change',
                        'keyword': keyword,
                        'app_name': app_name,
                        'prev_position': int(previous_pos),
                        'current_position': int(latest_pos),
                        'diff': int(diff),
                        'message': f"{emoji} '{app_name}' en '{keyword}': #{previous_pos}→#{latest_pos}"
                    })
        
        return insights
    
    def get_competitor_summary(self, keyword: str = None) -> Dict:
        """
        Obtener resumen de competidores actuales
        
        Args:
            keyword: Keyword específica (None = todas)
        
        Returns:
            Diccionario con estadísticas
        """
        if len(self.history_df) == 0:
            return {}
        
        latest_date = self.history_df['date'].max()
        latest = self.history_df[self.history_df['date'] == latest_date]
        
        if keyword:
            latest = latest[latest['keyword'] == keyword]
        
        # Top competidores recurrentes
        competitor_counts = latest['app_name'].value_counts().head(10)
        
        # Promedio ratings
        avg_rating = latest['rating'].mean()
        avg_rating_count = latest['rating_count'].mean()
        
        return {
            'last_update': latest_date,
            'total_tracked': len(latest),
            'unique_competitors': len(latest['app_id'].unique()),
            'avg_rating': f"{avg_rating:.2f}",
            'avg_rating_count': int(avg_rating_count),
            'top_competitors': competitor_counts.to_dict()
        }
    
    def find_correlation_with_drops(self, your_drops: List[Dict]) -> List[Dict]:
        """
        Correlacionar caídas tuyas con subidas de competidores
        
        Args:
            your_drops: Lista de tus caídas detectadas
        
        Returns:
            Lista de correlaciones encontradas
        """
        correlations = []
        competitor_changes = self.detect_competitor_changes()
        
        for drop in your_drops:
            keyword = drop['keyword']
            
            # Buscar competidores que subieron en esa keyword
            comp_rises = [c for c in competitor_changes 
                         if c['keyword'] == keyword and 
                         c['type'] == 'position_change' and 
                         c.get('diff', 0) > 0]
            
            if comp_rises:
                # Tomar el que más subió
                top_rise = max(comp_rises, key=lambda x: x['diff'])
                
                correlations.append({
                    'your_keyword': keyword,
                    'your_drop': drop['diff'],
                    'competitor_name': top_rise['app_name'],
                    'competitor_rise': top_rise['diff'],
                    'message': f"⚠️ Tu caída en '{keyword}' coincide con subida de '{top_rise['app_name']}' ({top_rise['diff']:+d} posiciones)"
                })
        
        return correlations


def main():
    """Test del competitor tracker"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    tracker = CompetitorTracker(config)
    
    # Test con algunas keywords
    test_keywords = config['keywords'][:3]  # Solo 3 para test rápido
    
    print("🧪 Testing Competitor Tracker\n")
    
    results = tracker.track_all_competitors(keywords=test_keywords)
    print(f"\n📊 Rastreados {len(results)} competidores")
    
    tracker.save_results(results)
    
    # Mostrar resumen
    summary = tracker.get_competitor_summary()
    print("\n📈 RESUMEN:")
    print(f"Top Competidores: {list(summary.get('top_competitors', {}).keys())[:5]}")
    
    # Detectar cambios
    changes = tracker.detect_competitor_changes()
    if changes:
        print(f"\n🔍 CAMBIOS DETECTADOS: {len(changes)}")
        for change in changes[:5]:
            print(f"  • {change['message']}")


if __name__ == "__main__":
    main()
