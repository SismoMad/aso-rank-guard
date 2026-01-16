#!/usr/bin/env python3
"""
ASO Expert Analyzer PRO - Sistema profesional con evidencia, scoring y acciones
Implementa todas las mejores prácticas de ASO real

SYSTEM PROMPT: ASO BOT (STRICT MODE)
────────────────────────────────────────
Purpose: Help decide what to change THIS WEEK.
Rules:
- Direct, honest, specific. No filler.
- Data validation MANDATORY (2 comparable periods?)
- SNAPSHOT MODE if single date or <7d history
- WEEKLY MODE if Last 7d vs Prev 7d
- No fake trends without valid comparison
- Focus keyword ONLY if #11-#20 + strong cluster
- Actions must be EXACT (no generic advice)
- ROI question: "If you change ONE thing this week, what should it be?"
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
    INFORMATIONAL = "informational"
    HABIT_ROUTINE = "habit_routine"
    AUDIO = "audio"
    KIDS_FAMILY = "kids_family"
    CHAT_AI = "chat_ai"
    LEARNING = "learning"
    SLEEP_RELAX = "sleep_relax"
    FREE = "free"
    UNKNOWN = "unknown"


class Severity(Enum):
    """Niveles de severidad para amenazas"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class KeywordEvidence:
    """Evidencia completa para cada keyword"""
    keyword: str
    rank_now: int
    rank_prev: Optional[int]
    delta: Optional[int]
    volume_proxy: int
    difficulty: str
    intent: str
    relevance: int
    country: str
    field_suggestion: str
    action: str
    confidence: str
    
    def to_row(self) -> str:
        """Formato fila para reportes"""
        delta_str = f"{self.delta:+d}" if self.delta else "NEW"
        return f"`{self.keyword[:25]}` | #{self.rank_now} | {self.rank_prev or '—'} | {delta_str} | vol:{self.volume_proxy} | {self.difficulty} | {self.confidence}"


@dataclass
class OpportunityScore:
    """Score de oportunidad 0-100 con desglose"""
    keyword: str
    total_score: int
    impact: int
    feasibility: int
    relevance: int
    risk: int
    bucket: str
    evidence: KeywordEvidence
    
    def to_task(self) -> str:
        """Convertir a tarea accionable"""
        return f"""
**Task**: {self.evidence.action}
**Why**: {self.keyword} #{self.evidence.rank_now} | Score:{self.total_score} | Vol:{self.evidence.volume_proxy} | {self.evidence.intent}
**Expected**: +5-10 ranks / +{self.evidence.volume_proxy * 0.3:.0f}% impressions
**Owner**: ASO
**ETA**: Next release
**Measure**: Rank after 7 days + CVR change
**Confidence**: {self.evidence.confidence}
"""


@dataclass
class Threat:
    """Amenaza detectada con contexto"""
    keyword: str
    severity: Severity
    rank_now: int
    rank_prev: int
    delta: int
    volume: int
    cause_probable: str
    action: str
    checks: List[str]


