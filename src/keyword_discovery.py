#!/usr/bin/env python3
"""
Keyword Discovery Engine - Descubrimiento automático de keywords
Encuentra nuevos keywords potenciales y oportunidades
"""

import requests
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import time
import random

logger = logging.getLogger(__name__)


class KeywordDiscoveryEngine:
    """Motor de descubrimiento de keywords"""
    
    def __init__(self, config: dict):
        self.config = config
        self.app_id = config['app']['id']
        self.current_keywords = set(config['keywords'])
        self.discoveries_file = Path('data/keyword_discoveries.csv')
        self.discoveries_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar descubrimientos previos
        self.discoveries_df = self._load_discoveries()
        
        logger.info("✅ KeywordDiscoveryEngine inicializado")
    
    def _load_discoveries(self) -> pd.DataFrame:
        """Cargar descubrimientos previos"""
        if self.discoveries_file.exists():
            try:
                df = pd.read_csv(self.discoveries_file)
                df['discovered_date'] = pd.to_datetime(df['discovered_date'])
                logger.info(f"📂 Descubrimientos previos: {len(df)}")
                return df
            except Exception as e:
                logger.warning(f"⚠️  Error cargando descubrimientos: {e}")
                return self._create_empty_discoveries()
        return self._create_empty_discoveries()
    
    def _create_empty_discoveries(self) -> pd.DataFrame:
        """Crear DataFrame vacío"""
        return pd.DataFrame(columns=[
            'keyword', 'discovered_date', 'source', 'estimated_volume',
            'difficulty', 'relevance_score', 'opportunity_score',
            'found_in_competitor', 'competitor_name', 'competitor_rank',
            'status', 'notes'
        ])
    
    def discover_from_apple_suggest(self, seed_keywords: List[str]) -> List[Dict]:
        """
        Descubrir keywords usando Apple Search Suggest API
        
        Args:
            seed_keywords: Keywords semilla para expandir
        
        Returns:
            Lista de keywords descubiertas
        """
        discovered = []
        
        # Apple Search Suggest endpoint (no oficial, puede cambiar)
        suggest_url = "https://search.itunes.apple.com/WebObjects/MZSearchHints.woa/wa/hints"
        
        for seed in seed_keywords:
            try:
                logger.info(f"🔍 Buscando sugerencias para '{seed}'...")
                
                # Añadir variaciones comunes
                variations = [
                    seed,
                    f"{seed} app",
                    f"{seed} free",
                    f"best {seed}",
                    f"{seed} for kids"
                ]
                
                for query in variations:
                    time.sleep(random.uniform(1, 2))  # Rate limiting
                    
                    params = {
                        'clientApplication': 'Software',
                        'term': query
                    }
                    
                    try:
                        response = requests.get(suggest_url, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            hints = data.get('hints', [])
                            
                            for hint in hints:
                                keyword = hint.get('term', '').lower().strip()
                                
                                # Filtrar keywords ya conocidas
                                if keyword and keyword not in self.current_keywords:
                                    discovered.append({
                                        'keyword': keyword,
                                        'source': 'apple_suggest',
                                        'seed': seed,
                                        'query': query
                                    })
                    
                    except Exception as e:
                        logger.debug(f"Error en sugerencia '{query}': {e}")
                        continue
            
            except Exception as e:
                logger.error(f"❌ Error procesando '{seed}': {e}")
                continue
        
        # Eliminar duplicados
        unique_keywords = {}
        for item in discovered:
            kw = item['keyword']
            if kw not in unique_keywords:
                unique_keywords[kw] = item
        
        logger.info(f"✅ Descubiertas {len(unique_keywords)} keywords desde Apple Suggest")
        return list(unique_keywords.values())
    
    def discover_from_competitors(self, competitor_data: pd.DataFrame, 
                                 min_competitor_rank: int = 50) -> List[Dict]:
        """
        Descubrir keywords analizando dónde rankean competidores
        
        Args:
            competitor_data: DataFrame con datos de competidores
            min_competitor_rank: Rank mínimo para considerar keyword
        
        Returns:
            Lista de keywords descubiertas
        """
        discovered = []
        
        if len(competitor_data) == 0:
            return discovered
        
        # Keywords donde competidores rankean bien pero tú no
        competitor_keywords = set(competitor_data['keyword'].unique())
        new_keywords = competitor_keywords - self.current_keywords
        
        for keyword in new_keywords:
            # Obtener mejores competidores en esa keyword
            kw_data = competitor_data[competitor_data['keyword'] == keyword]
            top_competitors = kw_data[kw_data['position'] <= min_competitor_rank].sort_values('position')
            
            if len(top_competitors) > 0:
                best_comp = top_competitors.iloc[0]
                
                discovered.append({
                    'keyword': keyword,
                    'source': 'competitor_analysis',
                    'found_in_competitor': best_comp['app_name'],
                    'competitor_rank': int(best_comp['position']),
                    'competitor_rating': float(best_comp.get('rating', 0))
                })
        
        logger.info(f"✅ Descubiertas {len(discovered)} keywords desde competidores")
        return discovered
    
    def discover_long_tail_variations(self, base_keywords: List[str]) -> List[Dict]:
        """
        Generar variaciones long-tail de keywords existentes
        
        Args:
            base_keywords: Keywords base
        
        Returns:
            Lista de variaciones descubiertas
        """
        discovered = []
        
        # Modifiers comunes para long-tail
        modifiers = {
            'intent': ['free', 'best', 'top', 'popular', 'new'],
            'user': ['kids', 'children', 'adults', 'family', 'toddler'],
            'quality': ['calming', 'relaxing', 'peaceful', 'soothing', 'gentle'],
            'time': ['bedtime', 'morning', 'daily', 'nightly', 'evening'],
            'feature': ['audio', 'offline', 'ad-free', 'interactive', 'guided']
        }
        
        for base in base_keywords:
            base_words = base.split()
            
            # Evitar duplicar modifiers que ya están
            existing_modifiers = set(base_words)
            
            for category, mod_list in modifiers.items():
                for modifier in mod_list:
                    # Solo si no está ya en la keyword
                    if modifier not in existing_modifiers:
                        # Variaciones: modifier + base / base + modifier
                        variations = [
                            f"{modifier} {base}",
                            f"{base} {modifier}",
                        ]
                        
                        for variation in variations:
                            # Evitar frases muy largas (>6 palabras)
                            if len(variation.split()) <= 6:
                                if variation not in self.current_keywords:
                                    discovered.append({
                                        'keyword': variation,
                                        'source': 'long_tail_generation',
                                        'base': base,
                                        'modifier': modifier,
                                        'category': category
                                    })
        
        # Eliminar duplicados
        unique_keywords = {}
        for item in discovered:
            kw = item['keyword']
            if kw not in unique_keywords:
                unique_keywords[kw] = item
        
        logger.info(f"✅ Generadas {len(unique_keywords)} variaciones long-tail")
        return list(unique_keywords.values())
    
    def estimate_opportunity_score(self, keyword: str, metadata: Dict) -> int:
        """
        Estimar opportunity score 0-100 para una keyword descubierta
        
        Args:
            keyword: Keyword a evaluar
            metadata: Metadata adicional (competidor, source, etc.)
        
        Returns:
            Score 0-100
        """
        score = 0
        
        # Base score según longitud (long-tail = más fácil)
        word_count = len(keyword.split())
        if word_count == 2:
            score += 20
        elif word_count == 3:
            score += 30
        elif word_count >= 4:
            score += 40  # Long-tail = mejor oportunidad
        
        # Boost si viene de competidor bien posicionado
        if metadata.get('source') == 'competitor_analysis':
            comp_rank = metadata.get('competitor_rank', 999)
            if comp_rank <= 10:
                score += 30  # Competidor en top 10 = keyword valiosa
            elif comp_rank <= 30:
                score += 20
            else:
                score += 10
        
        # Boost si viene de Apple Suggest (indica demanda)
        if metadata.get('source') == 'apple_suggest':
            score += 25
        
        # Penalizar keywords genéricas muy cortas (muy competidas)
        if word_count == 1:
            score -= 20
        
        # Boost por relevancia semántica (palabras clave de tu app)
        app_keywords = ['bible', 'audio', 'sleep', 'stories', 'bedtime', 'chat', 'kids']
        keyword_lower = keyword.lower()
        matches = sum(1 for kw in app_keywords if kw in keyword_lower)
        score += matches * 5
        
        # Clamp 0-100
        return max(0, min(score, 100))
    
    def estimate_difficulty(self, keyword: str, metadata: Dict) -> str:
        """
        Estimar dificultad de rankear
        
        Returns:
            'low', 'medium', 'high'
        """
        word_count = len(keyword.split())
        
        # Long-tail = más fácil
        if word_count >= 4:
            return 'low'
        
        # Si competidor rankea muy arriba = competido
        if metadata.get('competitor_rank', 999) <= 5:
            return 'high'
        elif metadata.get('competitor_rank', 999) <= 20:
            return 'medium'
        
        # Keywords cortas genéricas = difícil
        if word_count <= 2:
            return 'high'
        
        return 'medium'
    
    def save_discoveries(self, discoveries: List[Dict]):
        """Guardar nuevos descubrimientos"""
        if not discoveries:
            return
        
        new_records = []
        
        for disc in discoveries:
            keyword = disc['keyword']
            
            # Evitar duplicados
            if len(self.discoveries_df[self.discoveries_df['keyword'] == keyword]) > 0:
                continue
            
            # Calcular scores
            opp_score = self.estimate_opportunity_score(keyword, disc)
            difficulty = self.estimate_difficulty(keyword, disc)
            
            # Estimar volumen (simplificado)
            word_count = len(keyword.split())
            if word_count >= 5:
                volume = 20
            elif word_count == 4:
                volume = 50
            elif word_count == 3:
                volume = 150
            else:
                volume = 300
            
            new_records.append({
                'keyword': keyword,
                'discovered_date': datetime.now(),
                'source': disc.get('source', 'unknown'),
                'estimated_volume': volume,
                'difficulty': difficulty,
                'relevance_score': 0,  # TODO: calcular relevancia
                'opportunity_score': opp_score,
                'found_in_competitor': disc.get('found_in_competitor', ''),
                'competitor_name': disc.get('found_in_competitor', ''),
                'competitor_rank': disc.get('competitor_rank', 0),
                'status': 'discovered',  # discovered, testing, active, rejected
                'notes': ''
            })
        
        if new_records:
            new_df = pd.DataFrame(new_records)
            self.discoveries_df = pd.concat([self.discoveries_df, new_df], ignore_index=True)
            self.discoveries_df.to_csv(self.discoveries_file, index=False)
            logger.info(f"💾 Guardados {len(new_records)} nuevos descubrimientos")
    
    def get_top_opportunities(self, limit: int = 20, min_score: int = 50) -> pd.DataFrame:
        """
        Obtener top oportunidades descubiertas
        
        Args:
            limit: Número máximo de resultados
            min_score: Score mínimo para incluir
        
        Returns:
            DataFrame ordenado por opportunity_score
        """
        if len(self.discoveries_df) == 0:
            return pd.DataFrame()
        
        # Filtrar por score y status
        filtered = self.discoveries_df[
            (self.discoveries_df['opportunity_score'] >= min_score) &
            (self.discoveries_df['status'] == 'discovered')
        ]
        
        # Ordenar por score
        top = filtered.sort_values('opportunity_score', ascending=False).head(limit)
        
        return top
    
    def run_full_discovery(self, competitor_data: pd.DataFrame = None) -> Dict:
        """
        Ejecutar descubrimiento completo
        
        Args:
            competitor_data: DataFrame con datos de competidores (opcional)
        
        Returns:
            Resumen de descubrimientos
        """
        logger.info("🔍 Iniciando descubrimiento completo de keywords...")
        
        all_discoveries = []
        
        # 1. Apple Suggest (top keywords como semillas)
        seed_keywords = list(self.current_keywords)[:10]  # Solo top 10 para no saturar
        apple_discoveries = self.discover_from_apple_suggest(seed_keywords)
        all_discoveries.extend(apple_discoveries)
        
        # 2. Competitor Analysis (si hay datos)
        if competitor_data is not None and len(competitor_data) > 0:
            comp_discoveries = self.discover_from_competitors(competitor_data)
            all_discoveries.extend(comp_discoveries)
        
        # 3. Long-tail variations
        longtail_discoveries = self.discover_long_tail_variations(seed_keywords)
        all_discoveries.extend(longtail_discoveries)
        
        # Guardar descubrimientos
        self.save_discoveries(all_discoveries)
        
        # Obtener top oportunidades
        top_opps = self.get_top_opportunities(limit=20)
        
        summary = {
            'total_discovered': len(all_discoveries),
            'sources': {
                'apple_suggest': len(apple_discoveries),
                'competitors': len([d for d in all_discoveries if d.get('source') == 'competitor_analysis']),
                'long_tail': len(longtail_discoveries)
            },
            'top_opportunities': top_opps.to_dict('records') if len(top_opps) > 0 else []
        }
        
        logger.info(f"✅ Descubrimiento completado: {len(all_discoveries)} keywords nuevas")
        
        return summary
    
    def format_discovery_report(self, summary: Dict) -> str:
        """Formatear reporte de descubrimientos para Telegram"""
        msg = "🔍 *KEYWORD DISCOVERY REPORT*\n\n"
        
        msg += f"**Total descubiertas:** {summary['total_discovered']}\n"
        msg += f"**Fuentes:**\n"
        for source, count in summary['sources'].items():
            msg += f"  • {source}: {count}\n"
        
        msg += f"\n🎯 *TOP 10 OPORTUNIDADES:*\n\n"
        
        top_opps = summary['top_opportunities'][:10]
        for i, opp in enumerate(top_opps, 1):
            keyword = opp['keyword']
            score = opp['opportunity_score']
            difficulty = opp['difficulty']
            volume = opp['estimated_volume']
            
            emoji = '🟢' if difficulty == 'low' else '🟡' if difficulty == 'medium' else '🔴'
            
            msg += f"{i}. `{keyword}`\n"
            msg += f"   Score: {score}/100 | {emoji} {difficulty} | vol:{volume}\n"
            
            if opp.get('found_in_competitor'):
                msg += f"   Found in: {opp['found_in_competitor']} (#{opp['competitor_rank']})\n"
            
            msg += "\n"
        
        msg += f"_Revisar data/keyword_discoveries.csv para lista completa_"
        
        return msg


def main():
    """Test del discovery engine"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    engine = KeywordDiscoveryEngine(config)
    
    print("🧪 Testing Keyword Discovery Engine\n")
    
    # Test long-tail generation
    print("1️⃣ Testing long-tail generation...")
    longtail = engine.discover_long_tail_variations(['bible stories', 'audio bible'])
    print(f"   Generated {len(longtail)} variations")
    print(f"   Examples: {[d['keyword'] for d in longtail[:5]]}")
    
    # Test opportunity scoring
    print("\n2️⃣ Testing opportunity scoring...")
    test_kw = longtail[0] if longtail else {'keyword': 'calming bible stories'}
    score = engine.estimate_opportunity_score(test_kw['keyword'], test_kw)
    print(f"   '{test_kw['keyword']}' → Score: {score}/100")
    
    # Save and get top
    engine.save_discoveries(longtail[:20])
    top = engine.get_top_opportunities(limit=5)
    
    print(f"\n3️⃣ Top 5 Opportunities:")
    for _, row in top.iterrows():
        print(f"   • {row['keyword']} (score: {row['opportunity_score']})")


if __name__ == "__main__":
    main()
