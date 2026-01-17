#!/usr/bin/env python3
"""
Sistema de Alertas con Supabase para ASO Rank Guard
Versión actualizada que lee configuración de BD y guarda histórico
"""

import logging
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from supabase_client import get_supabase_client
from smart_alerts import SmartAlertEngine, AlertPriority

logger = logging.getLogger(__name__)

# Telegram (si está disponible)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("⚠️ requests no instalado")


class SupabaseAlertManager:
    """
    Gestor de alertas que usa Supabase
    
    Características:
    - Lee configuración de alertas desde tabla 'alerts'
    - Detecta cambios significativos en rankings
    - Envía por Telegram/Email según preferencias del usuario
    - Guarda histórico en tabla 'alert_history'
    - Multi-usuario (cada uno recibe sus alertas)
    """
    
    def __init__(self, test_mode: bool = False):
        """
        Inicializar gestor de alertas
        
        Args:
            test_mode: Si True, muestra alertas pero no envía
        """
        self.supabase = get_supabase_client(use_service_role=True)
        self.test_mode = test_mode or os.getenv('TEST_MODE', 'false').lower() == 'true'
        
        # Inicializar smart alert engine
        self.smart_engine = SmartAlertEngine(config={})
        
        # Telegram bot token
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if self.test_mode:
            logger.warning("🧪 MODO TEST activado - Alertas NO se enviarán")
        
        logger.info("✅ SupabaseAlertManager inicializado")
    
    def check_and_send_alerts(self, app_id: str):
        """
        Verificar cambios y enviar alertas para una app
        
        Args:
            app_id: UUID de la app a verificar
        """
        logger.info(f"🔍 Verificando alertas para app {app_id}...")
        
        # 1. Obtener alertas activas para esta app
        alerts = self.supabase.client.table('alerts')\
            .select('*, profiles!inner(id, email, telegram_user_id)')\
            .eq('app_id', app_id)\
            .eq('is_active', True)\
            .execute()
        
        if not alerts.data:
            logger.info("ℹ️ No hay alertas activas configuradas")
            return
        
        logger.info(f"📋 {len(alerts.data)} alertas activas encontradas")
        
        # 2. Obtener cambios recientes en rankings
        changes = self._get_recent_changes(app_id)
        
        if not changes:
            logger.info("✅ No hay cambios significativos")
            return
        
        logger.info(f"📊 {len(changes)} cambios detectados")
        
        # 3. Procesar cada alerta del usuario
        for alert_config in alerts.data:
            user_profile = alert_config['profiles']
            
            # Filtrar cambios según configuración de la alerta
            relevant_changes = self._filter_relevant_changes(alert_config, changes)
            
            if not relevant_changes:
                continue
            
            logger.info(
                f"📬 {len(relevant_changes)} alertas para "
                f"{user_profile['email']}"
            )
            
            # Formatear mensaje
            message = self._format_alert_message(alert_config, relevant_changes)
            
            # Enviar según canales habilitados
            sent = False
            
            if alert_config.get('telegram_enabled'):
                sent = self._send_telegram_alert(user_profile, message)
            
            if alert_config.get('email_enabled'):
                sent = self._send_email_alert(user_profile['email'], message)
            
            # Guardar en histórico
            self._save_to_history(alert_config, relevant_changes, message, sent)
    
    def _get_recent_changes(self, app_id: str, hours: int = 24) -> List[Dict]:
        """
        Obtener cambios significativos en las últimas N horas
        
        Args:
            app_id: UUID de la app
            hours: Ventana de tiempo para comparar
        
        Returns:
            Lista de cambios detectados
        """
        try:
            # Obtener keywords de la app
            keywords = self.supabase.client.table('keywords')\
                .select('id, keyword, country')\
                .eq('app_id', app_id)\
                .eq('is_active', True)\
                .execute()
            
            if not keywords.data:
                return []
            
            changes = []
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            for kw in keywords.data:
                # Obtener últimos 2 rankings
                rankings = self.supabase.client.table('rankings')\
                    .select('rank, tracked_at')\
                    .eq('keyword_id', kw['id'])\
                    .gte('tracked_at', cutoff_time.isoformat())\
                    .order('tracked_at', desc=True)\
                    .limit(2)\
                    .execute()
                
                if not rankings.data or len(rankings.data) < 2:
                    continue
                
                current = rankings.data[0]
                previous = rankings.data[1]
                
                # Calcular cambio (None significa no aparece en top 250)
                current_rank = current['rank'] if current['rank'] else 999
                prev_rank = previous['rank'] if previous['rank'] else 999
                diff = current_rank - prev_rank
                
                # Solo cambios significativos (>= 3 posiciones)
                if abs(diff) >= 3:
                    changes.append({
                        'keyword_id': kw['id'],
                        'keyword': kw['keyword'],
                        'country': kw['country'],
                        'prev_rank': prev_rank,
                        'current_rank': current_rank,
                        'diff': diff,
                        'tracked_at': current['tracked_at']
                    })
            
            return changes
            
        except Exception as e:
            logger.error(f"Error obteniendo cambios: {e}")
            return []
    
    def _filter_relevant_changes(self, alert_config: Dict, 
                                 changes: List[Dict]) -> List[Dict]:
        """
        Filtrar cambios según configuración de alerta
        
        Args:
            alert_config: Configuración de la alerta
            changes: Todos los cambios detectados
        
        Returns:
            Cambios relevantes para esta alerta
        """
        alert_type = alert_config.get('alert_type', 'all')
        threshold = alert_config.get('threshold', 5)
        
        relevant = []
        
        for change in changes:
            # Filtrar por tipo
            if alert_type == 'rank_drop' and change['diff'] >= 0:
                continue
            elif alert_type == 'rank_gain' and change['diff'] <= 0:
                continue
            elif alert_type == 'new_top10':
                if not (change['current_rank'] <= 10 and change['prev_rank'] > 10):
                    continue
            
            # Filtrar por threshold
            if abs(change['diff']) < threshold:
                continue
            
            relevant.append(change)
        
        return relevant
    
    def _format_alert_message(self, alert_config: Dict, 
                             changes: List[Dict]) -> str:
        """
        Formatear mensaje de alerta
        
        Args:
            alert_config: Configuración de la alerta
            changes: Cambios a reportar
        
        Returns:
            Mensaje formateado para Telegram/Email
        """
        app_name = alert_config.get('app_name', 'App')
        
        # Header
        if len(changes) == 1:
            message = f"🔔 *Alerta de Ranking - {app_name}*\n\n"
        else:
            message = f"🔔 *{len(changes)} Alertas de Ranking - {app_name}*\n\n"
        
        # Agrupar por tipo
        drops = [c for c in changes if c['diff'] > 0]
        gains = [c for c in changes if c['diff'] < 0]
        
        # Caídas
        if drops:
            message += "📉 *Caídas:*\n"
            for change in sorted(drops, key=lambda x: abs(x['diff']), reverse=True):
                emoji = self._get_severity_emoji(abs(change['diff']))
                message += (
                    f"{emoji} *{change['keyword']}* ({change['country']})\n"
                    f"   #{change['prev_rank']} → #{change['current_rank']} "
                    f"({change['diff']:+d})\n"
                )
            message += "\n"
        
        # Subidas
        if gains:
            message += "📈 *Subidas:*\n"
            for change in sorted(gains, key=lambda x: abs(x['diff']), reverse=True):
                emoji = "🎉" if abs(change['diff']) >= 20 else "✅"
                message += (
                    f"{emoji} *{change['keyword']}* ({change['country']})\n"
                    f"   #{change['prev_rank']} → #{change['current_rank']} "
                    f"({change['diff']:+d})\n"
                )
            message += "\n"
        
        # Footer
        message += f"_🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}_"
        
        return message
    
    def _get_severity_emoji(self, diff: int) -> str:
        """Emoji según severidad del cambio"""
        if diff >= 20:
            return "🚨"
        elif diff >= 10:
            return "⚠️"
        else:
            return "📊"
    
    def _send_telegram_alert(self, user_profile: Dict, message: str) -> bool:
        """
        Enviar alerta por Telegram
        
        Args:
            user_profile: Perfil del usuario (debe tener telegram_user_id)
            message: Mensaje a enviar
        
        Returns:
            True si se envió correctamente
        """
        if not REQUESTS_AVAILABLE:
            logger.error("❌ requests no disponible para Telegram")
            return False
        
        telegram_user_id = user_profile.get('telegram_user_id')
        
        if not telegram_user_id:
            logger.warning(
                f"⚠️ Usuario {user_profile['email']} no tiene Telegram vinculado"
            )
            return False
        
        if not self.telegram_bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
            return False
        
        if self.test_mode:
            logger.info(f"🧪 [TEST] Telegram a {user_profile['email']}:\n{message}")
            return True
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            payload = {
                'chat_id': telegram_user_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ Alerta Telegram enviada a {user_profile['email']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando Telegram: {e}")
            return False
    
    def _send_email_alert(self, email: str, message: str) -> bool:
        """
        Enviar alerta por email (futuro - integrar con SendGrid/Resend)
        
        Args:
            email: Email del usuario
            message: Mensaje a enviar
        
        Returns:
            True si se envió correctamente
        """
        # TODO: Implementar con SendGrid/Resend
        logger.info(f"📧 Email alert to {email} (not implemented yet)")
        return False
    
    def _save_to_history(self, alert_config: Dict, changes: List[Dict], 
                        message: str, sent: bool):
        """
        Guardar alertas en histórico
        
        Args:
            alert_config: Configuración de la alerta
            changes: Cambios detectados
            message: Mensaje enviado
            sent: Si se envió correctamente
        """
        try:
            # Guardar una entrada por cada cambio
            for change in changes:
                self.supabase.save_alert_history(
                    alert_id=alert_config['id'],
                    user_id=alert_config['user_id'],
                    message=message,
                    channel='telegram' if alert_config.get('telegram_enabled') else 'email',
                    status='sent' if sent else 'failed'
                )
            
            logger.info(f"✅ {len(changes)} alertas guardadas en histórico")
            
        except Exception as e:
            logger.error(f"⚠️ Error guardando histórico: {e}")


def main():
    """
    Script de prueba para sistema de alertas
    
    Uso:
        python src/supabase_alerts.py
    """
    import sys
    
    # Inicializar en modo test
    alert_manager = SupabaseAlertManager(test_mode=True)
    
    # Obtener primera app para probar
    supabase = get_supabase_client(use_service_role=True)
    
    apps = supabase.client.table('apps')\
        .select('id, name')\
        .eq('is_active', True)\
        .limit(1)\
        .execute()
    
    if not apps.data:
        logger.error("❌ No hay apps en la base de datos")
        sys.exit(1)
    
    app = apps.data[0]
    logger.info(f"🧪 Probando alertas para: {app['name']}")
    
    # Verificar alertas
    alert_manager.check_and_send_alerts(app['id'])


if __name__ == '__main__':
    main()
