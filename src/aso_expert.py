#!/usr/bin/env python3
"""
ASO Expert Analyzer - Análisis profundo PRO con evidencia y scoring
"""

import pandas as pd
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Tipos de intención de búsqueda"""
    INFORMATIONAL = "informational"  # "what is", "meaning", "stories"
    HABIT_ROUTINE = "habit_routine"   # "daily", "plan", "bedtime"
    AUDIO = "audio"                   # "audio", "listen", "podcast"
    KIDS_FAMILY = "kids_family"       # "for kids", "family", "children"
    CHAT_AI = "chat_ai"               # "chat", "ask", "ai"
    LEARNING = "learning"             # "study", "learn", "course"
    SLEEP_RELAX = "sleep_relax"       # "sleep", "calm", "relax"
    FREE = "free"                     # "free", "gratis"
    UNKNOWN = "unknown"


class Severity(Enum):
    """Niveles de severidad para amenazas"""
    CRITICAL = "CRITICAL"  # top10 → >20 o caída >15 con volumen alto
    HIGH = "HIGH"          # top30 → >60 o caída sostenida
    MEDIUM = "MEDIUM"      # caída 5-10 con volumen medio
    LOW = "LOW"            # ruido normal (±5)


@dataclass
class KeywordEvidence:
    """Evidencia completa para cada keyword"""
    keyword: str
    rank_now: int
    rank_prev: Optional[int]
    delta: Optional[int]
    volume_proxy: int  # Estimado por longitud y tipo
    difficulty: str    # "low", "medium", "high"
    intent: str
    relevance: int     # 0-100
    country: str
    field_suggestion: str  # "title", "subtitle", "keywords", "description"
    action: str
    confidence: str    # "high", "medium", "low"
    
@dataclass
class OpportunityScore:
    """Score de oportunidad 0-100"""
    keyword: str
    total_score: int
    impact: int        # 0-40
    feasibility: int   # 0-30
    relevance: int     # 0-20
    risk: int          # -10 to 0
    bucket: str        # "DO NOW", "NEXT", "WATCH", "IGNORE"
    evidence: KeywordEvidence


class ASOExpert:
    """Analizador experto de ASO con scoring y evidencia"""
    
    # Volumen proxy basado en tipo de keyword (sin API)
    VOLUME_PATTERNS = {
        'brand': 500,        # "biblenow"
        'generic_2w': 300,   # "bible chat"
        'generic_3w': 150,   # "audio bible stories"
        'long_tail': 50,     # "kids calming audio bible"
        'very_long': 20      # >5 palabras
    }
    
    # Patrones de intención
    INTENT_PATTERNS = {
        Intent.INFORMATIONAL: ['stories', 'story', 'tales', 'meaning', 'what is'],
        Intent.HABIT_ROUTINE: ['daily', 'bedtime', 'morning', 'routine', 'plan'],
        Intent.AUDIO: ['audio', 'listen', 'podcast', 'sound', 'voice'],
        Intent.KIDS_FAMILY: ['kids', 'children', 'family', 'child', 'toddler'],
        Intent.CHAT_AI: ['chat', 'ai', 'ask', 'talk', 'conversation'],
        Intent.LEARNING: ['learn', 'study', 'education', 'course', 'lesson'],
        Intent.SLEEP_RELAX: ['sleep', 'calm', 'relax', 'peaceful', 'soothing'],
        Intent.FREE: ['free', 'gratis', 'no cost']
    }
    
    # Mapping de intención a acción
    INTENT_TO_ACTION = {
        Intent.INFORMATIONAL: {
            'field': 'description',
            'template': 'Add "Rich Bible Stories with {kw}" in first paragraph',
            'visual': 'Screenshots showing story library + content preview'
        },
        Intent.HABIT_ROUTINE: {
            'field': 'subtitle',
            'template': 'Add "{kw}" to subtitle emphasizing routine features',
            'visual': 'Screenshots showing daily plans, reminders, scheduling'
        },
        Intent.AUDIO: {
            'field': 'title',
            'template': 'Ensure "Audio" is prominent in title',
            'visual': 'Video demo + screenshots with audio player UI'
        },
        Intent.KIDS_FAMILY: {
            'field': 'subtitle',
            'template': 'Add "Safe for Kids" + "{kw}" to subtitle',
            'visual': 'Kid-friendly screenshots + parental controls'
        },
        Intent.CHAT_AI: {
            'field': 'subtitle',
            'template': 'Add "Chat with Bible AI" featuring {kw}',
            'visual': 'Chat demo screenshots + example questions'
        },
        Intent.SLEEP_RELAX: {
            'field': 'subtitle',
            'template': 'Add "Bedtime Bible & {kw}" to subtitle',
            'visual': 'Night mode UI + calming visuals'
        },
        Intent.LEARNING: {
            'field': 'description',
            'template': 'Highlight educational features for {kw}',
            'visual': 'Learning path screenshots'
        },
        Intent.FREE: {
            'field': 'subtitle',
            'template': 'Add "100% Free" prominently',
            'visual': 'Screenshot 1: "Totally Free" badge'
        }
    }
    
    def __init__(self, config: dict):
        self.config = config
        self.ranks_file = Path(config['storage']['ranks_file'])
        self.app_name = config['app']['name']
        self.brand_keywords = self._detect_brand_keywords()
    
    def _detect_brand_keywords(self) -> List[str]:
        """Detectar keywords de marca"""
        app_name_lower = self.app_name.lower()
        brand_words = app_name_lower.split()
        return [kw for kw in self.config['keywords'] 
                if any(brand in kw.lower() for brand in brand_words)]
    
    def _estimate_volume(self, keyword: str) -> int:
        """Estimar volumen de búsqueda (proxy sin API)"""
        kw_lower = keyword.lower()
        word_count = len(kw_lower.split())
        
        # Brand keywords
        if keyword in self.brand_keywords:
            return self.VOLUME_PATTERNS['brand']
        
        # Long tail (5+ palabras)
        if word_count >= 5:
            return self.VOLUME_PATTERNS['very_long']
        
        # 3-4 palabras
        if word_count >= 3:
            return self.VOLUME_PATTERNS['long_tail']
        
        # Generic 2-3 palabras
        # Boost si contiene términos populares
        popular_terms = ['bible', 'audio', 'chat', 'stories', 'sleep', 'kids']
        if any(term in kw_lower for term in popular_terms):
            return self.VOLUME_PATTERNS['generic_3w']
        
        return self.VOLUME_PATTERNS['generic_2w']
    
    def _detect_intent(self, keyword: str) -> Intent:
        """Detectar intención de búsqueda"""
        kw_lower = keyword.lower()
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            if any(pattern in kw_lower for pattern in patterns):
                return intent
        
        return Intent.UNKNOWN
    
    def _calculate_difficulty(self, rank: int, volume: int) -> str:
        """Calcular dificultad estimada"""
        # Heurística simple: rank alto + volumen alto = difícil
        if rank < 20 and volume > 200:
            return "high"
        elif rank < 50 and volume > 100:
            return "medium"
        elif rank > 150:
            return "high"  # Muy abajo = muy competido o irrelevante
        else:
            return "low"
    
    def _calculate_relevance(self, keyword: str, intent: Intent) -> int:
        """Calcular relevancia 0-100 basado en match con producto"""
        kw_lower = keyword.lower()
        score = 50  # Base
        
        # Product features (ajustar según tu app)
        core_features = {
            'audio': 30,
            'bible': 20,
            'stories': 20,
            'chat': 15,
            'sleep': 10,
            'kids': 10,
            'bedtime': 10,
            'daily': 5,
            'free': 5
        }
        
        for feature, points in core_features.items():
            if feature in kw_lower:
                score += points
        
        # Cap at 100
        return min(score, 100)
    
    def _suggest_field(self, rank: int, intent: Intent, relevance: int) -> str:
        """Sugerir qué campo optimizar"""
        # Top performers → mantener en title
        if rank <= 10:
            return "title (maintain)"
        
        # Quick wins → subtitle
        if 10 < rank <= 30:
            return "subtitle"
        
        # Intent-based
        if intent in self.INTENT_TO_ACTION:
            return self.INTENT_TO_ACTION[intent]['field']
        
        # Default
        if rank <= 50:
            return "keywords + description"
        else:
            return "description (low priority)"
    
    def analyze_comprehensive(self) -> Dict:
        """Análisis completo de ASO con insights profundos"""
        
        if not self.ranks_file.exists():
            return {'error': 'No hay datos históricos'}
        
        df = pd.read_csv(self.ranks_file)
        df['date'] = pd.to_datetime(df['date'])
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
        df['date_only'] = df['date'].dt.date
        
        # Análisis múltiple
        latest_analysis = self._analyze_current_state(df)
        trends_analysis = self._analyze_trends(df)
        opportunities = self._identify_opportunities(df)
        threats = self._identify_threats(df)
        recommendations = self._generate_recommendations(df, latest_analysis, trends_analysis)
        competitive_insights = self._competitive_analysis(df)
        
        return {
            'current_state': latest_analysis,
            'trends': trends_analysis,
            'opportunities': opportunities,
            'threats': threats,
            'recommendations': recommendations,
            'competitive': competitive_insights,
            'timestamp': datetime.now()
        }
    
    def _analyze_current_state(self, df: pd.DataFrame) -> Dict:
        """Análisis del estado actual"""
        latest_date = df['date_only'].max()
        latest = df[df['date_only'] == latest_date].copy()
        latest = latest.drop_duplicates(subset=['keyword', 'country'], keep='last')
        
        visible = latest[latest['rank'] < 250]
        
        # Categorización
        top10 = visible[visible['rank'] <= 10]
        top30 = visible[(visible['rank'] > 10) & (visible['rank'] <= 30)]
        top50 = visible[(visible['rank'] > 30) & (visible['rank'] <= 50)]
        top100 = visible[(visible['rank'] > 50) & (visible['rank'] <= 100)]
        low_visibility = visible[visible['rank'] > 100]
        invisible = latest[latest['rank'] >= 250]
        
        return {
            'total_keywords': len(latest),
            'visible': len(visible),
            'visibility_rate': len(visible) / len(latest) * 100 if len(latest) > 0 else 0,
            'avg_rank': visible['rank'].mean() if len(visible) > 0 else 0,
            'best_rank': visible['rank'].min() if len(visible) > 0 else 999,
            'categories': {
                'top10': len(top10),
                'top30': len(top30),
                'top50': len(top50),
                'top100': len(top100),
                'low_visibility': len(low_visibility),
                'invisible': len(invisible)
            },
            'top_performers': top10.nsmallest(5, 'rank')[['keyword', 'rank']].to_dict('records'),
            'low_performers': low_visibility.nlargest(5, 'rank')[['keyword', 'rank']].to_dict('records'),
            'invisible_keywords': invisible[['keyword']].to_dict('records')
        }
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Análisis de tendencias (compara últimos 7 días si hay datos)"""
        df_sorted = df.sort_values('date')
        unique_dates = df_sorted['date_only'].unique()
        
        if len(unique_dates) < 2:
            return {'message': 'Necesitas más datos históricos para analizar tendencias'}
        
        # Últimos 2 checkpoints
        latest_date = unique_dates[-1]
        previous_date = unique_dates[-2]
        
        latest = df[df['date_only'] == latest_date].drop_duplicates(subset=['keyword', 'country'], keep='last')
        previous = df[df['date_only'] == previous_date].drop_duplicates(subset=['keyword', 'country'], keep='last')
        
        improvements = []
        declines = []
        stable = []
        
        for _, current_row in latest.iterrows():
            keyword = current_row['keyword']
            current_rank = current_row['rank']
            
            prev_data = previous[previous['keyword'] == keyword]
            if len(prev_data) > 0:
                prev_rank = prev_data.iloc[0]['rank']
                diff = prev_rank - current_rank  # Positivo = mejoró
                
                if diff > 0 and current_rank < 250:  # Mejoró
                    improvements.append({
                        'keyword': keyword,
                        'prev_rank': int(prev_rank),
                        'current_rank': int(current_rank),
                        'improvement': int(diff)
                    })
                elif diff < -3:  # Empeoró significativamente
                    declines.append({
                        'keyword': keyword,
                        'prev_rank': int(prev_rank),
                        'current_rank': int(current_rank),
                        'decline': int(abs(diff))
                    })
                else:
                    stable.append(keyword)
        
        # Ordenar
        improvements.sort(key=lambda x: x['improvement'], reverse=True)
        declines.sort(key=lambda x: x['decline'], reverse=True)
        
        return {
            'improvements': improvements[:10],
            'declines': declines[:10],
            'stable_count': len(stable),
            'trend_direction': 'positive' if len(improvements) > len(declines) else 'negative' if len(declines) > len(improvements) else 'neutral'
        }
    
    def _identify_opportunities(self, df: pd.DataFrame) -> List[Dict]:
        """Identificar oportunidades de mejora"""
        latest_date = df['date_only'].max()
        latest = df[df['date_only'] == latest_date].copy()
        latest = latest.drop_duplicates(subset=['keyword', 'country'], keep='last')
        
        opportunities = []
        
        # Oportunidad 1: Keywords en posición 11-30 (casi top 10)
        near_top10 = latest[(latest['rank'] > 10) & (latest['rank'] <= 30)]
        if len(near_top10) > 0:
            for _, row in near_top10.nsmallest(5, 'rank').iterrows():
                opportunities.append({
                    'type': 'quick_win',
                    'keyword': row['keyword'],
                    'current_rank': int(row['rank']),
                    'reason': f'Está en posición #{int(row["rank"])}. Con optimización podría entrar al Top 10',
                    'action': 'Reforzar en title/subtitle o descripción',
                    'priority': 'high'
                })
        
        # Oportunidad 2: Keywords en 51-100 (baja competencia potencial)
        mid_range = latest[(latest['rank'] > 50) & (latest['rank'] <= 100)]
        if len(mid_range) > 0:
            for _, row in mid_range.nsmallest(3, 'rank').iterrows():
                opportunities.append({
                    'type': 'growth_potential',
                    'keyword': row['keyword'],
                    'current_rank': int(row['rank']),
                    'reason': f'Posición #{int(row["rank"])}. Puede tener baja competencia',
                    'action': 'Analizar competencia y considerar push de metadata',
                    'priority': 'medium'
                })
        
        # Oportunidad 3: Keywords no visibles con potencial (long tail)
        invisible = latest[latest['rank'] >= 250]
        if len(invisible) > 0:
            # Priorizar keywords más específicos (long tail)
            for _, row in invisible.head(3).iterrows():
                kw = row['keyword']
                if len(kw.split()) >= 3:  # Long tail
                    opportunities.append({
                        'type': 'long_tail',
                        'keyword': kw,
                        'current_rank': 999,
                        'reason': 'Keyword long-tail no visible. Puede ser nicho con poca competencia',
                        'action': 'Considerar añadir a descripción o crear contenido específico',
                        'priority': 'low'
                    })
        
        return opportunities[:8]
    
    def _identify_threats(self, df: pd.DataFrame) -> List[Dict]:
        """Identificar amenazas y riesgos"""
        threats = []
        
        unique_dates = df['date_only'].unique()
        if len(unique_dates) < 2:
            return threats
        
        latest_date = unique_dates[-1]
        previous_date = unique_dates[-2]
        
        latest = df[df['date_only'] == latest_date].drop_duplicates(subset=['keyword', 'country'], keep='last')
        previous = df[df['date_only'] == previous_date].drop_duplicates(subset=['keyword', 'country'], keep='last')
        
        # Threat 1: Caídas grandes en keywords TOP
        for _, current_row in latest.iterrows():
            keyword = current_row['keyword']
            current_rank = current_row['rank']
            
            prev_data = previous[previous['keyword'] == keyword]
            if len(prev_data) > 0:
                prev_rank = prev_data.iloc[0]['rank']
                
                # Si estaba en top 30 y cayó >10 posiciones
                if prev_rank <= 30 and (current_rank - prev_rank) > 10:
                    threats.append({
                        'type': 'significant_drop',
                        'keyword': keyword,
                        'severity': 'high',
                        'prev_rank': int(prev_rank),
                        'current_rank': int(current_rank),
                        'drop': int(current_rank - prev_rank),
                        'warning': f'Cayó {int(current_rank - prev_rank)} posiciones desde top 30',
                        'action': 'URGENTE: Revisar competencia, metadata y ratings'
                    })
        
        # Threat 2: Keywords estratégicos no visibles
        strategic_keywords = ['bible sleep', 'bible stories', 'bible bedtime', 'audio bible']
        for kw in strategic_keywords:
            kw_data = latest[latest['keyword'].str.contains(kw, case=False, na=False)]
            invisible_count = len(kw_data[kw_data['rank'] >= 250])
            if invisible_count > 0:
                threats.append({
                    'type': 'strategic_keyword_invisible',
                    'severity': 'medium',
                    'warning': f'{invisible_count} keywords con "{kw}" no visibles',
                    'action': 'Optimizar metadata para términos relacionados con "' + kw + '"'
                })
        
        return threats[:5]
    
    def _competitive_analysis(self, df: pd.DataFrame) -> Dict:
        """Análisis competitivo implícito"""
        latest_date = df['date_only'].max()
        latest = df[df['date_only'] == latest_date].copy()
        latest = latest.drop_duplicates(subset=['keyword', 'country'], keep='last')
        
        # Detectar keywords donde la competencia es fuerte (rank > 100)
        high_competition = latest[latest['rank'] > 100]
        
        # Detectar nichos (keywords long-tail con buen ranking)
        long_tail_winners = latest[
            (latest['rank'] < 50) & 
            (latest['keyword'].str.split().str.len() >= 4)
        ]
        
        return {
            'high_competition_count': len(high_competition),
            'high_competition_keywords': high_competition.nsmallest(5, 'rank')[['keyword', 'rank']].to_dict('records'),
            'niche_winners': long_tail_winners.nsmallest(5, 'rank')[['keyword', 'rank']].to_dict('records'),
            'recommendation': 'Enfócate en keywords long-tail donde tienes ventaja competitiva'
        }
    
    def _generate_recommendations(self, df: pd.DataFrame, current: Dict, trends: Dict) -> List[Dict]:
        """Generar recomendaciones accionables de ASO"""
        recommendations = []
        
        # Recomendación 1: Basada en visibilidad
        visibility = current['visibility_rate']
        if visibility < 70:
            recommendations.append({
                'priority': 'high',
                'category': 'Metadata Optimization',
                'title': 'Baja visibilidad general',
                'insight': f'Solo {visibility:.1f}% de keywords son visibles',
                'action': 'Revisa title, subtitle y keywords field. Elimina keywords no visibles y reemplaza con variaciones'
            })
        
        # Recomendación 2: Top performers
        if len(current['top_performers']) > 0:
            top_kw = current['top_performers'][0]['keyword']
            rank = current['top_performers'][0]['rank']
            recommendations.append({
                'priority': 'high',
                'category': 'Capitalize Success',
                'title': f'Aprovecha tu mejor keyword',
                'insight': f'"{top_kw}" está en posición #{int(rank)}',
                'action': f'Asegúrate de que "{top_kw}" esté en tu TITLE y subtitle. Pide reviews mencionando este término'
            })
        
        # Recomendación 3: Tendencias
        if trends.get('trend_direction') == 'negative':
            recommendations.append({
                'priority': 'urgent',
                'category': 'Trend Alert',
                'title': 'Tendencia negativa detectada',
                'insight': f'{len(trends.get("declines", []))} keywords bajaron de posición',
                'action': 'Revisa reviews recientes, ratings, y cambios de competidores. Considera update de app'
            })
        
        # Recomendación 4: Keywords invisibles
        invisible_count = current['categories']['invisible']
        if invisible_count > 10:
            recommendations.append({
                'priority': 'medium',
                'category': 'Keyword Cleanup',
                'title': f'{invisible_count} keywords no aportan',
                'insight': 'Keywords no visibles no generan tráfico orgánico',
                'action': 'Elimina keywords con rank >250 y reemplaza con variaciones de los que funcionan'
            })
        
        # Recomendación 5: Promedio de ranking
        avg_rank = current['avg_rank']
        if avg_rank > 100:
            recommendations.append({
                'priority': 'medium',
                'category': 'Overall Performance',
                'title': 'Ranking promedio bajo',
                'insight': f'Promedio en posición #{avg_rank:.0f}',
                'action': 'Enfócate en 5-10 keywords principales y optimiza agresivamente para ellos. Calidad > Cantidad'
            })
        elif avg_rank < 50:
            recommendations.append({
                'priority': 'low',
                'category': 'Maintain Excellence',
                'title': '¡Excelente ranking promedio!',
                'insight': f'Promedio en posición #{avg_rank:.0f}',
                'action': 'Mantén metadata estable. Enfócate en conversión (screenshots, preview, ratings)'
            })
        
        # Recomendación 6: Categorización
        top10_count = current['categories']['top10']
        if top10_count == 0:
            recommendations.append({
                'priority': 'high',
                'category': 'Breakthrough Needed',
                'title': 'Sin keywords en Top 10',
                'insight': 'No tienes keywords en posiciones premium',
                'action': 'Identifica 1-2 keywords alcanzables (rank 11-20) y optimiza title específicamente para ellos'
            })
        
        return recommendations[:6]
    
    def format_telegram_report(self, analysis: Dict) -> str:
        """Formatear análisis completo para Telegram"""
        current = analysis['current_state']
        trends = analysis['trends']
        opportunities = analysis['opportunities']
        threats = analysis['threats']
        recommendations = analysis['recommendations']
        competitive = analysis['competitive']
        
        msg = "🎯 *ANÁLISIS EXPERTO ASO - BibleNow*\n"
        msg += "=" * 40 + "\n\n"
        
        # ESTADO ACTUAL
        msg += "📊 *ESTADO ACTUAL*\n\n"
        msg += f"✅ Visibilidad: {current['visibility_rate']:.1f}%\n"
        msg += f"📈 Ranking promedio: #{current['avg_rank']:.1f}\n"
        msg += f"🏆 Mejor posición: #{int(current['best_rank'])}\n\n"
        
        msg += "*Distribución:*\n"
        cats = current['categories']
        msg += f"🥇 Top 10: {cats['top10']} kws\n"
        msg += f"🥈 Top 30: {cats['top30']} kws\n"
        msg += f"🥉 Top 50: {cats['top50']} kws\n"
        msg += f"🎯 Top 100: {cats['top100']} kws\n"
        msg += f"⚠️ >100: {cats['low_visibility']} kws\n"
        msg += f"❌ Invisibles: {cats['invisible']} kws\n\n"
        
        # TOP PERFORMERS
        if current['top_performers']:
            msg += "🏆 *TOP PERFORMERS*\n\n"
            for kw in current['top_performers'][:5]:
                keyword = kw['keyword']
                if len(keyword) > 25:
                    keyword = keyword[:22] + "..."
                msg += f"🥇 #{int(kw['rank']):3d} - `{keyword}`\n"
            msg += "\n"
        
        # TENDENCIAS
        if 'message' not in trends:
            msg += "📈 *TENDENCIAS*\n\n"
            trend_emoji = "🟢" if trends['trend_direction'] == 'positive' else "🔴" if trends['trend_direction'] == 'negative' else "🟡"
            msg += f"{trend_emoji} Tendencia: *{trends['trend_direction'].upper()}*\n\n"
            
            if trends['improvements']:
                msg += f"⬆️ *Mejoras:* {len(trends['improvements'])}\n"
                for imp in trends['improvements'][:3]:
                    kw = imp['keyword']
                    if len(kw) > 20:
                        kw = kw[:17] + "..."
                    msg += f"  • `{kw}` +{imp['improvement']}\n"
                msg += "\n"
            
            if trends['declines']:
                msg += f"⬇️ *Caídas:* {len(trends['declines'])}\n"
                for dec in trends['declines'][:3]:
                    kw = dec['keyword']
                    if len(kw) > 20:
                        kw = kw[:17] + "..."
                    msg += f"  • `{kw}` -{dec['decline']}\n"
                msg += "\n"
        
        # AMENAZAS
        if threats:
            msg += "⚠️ *AMENAZAS DETECTADAS*\n\n"
            for threat in threats[:3]:
                severity_emoji = "🔴" if threat.get('severity') == 'high' else "🟡"
                msg += f"{severity_emoji} {threat.get('warning', threat.get('type'))}\n"
                if 'action' in threat:
                    msg += f"   ➜ _{threat['action']}_\n"
            msg += "\n"
        
        # OPORTUNIDADES
        if opportunities:
            msg += "💡 *OPORTUNIDADES*\n\n"
            for opp in opportunities[:4]:
                type_emoji = "🎯" if opp['type'] == 'quick_win' else "📊"
                kw = opp['keyword']
                if len(kw) > 20:
                    kw = kw[:17] + "..."
                msg += f"{type_emoji} `{kw}`\n"
                msg += f"   {opp['reason']}\n"
                msg += f"   ➜ _{opp['action']}_\n\n"
        
        # RECOMENDACIONES TOP
        if recommendations:
            msg += "🎓 *RECOMENDACIONES CLAVE*\n\n"
            for idx, rec in enumerate(recommendations[:4], 1):
                priority_emoji = "🔥" if rec['priority'] == 'urgent' or rec['priority'] == 'high' else "⭐"
                msg += f"{priority_emoji} *{rec['title']}*\n"
                msg += f"   {rec['insight']}\n"
                msg += f"   ✅ _{rec['action']}_\n\n"
        
        # INSIGHT COMPETITIVO
        if competitive.get('niche_winners'):
            msg += "🎯 *VENTAJA COMPETITIVA*\n\n"
            msg += f"Tienes {len(competitive['niche_winners'])} nichos donde dominas:\n"
            for niche in competitive['niche_winners'][:3]:
                kw = niche['keyword']
                if len(kw) > 25:
                    kw = kw[:22] + "..."
                msg += f"  • `{kw}` (#{int(niche['rank'])})\n"
            msg += f"\n💡 _{competitive['recommendation']}_\n\n"
        
        msg += "=" * 40 + "\n"
        msg += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        msg += "_ASO Rank Guard - Expert Analysis_"
        
        return msg


def test_expert():
    """Test del analizador experto"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    expert = ASOExpert(config)
    analysis = expert.analyze_comprehensive()
    
    print("\n" + "=" * 80)
    print("ASO EXPERT ANALYSIS")
    print("=" * 80 + "\n")
    
    report = expert.format_telegram_report(analysis)
    print(report)


if __name__ == "__main__":
    test_expert()
