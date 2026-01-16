#!/usr/bin/env python3
"""
Smart Alert Engine para ASO Rank Guard
Sistema inteligente de alertas basado en reglas y contexto
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class AlertPriority(Enum):
    """Niveles de prioridad de alertas"""
    CRITICAL = "CRITICAL"      # Requiere acción inmediata
    HIGH = "HIGH"              # Importante, revisar pronto
    MEDIUM = "MEDIUM"          # Monitorizar
    LOW = "LOW"                # Informativo
    CELEBRATION = "CELEBRATION"  # Buenas noticias
    IGNORE = "IGNORE"          # No alertar


class AlertContext(Enum):
    """Contexto para añadir inteligencia a las alertas"""
    MULTIPLE_DROPS = "multiple_drops"  # Varias keywords cayeron
    TOP_KEYWORD_DROP = "top_keyword_drop"  # Keyword TOP cayó
    COMPETITOR_SURGE = "competitor_surge"  # Competidor subió
    SEASONAL = "seasonal"  # Cambio estacional
    ALGORITHM_CHANGE = "algorithm_change"  # Posible cambio de algoritmo
    REVIEW_BOMBING = "review_bombing"  # Reviews negativas recientes
    NORMAL = "normal"  # Cambio normal


class SmartAlert:
    """Representa una alerta inteligente con contexto"""
    
    def __init__(self, alert_type: str, keyword: str, country: str,
                 prev_rank: int, current_rank: int, diff: int):
        self.type = alert_type
        self.keyword = keyword
        self.country = country
        self.prev_rank = prev_rank
        self.current_rank = current_rank
        self.diff = diff
        self.priority = AlertPriority.MEDIUM
        self.context = AlertContext.NORMAL
        self.insights = []
        self.actions = []
        self.estimated_impact = None
        self.emoji = self._get_default_emoji()
    
    def _get_default_emoji(self) -> str:
        """Obtener emoji por defecto según tipo"""
        if self.type == 'drop':
            return '📉'
        elif self.type == 'rise':
            return '📈'
        return '🔔'
    
    def add_insight(self, insight: str):
        """Añadir insight al análisis"""
        self.insights.append(insight)
    
    def add_action(self, action: str):
        """Añadir acción recomendada"""
        self.actions.append(action)
    
    def set_impact(self, impact: str):
        """Establecer impacto estimado"""
        self.estimated_impact = impact
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        return {
            'type': self.type,
            'keyword': self.keyword,
            'country': self.country,
            'prev_rank': self.prev_rank,
            'current_rank': self.current_rank,
            'diff': self.diff,
            'priority': self.priority.value,
            'context': self.context.value,
            'insights': self.insights,
            'actions': self.actions,
            'estimated_impact': self.estimated_impact,
            'emoji': self.emoji
        }


class SmartAlertEngine:
    """Motor de alertas inteligentes"""
    
    def __init__(self, config: dict):
        self.config = config
        self.smart_rules = self._load_smart_rules()
    
    def _load_smart_rules(self) -> List[Dict]:
        """Cargar reglas smart desde config o usar defaults"""
        default_rules = [
            # CRITICAL: Keywords TOP que caen
            {
                'name': 'top_keyword_critical_drop',
                'condition': lambda r, c, d: c <= 20 and d <= -3,
                'priority': AlertPriority.CRITICAL,
                'emoji': '🚨',
                'telegram': True
            },
            {
                'name': 'top_keyword_major_drop',
                'condition': lambda r, c, d: c <= 50 and d <= -10,
                'priority': AlertPriority.CRITICAL,
                'emoji': '🚨',
                'telegram': True
            },
            
            # HIGH: Buenos keywords con caída significativa
            {
                'name': 'good_keyword_big_drop',
                'condition': lambda r, c, d: c <= 100 and d <= -15,
                'priority': AlertPriority.HIGH,
                'emoji': '⚠️',
                'telegram': True
            },
            
            # MEDIUM: Keywords promedio
            {
                'name': 'medium_keyword_change',
                'condition': lambda r, c, d: c <= 150 and abs(d) >= 15,
                'priority': AlertPriority.MEDIUM,
                'emoji': '📊',
                'telegram': False  # Solo daily summary
            },
            
            # LOW/IGNORE: Keywords malos fluctuando
            {
                'name': 'bad_keyword_fluctuation',
                'condition': lambda r, c, d: c > 150 and abs(d) < 20,
                'priority': AlertPriority.IGNORE,
                'emoji': '🔇',
                'telegram': False
            },
            
            # CELEBRATION: Grandes subidas
            {
                'name': 'big_win',
                'condition': lambda r, c, d: d >= 20 and c <= 50,
                'priority': AlertPriority.CELEBRATION,
                'emoji': '🎉',
                'telegram': True
            },
            {
                'name': 'top_10_entry',
                'condition': lambda r, c, d: r > 10 and c <= 10,
                'priority': AlertPriority.CELEBRATION,
                'emoji': '🎯',
                'telegram': True
            },
            
            # Subidas menores
            {
                'name': 'good_rise',
                'condition': lambda r, c, d: d >= 10 and c <= 100,
                'priority': AlertPriority.HIGH,
                'emoji': '📈',
                'telegram': True
            }
        ]
        
        # Si hay smart_rules en config, usarlas (futuro)
        if 'smart_rules' in self.config.get('alerts', {}):
            # TODO: Parsear reglas custom del config
            pass
        
        return default_rules
    
    def evaluate_change(self, keyword: str, country: str, prev_rank: int, 
                       current_rank: int) -> Optional[SmartAlert]:
        """
        Evaluar un cambio y determinar si genera alerta
        
        Args:
            keyword: Keyword afectada
            country: País
            prev_rank: Ranking anterior
            current_rank: Ranking actual
        
        Returns:
            SmartAlert si cumple reglas, None si se ignora
        """
        diff = prev_rank - current_rank  # Positivo = subió, negativo = bajó
        
        # Evaluar contra todas las reglas
        matched_rule = None
        for rule in self.smart_rules:
            if rule['condition'](prev_rank, current_rank, diff):
                matched_rule = rule
                break
        
        # Si no matchea ninguna regla o es IGNORE, no alertar
        if not matched_rule or matched_rule['priority'] == AlertPriority.IGNORE:
            logger.debug(f"Ignorando cambio: {keyword} ({prev_rank}→{current_rank})")
            return None
        
        # Crear alerta
        alert_type = 'rise' if diff > 0 else 'drop'
        alert = SmartAlert(alert_type, keyword, country, prev_rank, current_rank, diff)
        alert.priority = matched_rule['priority']
        alert.emoji = matched_rule['emoji']
        
        # Añadir contexto e insights
        self._enrich_alert(alert)
        
        return alert
    
    def _enrich_alert(self, alert: SmartAlert):
        """Añadir contexto, insights y acciones a la alerta"""
        
        # Estimar impacto basado en ranking
        if alert.current_rank <= 10:
            impressions_lost = abs(alert.diff) * 100
            alert.set_impact(f"~{impressions_lost} impresiones/día")
        elif alert.current_rank <= 30:
            impressions_lost = abs(alert.diff) * 50
            alert.set_impact(f"~{impressions_lost} impresiones/día")
        elif alert.current_rank <= 100:
            impressions_lost = abs(alert.diff) * 20
            alert.set_impact(f"~{impressions_lost} impresiones/día")
        
        # Añadir insights según tipo
        if alert.type == 'drop':
            self._add_drop_insights(alert)
        else:
            self._add_rise_insights(alert)
        
        # Añadir acciones recomendadas
        self._add_recommended_actions(alert)
    
    def _add_drop_insights(self, alert: SmartAlert):
        """Añadir insights para caídas"""
        if alert.current_rank <= 20:
            alert.add_insight("Keyword TOP perdiendo visibilidad crítica")
        elif alert.current_rank <= 50:
            alert.add_insight("Keyword importante en zona de riesgo")
        
        if abs(alert.diff) >= 10:
            alert.add_insight("Caída significativa, posible causa externa")
        
        # Detectar patrones
        if alert.prev_rank <= 10 and alert.current_rank > 10:
            alert.add_insight("⚠️ SALIÓ DEL TOP 10")
            alert.context = AlertContext.TOP_KEYWORD_DROP
    
    def _add_rise_insights(self, alert: SmartAlert):
        """Añadir insights para subidas"""
        if alert.current_rank <= 10:
            alert.add_insight("Keyword en zona premium de tráfico")
        elif alert.current_rank <= 30:
            alert.add_insight("Keyword en excelente posición")
        
        if alert.diff >= 20:
            alert.add_insight("Subida excepcional, capitalizar ahora")
        
        # Detectar entrada a zonas importantes
        if alert.prev_rank > 10 and alert.current_rank <= 10:
            alert.add_insight("🎯 ENTRADA AL TOP 10")
            alert.context = AlertContext.TOP_KEYWORD_DROP
    
    def _add_recommended_actions(self, alert: SmartAlert):
        """Añadir acciones recomendadas"""
        
        if alert.type == 'drop':
            # Acciones para caídas
            if alert.current_rank <= 20:
                alert.add_action("1. Revisa reviews últimas 24-48h")
                alert.add_action("2. Verifica metadata sigue optimizada")
                alert.add_action("3. Chequea competidores en esta keyword")
            elif alert.current_rank <= 100:
                alert.add_action("1. Monitoriza próximos 2-3 días")
                alert.add_action("2. Considera update si llevas >30 días sin actualizar")
            
            if abs(alert.diff) >= 15:
                alert.add_action("3. Busca si hubo update de iOS/competidor principal")
        
        else:
            # Acciones para subidas
            if alert.current_rank <= 10:
                alert.add_action("1. Asegúrate que keyword está en TITLE")
                alert.add_action("2. Pide reviews mencionando este término")
                alert.add_action("3. Considera aumentar presupuesto ASA si aplica")
            elif alert.current_rank <= 30:
                alert.add_action("1. Refuerza keyword en subtitle/description")
                alert.add_action("2. Monitoriza para mantener posición")
    
    def detect_patterns(self, alerts: List[SmartAlert]) -> List[Dict]:
        """
        Detectar patrones en múltiples alertas
        
        Returns:
            Lista de patrones detectados con insights
        """
        patterns = []
        
        if not alerts:
            return patterns
        
        # Patrón 1: Múltiples keywords TOP cayendo
        critical_drops = [a for a in alerts 
                         if a.type == 'drop' and a.current_rank <= 30]
        
        if len(critical_drops) >= 3:
            patterns.append({
                'type': 'multiple_top_drops',
                'severity': 'URGENT',
                'count': len(critical_drops),
                'message': f"⚠️ PATRÓN CRÍTICO: {len(critical_drops)} keywords TOP cayeron simultáneamente",
                'possible_causes': [
                    "Update de competidor principal",
                    "Cambio en algoritmo de App Store",
                    "Reviews negativas recientes afectando ASO",
                    "Metadata modificada recientemente"
                ],
                'actions': [
                    "Análisis urgente de competidores",
                    "Revisar reviews últimas 48h",
                    "Considerar update de emergencia"
                ]
            })
        
        # Patrón 2: Todas las keywords de una categoría afectadas
        drops_by_rank = {
            'top_10': [a for a in alerts if a.type == 'drop' and a.current_rank <= 10],
            'top_30': [a for a in alerts if a.type == 'drop' and 10 < a.current_rank <= 30],
            'top_100': [a for a in alerts if a.type == 'drop' and 30 < a.current_rank <= 100]
        }
        
        for rank_range, drop_list in drops_by_rank.items():
            if len(drop_list) >= 4:
                patterns.append({
                    'type': 'category_drop',
                    'severity': 'HIGH',
                    'category': rank_range,
                    'count': len(drop_list),
                    'message': f"📉 Caída coordinada en {rank_range.upper()}: {len(drop_list)} keywords afectadas"
                })
        
        # Patrón 3: Muchas subidas (buen momento)
        big_rises = [a for a in alerts 
                    if a.type == 'rise' and a.diff >= 10]
        
        if len(big_rises) >= 5:
            patterns.append({
                'type': 'positive_momentum',
                'severity': 'CELEBRATION',
                'count': len(big_rises),
                'message': f"🚀 MOMENTO POSITIVO: {len(big_rises)} keywords subiendo fuerte",
                'actions': [
                    "Capitalizar: aumentar esfuerzos ASO",
                    "Pedir reviews agresivamente",
                    "Considerar aumentar budget ASA"
                ]
            })
        
        return patterns
    
    def group_alerts_by_priority(self, alerts: List[SmartAlert]) -> Dict[str, List[SmartAlert]]:
        """Agrupar alertas por prioridad"""
        grouped = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': [],
            'CELEBRATION': []
        }
        
        for alert in alerts:
            if alert.priority != AlertPriority.IGNORE:
                grouped[alert.priority.value].append(alert)
        
        return grouped
    
    def should_send_immediately(self, alert: SmartAlert) -> bool:
        """Determinar si una alerta debe enviarse inmediatamente"""
        immediate_priorities = [
            AlertPriority.CRITICAL,
            AlertPriority.HIGH,
            AlertPriority.CELEBRATION
        ]
        return alert.priority in immediate_priorities
    
    def format_alert_message(self, alert: SmartAlert) -> str:
        """Formatear una alerta individual para Telegram"""
        emoji = alert.emoji
        keyword = alert.keyword
        prev = alert.prev_rank
        curr = alert.current_rank
        diff = alert.diff
        
        msg = f"{emoji} *{keyword}* ({alert.country})\n"
        msg += f"   #{prev} → #{curr} ({diff:+d})\n"
        
        if alert.estimated_impact:
            msg += f"   📊 Impacto: {alert.estimated_impact}\n"
        
        if alert.insights:
            msg += f"   💡 {alert.insights[0]}\n"
        
        return msg
    
    def format_grouped_message(self, alerts: List[SmartAlert], 
                              patterns: List[Dict] = None) -> str:
        """
        Formatear mensaje completo con alertas agrupadas
        
        Args:
            alerts: Lista de alertas a incluir
            patterns: Patrones detectados (opcional)
        
        Returns:
            Mensaje formateado para Telegram
        """
        if not alerts:
            return None
        
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        grouped = self.group_alerts_by_priority(alerts)
        
        msg = f"🔔 *SMART ALERTS*\n📅 {now}\n\n"
        
        # Mostrar patrones primero (si hay)
        if patterns:
            msg += "⚡️ *PATRONES DETECTADOS*\n"
            for pattern in patterns:
                msg += f"{pattern['message']}\n"
                if 'possible_causes' in pattern:
                    msg += f"🔍 Causas: {pattern['possible_causes'][0]}\n"
            msg += "\n"
        
        # CRITICAL
        if grouped['CRITICAL']:
            msg += "🚨 *CRÍTICO* (acción inmediata)\n"
            for alert in grouped['CRITICAL'][:5]:  # Max 5
                msg += self.format_alert_message(alert)
                if alert.actions:
                    msg += f"   ✅ {alert.actions[0]}\n"
            msg += "\n"
        
        # HIGH
        if grouped['HIGH']:
            msg += "⚠️ *IMPORTANTE*\n"
            for alert in grouped['HIGH'][:5]:
                msg += self.format_alert_message(alert)
            msg += "\n"
        
        # CELEBRATION
        if grouped['CELEBRATION']:
            msg += "🎉 *CELEBREMOS*\n"
            for alert in grouped['CELEBRATION'][:5]:
                msg += self.format_alert_message(alert)
            msg += "\n"
        
        # MEDIUM (solo mencionar)
        if grouped['MEDIUM']:
            msg += f"📊 {len(grouped['MEDIUM'])} cambios menores "
            msg += "(ver resumen diario)\n\n"
        
        total = len([a for a in alerts if a.priority != AlertPriority.IGNORE])
        msg += f"_Total: {total} alertas_"
        
        return msg
    
    def format_daily_summary(self, alerts: List[SmartAlert]) -> str:
        """Formatear resumen diario de cambios menores"""
        if not alerts:
            return None
        
        msg = f"📊 *RESUMEN DIARIO*\n"
        msg += f"📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
        
        grouped = self.group_alerts_by_priority(alerts)
        
        # MEDIUM changes
        if grouped['MEDIUM']:
            msg += f"📉 *Cambios Medios* ({len(grouped['MEDIUM'])})\n"
            for alert in grouped['MEDIUM'][:10]:
                emoji = '⬇️' if alert.type == 'drop' else '⬆️'
                msg += f"{emoji} {alert.keyword}: #{alert.prev_rank}→#{alert.current_rank}\n"
            msg += "\n"
        
        # LOW changes (si hay)
        if grouped['LOW']:
            msg += f"ℹ️ Cambios menores: {len(grouped['LOW'])}\n\n"
        
        msg += "_Enviado automáticamente por ASO Rank Guard_"
        
        return msg
    
    def format_enhanced_daily_summary(self, all_current_ranks: List[Dict], 
                                     alerts: List[SmartAlert]) -> str:
        """
        Resumen diario mejorado para apps jóvenes
        Incluye TOP keywords, estadísticas y oportunidades
        
        Args:
            all_current_ranks: Lista de todos los rankings actuales
            alerts: Lista de alertas detectadas
        """
        msg = f"📊 *RESUMEN DIARIO - BibleNow*\n"
        msg += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        
        # 1. TOP 15 KEYWORDS (core)
        msg += "🏆 *TOP 15 KEYWORDS*\n"
        top_15 = sorted(all_current_ranks, key=lambda x: x['rank'])[:15]
        for i, kw in enumerate(top_15, 1):
            rank = kw['rank']
            keyword = kw['keyword']
            
            # Buscar si cambió
            alert = next((a for a in alerts if a.keyword == keyword), None)
            if alert:
                diff = alert.diff
                emoji = '⚠️' if diff < 0 else '✅'
                msg += f"{emoji} {keyword}: #{rank} ({diff:+d})\n"
            else:
                msg += f"• {keyword}: #{rank} (estable)\n"
        
        msg += "\n"
        
        # 2. MOMENTUM DEL DÍA
        improved = len([a for a in alerts if a.type == 'rise'])
        worsened = len([a for a in alerts if a.type == 'drop'])
        net = improved - worsened
        
        msg += "📈 *MOMENTUM DEL DÍA*\n"
        msg += f"• {improved} keywords mejoraron\n"
        msg += f"• {worsened} keywords empeoraron\n"
        
        if net > 0:
            msg += f"• Tendencia: +{net} neto 🟢 POSITIVO\n"
        elif net < 0:
            msg += f"• Tendencia: {net} neto 🔴 NEGATIVO\n"
        else:
            msg += f"• Tendencia: neutral 🟡\n"
        
        msg += "\n"
        
        # 3. OPORTUNIDADES (keywords cerca de rankings importantes)
        msg += "🎯 *OPORTUNIDADES*\n"
        opportunities = []
        
        for alert in alerts:
            # Keywords subiendo y cerca de top 30
            if alert.type == 'rise' and 30 < alert.current_rank <= 50:
                opportunities.append((alert, f"Cerca del TOP 30, empuja más"))
            # Keywords subiendo y cerca de top 10
            elif alert.type == 'rise' and 10 < alert.current_rank <= 20:
                opportunities.append((alert, f"Cerca del TOP 10, casi ahí!"))
        
        if opportunities:
            for alert, reason in opportunities[:3]:  # Max 3
                msg += f"📈 *{alert.keyword}* #{alert.prev_rank}→#{alert.current_rank}\n"
                msg += f"   {reason}\n"
        else:
            msg += "• No hay oportunidades urgentes hoy\n"
        
        msg += "\n"
        
        # 4. ALERTAS CRÍTICAS (si las hubo en el día)
        critical_count = len([a for a in alerts if a.priority == AlertPriority.CRITICAL])
        if critical_count > 0:
            msg += f"⚠️ {critical_count} alertas CRÍTICAS enviadas hoy\n\n"
        
        msg += "_ASO Rank Guard - Daily Summary_"
        
        return msg


def main():
    """Test del smart alert engine"""
    import yaml
    
    # Cargar config
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Crear engine
    engine = SmartAlertEngine(config)
    
    # Test de evaluación
    print("🧪 Testing Smart Alert Engine\n")
    
    test_cases = [
        ("biblenow", "US", 3, 8),
        ("bible sleep", "US", 45, 60),
        ("scripture notes", "US", 180, 195),
        ("bible meditation", "US", 25, 10),
    ]
    
    alerts = []
    for keyword, country, prev, curr in test_cases:
        alert = engine.evaluate_change(keyword, country, prev, curr)
        if alert:
            alerts.append(alert)
            print(f"✅ {keyword}: {prev}→{curr} = {alert.priority.value}")
        else:
            print(f"🔇 {keyword}: {prev}→{curr} = IGNORED")
    
    print(f"\n📊 Total alerts: {len(alerts)}")
    
    # Detectar patrones
    patterns = engine.detect_patterns(alerts)
    if patterns:
        print(f"\n⚡️ Patterns detected: {len(patterns)}")
        for p in patterns:
            print(f"   - {p['message']}")
    
    # Formatear mensaje
    if alerts:
        print("\n📱 Telegram Message:\n")
        print(engine.format_grouped_message(alerts, patterns))


if __name__ == "__main__":
    main()
