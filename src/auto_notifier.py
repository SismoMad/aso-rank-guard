#!/usr/bin/env python3
"""
Auto Notifier para ASO Rank Guard
Envía notificaciones automáticas cuando se detectan cambios significativos
Ahora con Smart Alerting integrado
"""

import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

# Importar Smart Alert Engine
try:
    from smart_alerts import SmartAlertEngine, SmartAlert, AlertPriority
    SMART_ALERTS_AVAILABLE = True
except ImportError:
    SMART_ALERTS_AVAILABLE = False
    logger.warning("⚠️ smart_alerts.py no disponible, usando sistema legacy")


class AutoNotifier:
    """Gestor de notificaciones automáticas con Smart Alerting"""
    
    def __init__(self, config: dict):
        self.config = config
        self.ranks_file = Path(config['storage']['ranks_file'])
        
        # Inicializar Smart Alert Engine si está disponible
        self.use_smart_alerts = (
            SMART_ALERTS_AVAILABLE and 
            config.get('alerts', {}).get('smart_alerts', {}).get('enabled', True)
        )
        
        if self.use_smart_alerts:
            self.smart_engine = SmartAlertEngine(config)
            logger.info("✅ Smart Alerting habilitado")
        else:
            logger.info("ℹ️ Usando sistema de alertas legacy")
        
        # Umbrales configurables (para modo legacy)
        self.thresholds = {
            'top_10_entry': True,      # Alerta al entrar al top 10
            'top_10_exit': True,       # Alerta al salir del top 10
            'big_drop': 10,            # Caída de más de X posiciones
            'big_gain': 10,            # Subida de más de X posiciones
            'not_found': True          # Alerta cuando keyword desaparece del ranking
        }
    
    def check_for_alerts(self) -> List[Dict]:
        """
        Analiza los últimos datos y retorna alertas que deben enviarse
        Usa Smart Alerting si está habilitado
        
        Returns:
            Lista de diccionarios con tipo de alerta, keyword, y detalles
        """
        if not self.ranks_file.exists():
            logger.warning("❌ No hay archivo de rankings")
            return []
        
        try:
            df = pd.read_csv(self.ranks_file)
            df['date'] = pd.to_datetime(df['date'])
            
            # FIX: Agrupar por DÍA en vez de timestamp exacto
            df['date_only'] = df['date'].dt.date
            
            # Obtener los dos DÍAS más recientes (no timestamps)
            days = sorted(df['date_only'].unique())
            if len(days) < 2:
                logger.info("ℹ️ Necesitamos al menos 2 días de datos para comparar")
                return []
            
            current_day = days[-1]
            previous_day = days[-2]
            
            logger.info(f"🔍 Comparando {previous_day} vs {current_day}")
            
            # Filtrar por DÍA (no por timestamp exacto)
            df_current = df[df['date_only'] == current_day].copy()
            df_previous = df[df['date_only'] == previous_day].copy()
            
            # Usar Smart Alerts si está habilitado
            if self.use_smart_alerts:
                return self._check_with_smart_engine(df_current, df_previous)
            else:
                return self._check_legacy(df_current, df_previous)
        
        except Exception as e:
            logger.error(f"❌ Error al detectar alertas: {e}", exc_info=True)
            return []
    
    def _check_with_smart_engine(self, df_current: pd.DataFrame, 
                                 df_previous: pd.DataFrame) -> List[Dict]:
        """Detectar alertas usando Smart Alert Engine"""
        smart_alerts = []
        
        for keyword in df_current['keyword'].unique():
            current_row = df_current[df_current['keyword'] == keyword]
            previous_row = df_previous[df_previous['keyword'] == keyword]
            
            if len(current_row) == 0 or len(previous_row) == 0:
                continue
            
            country = current_row.iloc[0].get('country', 'US')
            current_rank = int(current_row.iloc[0]['rank'])
            previous_rank = int(previous_row.iloc[0]['rank'])
            
            # Evaluar con smart engine
            alert = self.smart_engine.evaluate_change(
                keyword, country, previous_rank, current_rank
            )
            
            if alert:
                smart_alerts.append(alert.to_dict())
        
        logger.info(f"✅ Smart engine detectó {len(smart_alerts)} alertas")
        return smart_alerts
    
    def _check_legacy(self, df_current: pd.DataFrame, 
                     df_previous: pd.DataFrame) -> List[Dict]:
        """Detectar alertas con sistema legacy (código original)"""
        alerts = []
        
        for keyword in df_current['keyword'].unique():
            current_row = df_current[df_current['keyword'] == keyword]
            previous_row = df_previous[df_previous['keyword'] == keyword]
            
            if len(current_row) == 0:
                continue
            
            current_rank = int(current_row.iloc[0]['rank'])
            
            # Keyword nueva (no existía antes)
            if len(previous_row) == 0:
                if current_rank <= 10:
                    alerts.append({
                        'type': 'new_top_10',
                        'keyword': keyword,
                        'rank': current_rank,
                        'emoji': '🆕',
                        'message': f"Nueva keyword en Top 10: `{keyword}` (#{current_rank})"
                    })
                continue
            
            previous_rank = int(previous_row.iloc[0]['rank'])
            change = previous_rank - current_rank  # Positivo = subió, negativo = bajó
            
            # Entrada al Top 10
            if self.thresholds['top_10_entry'] and previous_rank > 10 and current_rank <= 10:
                alerts.append({
                    'type': 'top_10_entry',
                    'keyword': keyword,
                    'previous_rank': previous_rank,
                    'current_rank': current_rank,
                    'change': change,
                    'emoji': '🎯',
                    'message': f"`{keyword}` entró al Top 10: #{previous_rank} → #{current_rank} (+{change})"
                })
            
            # Salida del Top 10
            elif self.thresholds['top_10_exit'] and previous_rank <= 10 and current_rank > 10:
                alerts.append({
                    'type': 'top_10_exit',
                    'keyword': keyword,
                    'previous_rank': previous_rank,
                    'current_rank': current_rank,
                    'change': change,
                    'emoji': '⚠️',
                    'message': f"`{keyword}` salió del Top 10: #{previous_rank} → #{current_rank} ({change:+d})"
                })
            
            # Gran caída
            elif change < 0 and abs(change) >= self.thresholds['big_drop']:
                alerts.append({
                    'type': 'big_drop',
                    'keyword': keyword,
                    'previous_rank': previous_rank,
                    'current_rank': current_rank,
                    'change': change,
                    'emoji': '📉',
                    'message': f"`{keyword}` cayó {abs(change)} posiciones: #{previous_rank} → #{current_rank}"
                })
            
            # Gran subida
            elif change > 0 and change >= self.thresholds['big_gain']:
                alerts.append({
                    'type': 'big_gain',
                    'keyword': keyword,
                    'previous_rank': previous_rank,
                    'current_rank': current_rank,
                    'change': change,
                    'emoji': '🚀',
                    'message': f"`{keyword}` subió {change} posiciones: #{previous_rank} → #{current_rank}"
                })
        
        # Detectar keywords que desaparecieron
        if self.thresholds['not_found']:
            for keyword in df_previous['keyword'].unique():
                if keyword not in df_current['keyword'].values:
                    previous_row = df_previous[df_previous['keyword'] == keyword]
                    previous_rank = int(previous_row.iloc[0]['rank'])
                    
                    alerts.append({
                        'type': 'not_found',
                        'keyword': keyword,
                        'previous_rank': previous_rank,
                        'emoji': '❌',
                        'message': f"`{keyword}` ya no está en el ranking (antes: #{previous_rank})"
                    })
        
        logger.info(f"✅ Sistema legacy detectó {len(alerts)} alertas")
        return alerts
    
    def format_alert_message(self, alerts: List[Dict]) -> str:
        """
        Formatea las alertas en un mensaje de Telegram
        Usa Smart Engine si está habilitado
        
        Args:
            alerts: Lista de alertas detectadas
        
        Returns:
            Mensaje formateado en Markdown
        """
        if not alerts:
            return None
        
        # Si usa smart alerts, formatear con el engine
        if self.use_smart_alerts and hasattr(self, 'smart_engine'):
            # Convertir dicts de vuelta a SmartAlert objects si es necesario
            from smart_alerts import SmartAlert, AlertPriority
            
            smart_alerts = []
            for alert_dict in alerts:
                # Reconstruir objeto SmartAlert
                alert = SmartAlert(
                    alert_dict['type'],
                    alert_dict['keyword'],
                    alert_dict.get('country', 'US'),
                    alert_dict['prev_rank'],
                    alert_dict['current_rank'],
                    alert_dict['diff']
                )
                alert.priority = AlertPriority(alert_dict['priority'])
                alert.emoji = alert_dict['emoji']
                alert.insights = alert_dict.get('insights', [])
                alert.actions = alert_dict.get('actions', [])
                alert.estimated_impact = alert_dict.get('estimated_impact')
                smart_alerts.append(alert)
            
            # Detectar patrones
            patterns = None
            if self.config.get('alerts', {}).get('smart_alerts', {}).get('pattern_detection', True):
                patterns = self.smart_engine.detect_patterns(smart_alerts)
            
            # Formatear con smart engine
            return self.smart_engine.format_grouped_message(smart_alerts, patterns)
        
        # Si no, usar formato legacy
        return self._format_legacy(alerts)
    
    def _format_legacy(self, alerts: List[Dict]) -> str:
        """Formatear con sistema legacy (código original)"""
    def _format_legacy(self, alerts: List[Dict]) -> str:
        """Formatear con sistema legacy (código original)"""
        # Agrupar por tipo
        by_type = {
            'top_10_entry': [],
            'top_10_exit': [],
            'big_gain': [],
            'big_drop': [],
            'new_top_10': [],
            'not_found': []
        }
        
        for alert in alerts:
            by_type[alert['type']].append(alert)
        
        # Construir mensaje
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        message = f"🔔 *ALERTAS ASO AUTOMÁTICAS*\n📅 {now}\n\n"
        
        # Entradas al Top 10
        if by_type['top_10_entry']:
            message += "🎯 *ENTRADA TOP 10*\n"
            for alert in by_type['top_10_entry']:
                message += f"• {alert['message']}\n"
            message += "\n"
        
        # Nuevas keywords en Top 10
        if by_type['new_top_10']:
            message += "🆕 *NUEVAS EN TOP 10*\n"
            for alert in by_type['new_top_10']:
                message += f"• {alert['message']}\n"
            message += "\n"
        
        # Grandes subidas
        if by_type['big_gain']:
            message += "🚀 *GRANDES SUBIDAS*\n"
            for alert in by_type['big_gain']:
                message += f"• {alert['message']}\n"
            message += "\n"
        
        # Grandes caídas
        if by_type['big_drop']:
            message += "📉 *GRANDES CAÍDAS*\n"
            for alert in by_type['big_drop']:
                message += f"• {alert['message']}\n"
            message += "\n"
        
        # Salidas del Top 10
        if by_type['top_10_exit']:
            message += "⚠️ *SALIDA TOP 10*\n"
            for alert in by_type['top_10_exit']:
                message += f"• {alert['message']}\n"
            message += "\n"
        
        # Keywords desaparecidas
        if by_type['not_found']:
            message += "❌ *FUERA DE RANKING*\n"
            for alert in by_type['not_found']:
                message += f"• {alert['message']}\n"
            message += "\n"
        
        message += f"📊 Total: {len(alerts)} alertas detectadas"
        
        return message