class ASOExpertPro:
    """Analizador experto profesional con scoring y evidencia"""
    
    # Volúmenes proxy (ajustar según datos reales si tienes)
    VOLUME_PATTERNS = {
        'brand': 500,
        'generic_2w': 300,
        'generic_3w': 150,
        'long_tail': 50,
        'very_long': 20
    }
    
    # Patrones de intención
    INTENT_PATTERNS = {
        Intent.INFORMATIONAL: ['stories', 'story', 'tales', 'meaning', 'what'],
        Intent.HABIT_ROUTINE: ['daily', 'bedtime', 'morning', 'routine', 'plan'],
        Intent.AUDIO: ['audio', 'listen', 'podcast', 'sound', 'voice', 'hear'],
        Intent.KIDS_FAMILY: ['kids', 'children', 'family', 'child', 'toddler', 'baby'],
        Intent.CHAT_AI: ['chat', 'ai', 'ask', 'talk', 'conversation', 'gpt'],
        Intent.LEARNING: ['learn', 'study', 'education', 'course', 'lesson'],
        Intent.SLEEP_RELAX: ['sleep', 'calm', 'relax', 'peaceful', 'soothing', 'meditation'],
        Intent.FREE: ['free', 'gratis', 'no cost', 'without paying']
    }
    
    # Keywords sensibles (religión, niños, salud)
    SENSITIVE_PATTERNS = ['bible', 'god', 'jesus', 'church', 'prayer', 'kids', 'children', 'baby']
    
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
        """Estimar volumen de búsqueda (proxy)"""
        kw_lower = keyword.lower()
        word_count = len(kw_lower.split())
        
        if keyword in self.brand_keywords:
            return self.VOLUME_PATTERNS['brand']
        
        if word_count >= 5:
            return self.VOLUME_PATTERNS['very_long']
        
        if word_count >= 3:
            # Boost si tiene términos populares
            popular_boost = sum(1 for term in ['bible', 'audio', 'chat', 'stories', 'sleep'] 
                              if term in kw_lower)
            base = self.VOLUME_PATTERNS['long_tail']
            return min(base * (1 + popular_boost * 0.5), 200)
        
        return self.VOLUME_PATTERNS['generic_2w'] if word_count == 2 else self.VOLUME_PATTERNS['generic_3w']
    
    def _detect_intent(self, keyword: str) -> Intent:
        """Detectar intención de búsqueda"""
        kw_lower = keyword.lower()
        
        # Prioridad: más específico primero
        for intent, patterns in sorted(self.INTENT_PATTERNS.items(), 
                                      key=lambda x: -len(x[1])):
            if any(pattern in kw_lower for pattern in patterns):
                return intent
        
        return Intent.UNKNOWN
    
    def _is_sensitive(self, keyword: str) -> bool:
        """Detectar si es keyword sensible (políticas)"""
        kw_lower = keyword.lower()
        return any(pattern in kw_lower for pattern in self.SENSITIVE_PATTERNS)
    
    def _calculate_difficulty(self, rank: int, volume: int) -> str:
        """Calcular dificultad"""
        if rank < 10 and volume > 200:
            return "high"  # Top 10 con volumen = muy competido
        elif rank < 30 and volume > 100:
            return "medium"
        elif rank > 100:
            return "high"  # Muy abajo = difícil de mover
        else:
            return "low"
    
    def _calculate_relevance(self, keyword: str, intent: Intent) -> int:
        """Relevancia 0-100 según match con producto"""
        kw_lower = keyword.lower()
        score = 40  # Base
        
        # Core features de tu app (ajustar según tu producto)
        core_features = {
            'audio': 25,
            'bible': 20,
            'stories': 20,
            'chat': 15,
            'sleep': 12,
            'kids': 10,
            'bedtime': 10,
            'daily': 8,
            'free': 5,
            'calming': 8,
            'peaceful': 6
        }
        
        for feature, points in core_features.items():
            if feature in kw_lower:
                score += points
        
        # Penalizar si no match con intent principal
        if intent == Intent.UNKNOWN:
            score -= 10
        
        return max(0, min(score, 100))
    
    def _suggest_field_and_action(self, kw: str, rank: int, intent: Intent, 
                                   relevance: int, volume: int) -> Tuple[str, str, str]:
        """Sugerir campo, acción específica y confidence"""
        
        # Top 10: mantener
        if rank <= 10:
            field = "title (maintain)"
            action = f'Maintain "{kw}" in title. Monitor competitors.'
            confidence = "high"
            return field, action, confidence
        
        # Quick wins (11-30): subtitle
        if 11 <= rank <= 30 and volume > 50:
            field = "subtitle"
            if intent == Intent.AUDIO:
                action = f'Add "{kw}" to subtitle. Example: "BibleNow - Audio Bible Stories & {kw}"'
            elif intent == Intent.SLEEP_RELAX:
                action = f'Add to subtitle: "Bedtime Bible & {kw} for Sleep"'
            elif intent == Intent.KIDS_FAMILY:
                action = f'Add to subtitle: "Safe {kw} - Bible Stories for Children"'
            elif intent == Intent.CHAT_AI:
                action = f'Add to subtitle: "Bible Chat AI - Ask & Learn with {kw}"'
            else:
                action = f'Add "{kw}" to subtitle prominently'
            confidence = "high"
            return field, action, confidence
        
        # 31-50: keywords + screenshots
        if 31 <= rank <= 50:
            field = "keywords + visual"
            if intent == Intent.AUDIO:
                action = f'Add "{kw}" to keywords field. Create screenshot showing audio player with "{kw}" label'
            elif intent == Intent.SLEEP_RELAX:
                action = f'Add "{kw}" to keywords. Create night mode screenshot with "{kw}" feature'
            else:
                action = f'Add "{kw}" to keywords field. Consider screenshot highlighting this feature'
            confidence = "medium"
            return field, action, confidence
        
        # 51-100: description
        if 51 <= rank <= 100:
            field = "description"
            action = f'Add "{kw}" in first 2 paragraphs of description. Mention specific use case.'
            confidence = "medium" if volume > 50 else "low"
            return field, action, confidence
        
        # >100: low priority
        field = "description (low priority)"
        action = f'Consider if "{kw}" is worth keeping. Low rank + may have low relevance.'
        confidence = "low"
        return field, action, confidence
    
    def _calculate_opportunity_score(self, evidence: KeywordEvidence, 
                                     trend: Optional[int] = 0) -> OpportunityScore:
        """
        Calcular Opportunity Score 0-100
        
        Impact (0-40): volumen normalizado
        Feasibility (0-30): proximidad a top10 + tendencia
        Relevance (0-20): match con producto
        Risk (-10 to 0): sensibilidad/políticas
        """
        
        # IMPACT (0-40): volumen
        volume_norm = min(evidence.volume_proxy / 500, 1.0)  # Normalizar a 500 max
        impact = int(volume_norm * 40)
        
        # FEASIBILITY (0-30): proximidad + tendencia
        if evidence.rank_now <= 10:
            proximity = 20  # Ya está top, mantener
        elif evidence.rank_now <= 30:
            proximity = 15  # Cerca del top 10
        elif evidence.rank_now <= 50:
            proximity = 10
        elif evidence.rank_now <= 100:
            proximity = 5
        else:
            proximity = 0
        
        trend_score = min(max(trend or 0, -5), 5)  # -5 a +5
        trend_points = trend_score  # +5 si sube, -5 si baja
        
        feasibility = min(proximity + trend_points, 30)
        
        # RELEVANCE (0-20): del cálculo anterior
        relevance_score = int(evidence.relevance / 100 * 20)
        
        # RISK (-10 to 0): keywords sensibles
        risk = -10 if self._is_sensitive(evidence.keyword) else 0
        
        total = impact + feasibility + relevance_score + risk
        total = max(0, min(total, 100))  # Clamp 0-100
        
        # BUCKET
        if total >= 80:
            bucket = "DO NOW"
        elif total >= 60:
            bucket = "NEXT"
        elif total >= 40:
            bucket = "WATCH"
        else:
            bucket = "IGNORE"
        
        return OpportunityScore(
            keyword=evidence.keyword,
            total_score=total,
            impact=impact,
            feasibility=feasibility,
            relevance=relevance_score,
            risk=risk,
            bucket=bucket,
            evidence=evidence
        )
    
    def analyze_comprehensive(self) -> Dict:
        """Análisis completo PRO con evidencia"""
        
        if not self.ranks_file.exists():
            return {'error': 'No hay datos históricos'}
        
        df = pd.read_csv(self.ranks_file)
        df['date'] = pd.to_datetime(df['date'])
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
        df['date_only'] = df['date'].dt.date
        
        # Obtener últimas 2 mediciones
        unique_dates = sorted(df['date_only'].unique())
        
        if len(unique_dates) < 1:
            return {'error': 'Datos insuficientes'}
        
        latest_date = unique_dates[-1]
        previous_date = unique_dates[-2] if len(unique_dates) >= 2 else None
        
        # Validar si hay comparación
        has_valid_comparison = previous_date is not None
        data_quality = "✅ OK" if has_valid_comparison else "❌ No comparison"
        
        latest = df[df['date_only'] == latest_date].drop_duplicates(subset=['keyword', 'country'], keep='last')
        
        if previous_date:
            previous = df[df['date_only'] == previous_date].drop_duplicates(subset=['keyword', 'country'], keep='last')
        else:
            previous = pd.DataFrame()  # Empty DataFrame
        
        # Generar evidencia para cada keyword
        all_evidence = []
        opportunities = []
        threats = []
        
        for _, row in latest.iterrows():
            kw = row['keyword']
            rank_now = int(row['rank'])
            country = row['country']
            
            # Rank anterior
            rank_prev = None
            delta = None
            
            if len(previous) > 0:
                prev_row = previous[previous['keyword'] == kw]
                if len(prev_row) > 0:
                    rank_prev = int(prev_row.iloc[0]['rank'])
                    delta = (rank_prev - rank_now)  # Positivo = mejoró
            
            # Calcular métricas
            volume = self._estimate_volume(kw)
            intent = self._detect_intent(kw)
            relevance = self._calculate_relevance(kw, intent)
            difficulty = self._calculate_difficulty(rank_now, volume)
            field, action, confidence = self._suggest_field_and_action(kw, rank_now, intent, relevance, volume)
            
            evidence = KeywordEvidence(
                keyword=kw,
                rank_now=rank_now,
                rank_prev=rank_prev,
                delta=delta,
                volume_proxy=volume,
                difficulty=difficulty,
                intent=intent.value,
                relevance=relevance,
                country=country,
                field_suggestion=field,
                action=action,
                confidence=confidence
            )
            
            all_evidence.append(evidence)
            
            # Calcular opportunity score
            if rank_now < 250:  # Solo keywords visibles
                trend = delta if delta else 0
                opp_score = self._calculate_opportunity_score(evidence, trend)
                opportunities.append(opp_score)
            
            # Detectar amenazas
            if delta and delta < 0:  # Cayó
                threat = self._detect_threat(evidence, abs(delta))
                if threat:
                    threats.append(threat)
        
        # Ordenar oportunidades por score
        opportunities.sort(key=lambda x: x.total_score, reverse=True)
        
        # Ordenar amenazas por severidad
        severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3}
        threats.sort(key=lambda x: severity_order[x.severity])
        
        # Métricas agregadas (con definiciones claras)
        visible = [e for e in all_evidence if e.rank_now < 250]
        
        # Visibility: % keywords en top 250 ponderado por volumen
        total_volume = sum(e.volume_proxy for e in all_evidence)
        visible_volume = sum(e.volume_proxy for e in visible)
        visibility_weighted = (visible_volume / total_volume * 100) if total_volume > 0 else 0
        
        # Avg rank ponderado por volumen
        if visible:
            weighted_ranks = sum(e.rank_now * e.volume_proxy for e in visible)
            total_weight = sum(e.volume_proxy for e in visible)
            avg_rank_weighted = weighted_ranks / total_weight
        else:
            avg_rank_weighted = 0
        
        # Share of voice estimado (% del volumen capturable en top 20)
        top20 = [e for e in visible if e.rank_now <= 20]
        sov = (sum(e.volume_proxy for e in top20) / total_volume * 100) if total_volume > 0 else 0
        
        # Top movers
        with_delta = [e for e in all_evidence if e.delta is not None]
        top_gainers = sorted([e for e in with_delta if e.delta > 0], key=lambda x: x.delta, reverse=True)[:5]
        top_losers = sorted([e for e in with_delta if e.delta < 0], key=lambda x: x.delta)[:5]
        
        # Canibalización (keywords similares compitiendo)
        cannibalization = self._detect_cannibalization(all_evidence)
        
        # Calcular periodo mostrado
        if has_valid_comparison:
            days_diff = (latest_date - previous_date).days
            if days_diff == 1:
                period_str = f"Last 24h ({previous_date} → {latest_date})"
            else:
                period_str = f"Last {days_diff}d ({previous_date} → {latest_date})"
        else:
            period_str = f"{latest_date} (single point)"
        
        return {
            'period': period_str,
            'period_dates': (previous_date, latest_date),
            'has_valid_comparison': has_valid_comparison,
            'data_quality': data_quality,
            'market': f"{latest.iloc[0]['country']} EN" if len(latest) > 0 else "US EN",
            'data_points': len(all_evidence),
            'metrics': {
                'visibility_weighted': visibility_weighted,
                'visibility_simple': len(visible) / len(all_evidence) * 100,
                'avg_rank_weighted': avg_rank_weighted,
                'avg_rank_simple': sum(e.rank_now for e in visible) / len(visible) if visible else 0,
                'share_of_voice': sov,
                'top10_count': len([e for e in visible if e.rank_now <= 10]),
                'top20_count': len([e for e in visible if e.rank_now <= 20]),
                'top50_count': len([e for e in visible if e.rank_now <= 50])
            },
            'opportunities': opportunities,
            'threats': threats,
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'cannibalization': cannibalization,
            'all_evidence': all_evidence
        }
    
    def _detect_threat(self, evidence: KeywordEvidence, drop: int) -> Optional[Threat]:
        """Detectar amenaza con severity y contexto"""
        
        rank = evidence.rank_now
        volume = evidence.volume_proxy
        
        # CRITICAL: top10 → >20 o caída >15 con volumen alto
        if ((evidence.rank_prev and evidence.rank_prev <= 10 and rank > 20) or 
            (drop > 15 and volume > 200)):
            severity = Severity.CRITICAL
            cause = "Probable: Competitor update OR ratings drop OR algorithm change"
            action = "URGENT: Check top 10 competitors, review recent ratings, verify metadata unchanged"
            checks = [
                "Search keyword in App Store - check top 10",
                "Compare competitor screenshots/titles",
                "Review ratings last 7 days",
                "Verify no metadata change on your side"
            ]
        
        # HIGH: top30 → >60 o caída sostenida
        elif ((evidence.rank_prev and evidence.rank_prev <= 30 and rank > 60) or 
              drop > 20):
            severity = Severity.HIGH
            cause = "Probable: Competitor optimization OR seasonal drop"
            action = "HIGH: Analyze competitor metadata, check for seasonal patterns"
            checks = [
                "Check competitors in rank 1-30",
                "Review seasonality (calendar, trends)",
                "Verify CVR hasn't dropped"
            ]
        
        # MEDIUM: caída 5-10 con volumen medio
        elif drop >= 5 and volume > 50:
            severity = Severity.MEDIUM
            cause = "Probable: Normal volatility OR minor algorithm shift"
            action = "MEDIUM: Monitor for 2-3 more days. If persists, investigate."
            checks = [
                "Wait 3 days and re-check",
                "Compare with other similar keywords"
            ]
        
        # LOW: ruido
        else:
            return None  # No reportar
        
        return Threat(
            keyword=evidence.keyword,
            severity=severity,
            rank_now=rank,
            rank_prev=evidence.rank_prev or 0,
            delta=-drop,
            volume=volume,
            cause_probable=cause,
            action=action,
            checks=checks
        )
    
    def _detect_cannibalization(self, all_evidence: List[KeywordEvidence]) -> List[Dict]:
        """Detectar keywords similares que compiten entre sí - Separar Head vs Tail"""
        cannibalization_cases = []
        
        # Agrupar por stems similares
        groups = {}
        for e in all_evidence:
            words = set(e.keyword.lower().split())
            # Buscar coincidencias
            matched = False
            for stem, group in groups.items():
                stem_words = set(stem.split())
                # Si comparten 2+ palabras
                if len(words & stem_words) >= 2:
                    group.append(e)
                    matched = True
                    break
            
            if not matched:
                # Crear nuevo grupo
                groups[e.keyword] = [e]
        
        # Detectar casos problemáticos y separar Head vs Tail
        for stem, group in groups.items():
            if len(group) >= 3:  # 3+ keywords similares
                # Ordenar por rank (mejores primero)
                sorted_group = sorted(group, key=lambda x: x.rank_now)
                
                # HEAD: Top 1-3 keywords del cluster
                head = sorted_group[:min(3, len(sorted_group))]
                # TAIL: El resto
                tail = sorted_group[3:] if len(sorted_group) > 3 else []
                
                head_avg = sum(e.rank_now for e in head) / len(head)
                tail_avg = sum(e.rank_now for e in tail) / len(tail) if tail else 0
                
                # Solo reportar si hay problema real (tail débil)
                if tail and tail_avg > 80:
                    status = "Head strong / Tail weak" if head_avg < 50 else "All weak"
                    
                    cannibalization_cases.append({
                        'cluster_name': stem if len(stem) < 30 else ' '.join(stem.split()[:3]) + '...',
                        'count': len(group),
                        'head': [{'kw': e.keyword, 'rank': e.rank_now} for e in head],
                        'tail': [{'kw': e.keyword, 'rank': e.rank_now} for e in tail],
                        'head_avg': head_avg,
                        'tail_avg': tail_avg,
                        'status': status,
                        'recommendation': f'Keep {len(head)} head variants in metadata, prune {len(tail)} tail variants'
                    })
        
        return cannibalization_cases
    
    def format_telegram_report(self, analysis: Dict) -> str:
        """Formatear reporte siguiendo STRICT MODE system prompt"""
        
        # VALIDACIÓN DE DATOS (RULE 1)
        has_comparison = analysis.get('has_valid_comparison', False)
        period_dates = analysis.get('period_dates', (None, None))
        prev_date, latest_date = period_dates
        
        # Determinar MODE según reglas
        mode = "SNAPSHOT"  # Default
        
        if has_comparison and prev_date and latest_date:
            days_diff = (latest_date - prev_date).days
            if days_diff >= 7:
                mode = "WEEKLY"
            else:
                # <7d history: SNAPSHOT mode
                mode = "SNAPSHOT"
        
        # EJECUTAR MODE CORRECTO
        if mode == "SNAPSHOT":
            return self._format_snapshot_mode(analysis)
        else:
            return self._format_weekly_mode(analysis)
    
    def _format_snapshot_mode(self, analysis: Dict) -> str:
        """SNAPSHOT MODE - Single point, no trend analysis (RULE 9)"""
        
        period_dates = analysis.get('period_dates', (None, None))
        latest_date = period_dates[1]
        
        msg = "🧠 *ASO SNAPSHOT (Single Point)*\n"
        msg += f"Period: {latest_date}\n"
        msg += f"Note: _This is a single-point snapshot. No trend analysis is possible._\n\n"
        
        # KEY OBSERVATIONS (3 facts)
        msg += "*KEY OBSERVATIONS*\n"
        
        opportunities = analysis['opportunities']
        all_evidence = analysis['all_evidence']
        metrics = analysis['metrics']
        
        # Obs 1: Top performers
        top10 = [e for e in all_evidence if e.rank_now <= 10]
        msg += f"• Top 10 keywords: {len(top10)}/{len(all_evidence)}\n"
        
        # Obs 2: Best keyword
        if opportunities:
            best = opportunities[0]
            msg += f"• Best opportunity: `{best.keyword}` #{best.evidence.rank_now} (score {best.total_score})\n"
        
        # Obs 3: Visibility
        visible = [e for e in all_evidence if e.rank_now < 250]
        msg += f"• Visibility: {len(visible)}/{len(all_evidence)} keywords in top 250\n\n"
        
        # HIGHEST ROI OPPORTUNITY (ONE) - ROI Question
        msg += "*HIGHEST ROI OPPORTUNITY (ONE)*\n"
        
        if opportunities:
            top = opportunities[0]
            e = top.evidence
            
            msg += f"• `{e.keyword}` — #{e.rank_now}\n"
            msg += f"  Why: Score {top.total_score} = Feasible rank improvement with {e.volume_proxy} volume\n"
            msg += f"  Action:\n"
            msg += f"  → {e.action}\n"
            
            # Expected outcome
            if e.rank_now <= 30:
                expected = "Reach top 10 within 14d"
            elif e.rank_now <= 50:
                expected = "Reach top 30 within 14d"
            else:
                expected = "Reach top 50 within 21d"
            
            msg += f"  Expected outcome: {expected} + {int(e.volume_proxy * 0.3)} impressions/day\n\n"
        else:
            msg += "• No clear opportunity detected\n\n"
        
        # CANNIBALIZATION
        cannibs = analysis['cannibalization']
        if cannibs:
            msg += "*CANNIBALIZATION*\n"
            case = cannibs[0]
            
            # Keep best performer
            if case['head']:
                keep = case['head'][0]['kw']
                msg += f"Keep: `{keep}`\n"
                
                # Secondary if exists
                if len(case['head']) > 1:
                    secondary = case['head'][1]['kw']
                    msg += f"Secondary: `{secondary}`\n"
                else:
                    msg += "Secondary: NONE\n"
                
                # Prune tail
                if case['tail']:
                    tail_count = len(case['tail'])
                    msg += f"Prune: {tail_count} variants\n\n"
        
        # IGNORE FOR NOW
        cleanup = [e for e in all_evidence if e.rank_now > 150 or e.volume_proxy < 30]
        if cleanup:
            msg += "*IGNORE FOR NOW*\n"
            for e in cleanup[:3]:
                msg += f"• `{e.keyword}` (rank >{150 if e.rank_now > 150 else ''} or low volume)\n"
        
        msg += f"\n_Generated: {datetime.now().strftime('%H:%M')}_"
        
        return msg
    
    def _format_weekly_mode(self, analysis: Dict) -> str:
        """WEEKLY MODE - Last 7d vs Prev 7d (RULE 10)"""
        
        period = analysis['period']
        
        msg = "🧠 *ASO WEEKLY PLAN*\n"
        msg += f"Period: {period}\n\n"
        
        # WHAT CHANGED (FACTS ONLY) - No fake trends
        msg += "*WHAT CHANGED (FACTS ONLY)*\n"
        
        gainers = analysis['top_gainers']
        losers = analysis['top_losers']
        metrics = analysis['metrics']
        
        if gainers:
            best = gainers[0]
            msg += f"• `{best.keyword}` improved #{best.rank_prev} → #{best.rank_now} ({best.delta:+d})\n"
        
        if losers:
            worst = losers[0]
            msg += f"• `{worst.keyword}` dropped #{worst.rank_prev} → #{worst.rank_now} ({worst.delta:+d})\n"
        
        # Top 10 changes
        all_evidence = analysis['all_evidence']
        top10_changes = [e for e in all_evidence if e.delta and (e.rank_now <= 10 or e.rank_prev and e.rank_prev <= 10)]
        if top10_changes:
            msg += f"• Top 10 keywords: {len([e for e in all_evidence if e.rank_now <= 10])}\n"
        
        msg += "\n"
        
        # FOCUS (0 or 1) - STRICT: Only #11-#20 + strong cluster
        msg += "*FOCUS (0 or 1)*\n"
        
        focus_candidate = self._find_focus_keyword(analysis)
        
        if focus_candidate:
            e = focus_candidate.evidence
            prev = f"#{e.rank_prev}" if e.rank_prev else "NEW"
            msg += f"• `{e.keyword}` — {prev} → #{e.rank_now}\n"
            msg += f"  Why: Rank #11-#20 zone + {e.intent} intent aligned + feasible to push\n\n"
        else:
            msg += "• No clear weekly focus.\n\n"
        
        # DO NOW (MAX 2 ACTIONS) - EXACT changes only
        msg += "*DO NOW (MAX 2)*\n"
        
        do_now = [o for o in analysis['opportunities'] if o.bucket == "DO NOW"][:2]
        
        if do_now:
            for i, opp in enumerate(do_now, 1):
                e = opp.evidence
                msg += f"{i}) {e.action}\n"
        else:
            msg += "• No immediate actions required\n"
        
        msg += "\n"
        
        # NEXT (MAX 2)
        msg += "*NEXT (MAX 2)*\n"
        
        next_queue = [o for o in analysis['opportunities'] if o.bucket == "NEXT"][:2]
        
        if next_queue:
            for opp in next_queue:
                e = opp.evidence
                msg += f"• {e.field_suggestion}: Add/modify `{e.keyword}`\n"
        else:
            msg += "• Queue empty\n"
        
        msg += "\n"
        
        # WATCHLIST (MAX 5 keywords)
        msg += "*WATCHLIST (MAX 5)*\n"
        
        watchlist = [o for o in analysis['opportunities'] if o.bucket == "WATCH"][:5]
        
        if watchlist:
            for opp in watchlist:
                e = opp.evidence
                msg += f"• `{e.keyword}` — #{e.rank_now} (watch for movement)\n"
        else:
            msg += "• None\n"
        
        msg += "\n"
        
        # CANNIBALIZATION
        cannibs = analysis['cannibalization']
        if cannibs:
            msg += "*CANNIBALIZATION*\n"
            case = cannibs[0]
            
            if case['head']:
                keep = case['head'][0]['kw']
                msg += f"Keep: `{keep}`\n"
                
                if len(case['head']) > 1:
                    secondary = case['head'][1]['kw']
                    msg += f"Secondary: `{secondary}`\n"
                else:
                    msg += "Secondary: NONE\n"
                
                if case['tail']:
                    tail_list = ', '.join([f"`{t['kw'][:15]}`" for t in case['tail'][:3]])
                    msg += f"Prune: {tail_list}"
                    if len(case['tail']) > 3:
                        msg += f" +{len(case['tail'])-3} more"
                    msg += "\n"
            
            msg += "\n"
        
        # CONFIDENCE
        msg += "*CONFIDENCE*\n"
        
        # Calculate confidence
        if len(gainers) > len(losers):
            confidence = "High — Positive momentum"
        elif len(do_now) > 0:
            confidence = "Medium — Clear actions available"
        else:
            confidence = "Low — Limited actionable opportunities"
        
        msg += f"{confidence}\n\n"
        
        msg += f"_Generated: {datetime.now().strftime('%H:%M')}_"
        
        return msg
    
    def _find_focus_keyword(self, analysis: Dict) -> Optional[OpportunityScore]:
        """Find Focus keyword following STRICT rules (RULE 3)
        
        Must meet ALL:
        - Rank #11-#20 (not #1-10, not #21+)
        - Belongs to strong cluster (>=2 related keywords in top 100)
        - Small change could realistically move it
        - Clear user intent aligned with app
        """
        
        opportunities = analysis['opportunities']
        all_evidence = analysis['all_evidence']
        
        # Filter candidates: rank 11-20 only
        candidates = [o for o in opportunities if 11 <= o.evidence.rank_now <= 20]
        
        if not candidates:
            return None
        
        # Check each candidate for cluster strength
        for candidate in candidates:
            kw = candidate.evidence.keyword
            
            # Find related keywords (share 2+ words)
            words = set(kw.lower().split())
            related = [e for e in all_evidence 
                      if e.rank_now <= 100 and 
                      len(set(e.keyword.lower().split()) & words) >= 2]
            
            # Strong cluster = >=2 related keywords in top 100
            if len(related) >= 2:
                # Check intent alignment
                intent = candidate.evidence.intent
                if intent != Intent.UNKNOWN.value:
                    # This is a valid Focus
                    return candidate
        
        return None


def test_expert_pro():
    """Test del analizador PRO"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    expert = ASOExpertPro(config)
    analysis = expert.analyze_comprehensive()
    
    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return
    
    print("\n" + "=" * 80)
    print("ASO EXPERT PRO ANALYSIS")
    print("=" * 80 + "\n")
    
    report = expert.format_telegram_report(analysis)
    print(report)
    
    # También mostrar algunas evidencias raw
    print("\n\n" + "=" * 80)
    print("SAMPLE EVIDENCE (Top 5 Opportunities)")
    print("=" * 80 + "\n")
    
    for opp in analysis['opportunities'][:5]:
        print(f"\nKeyword: {opp.keyword}")
        print(f"Score: {opp.total_score}/100 (Impact:{opp.impact} + Feasibility:{opp.feasibility} + Relevance:{opp.relevance} + Risk:{opp.risk})")
        print(f"Evidence: {opp.evidence.to_row()}")
        print(f"Action: {opp.evidence.action}")


if __name__ == "__main__":
    test_expert_pro()
