#!/usr/bin/env python3
"""
Módulo de alertas - Telegram & Slack
Envío de notificaciones cuando hay cambios en rankings
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from telegram import Bot
    from telegram.error import TelegramError
    import asyncio
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("⚠️  python-telegram-bot no instalado. Instala con: pip install python-telegram-bot")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from aso_expert import ASOExpert
    EXPERT_AVAILABLE = True
except ImportError:
    EXPERT_AVAILABLE = False
    logger.warning("⚠️ aso_expert no disponible")

try:
    from aso_expert_pro import ASOExpertPro
    EXPERT_PRO_AVAILABLE = True
except ImportError:
    EXPERT_PRO_AVAILABLE = False
    logger.warning("⚠️ aso_expert_pro no disponible (usando versión básica)")


class AlertManager:
    """Gestor de alertas para notificar cambios en rankings"""
    
    def __init__(self, config: dict):
        """
        Inicializar gestor de alertas
        
        Args:
            config: Diccionario de configuración
        """
        self.config = config
        self.telegram_enabled = config['alerts']['telegram']['enabled']
        self.slack_enabled = config['alerts']['slack']['enabled']
        self.test_mode = config['debug'].get('test_mode', False)
        
        # Inicializar Telegram
        if self.telegram_enabled and TELEGRAM_AVAILABLE:
            try:
                bot_token = config['alerts']['telegram']['bot_token']
                self.chat_id = config['alerts']['telegram']['chat_id']
                
                if bot_token == "TU_BOT_TOKEN_AQUI" or self.chat_id == "TU_CHAT_ID_AQUI":
                    logger.warning("⚠️  Telegram no configurado correctamente. Edita config.yaml")
                    self.telegram_enabled = False
                else:
                    self.telegram_bot = Bot(token=bot_token)
                    logger.info("✅ Telegram inicializado correctamente")
            except Exception as e:
                logger.error(f"❌ Error inicializando Telegram: {e}")
                self.telegram_enabled = False
        elif self.telegram_enabled and not TELEGRAM_AVAILABLE:
            logger.warning("⚠️  Telegram habilitado pero librería no disponible")
            self.telegram_enabled = False
        
        if self.test_mode:
            logger.warning("🧪 MODO TEST activado - Las alertas se mostrarán pero NO se enviarán")
    
    def send_telegram_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """
        Enviar mensaje por Telegram
        
        Args:
            message: Texto del mensaje
            parse_mode: Formato del mensaje (Markdown, HTML)
        
        Returns:
            True si se envió correctamente
        """
        if not self.telegram_enabled:
            logger.debug("Telegram no habilitado, saltando envío")
            return False
        
        if self.test_mode:
            logger.info(f"🧪 [TEST MODE] Mensaje Telegram:\n{message}")
            return True
        
        try:
            # Usar API directa de Telegram (más simple y compatible)
            import requests
            
            bot_token = self.config['alerts']['telegram']['bot_token']
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("✅ Mensaje Telegram enviado correctamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje Telegram: {e}")
            return False
    
    def send_slack_message(self, message: str) -> bool:
        """
        Enviar mensaje por Slack (webhook)
        
        Args:
            message: Texto del mensaje
        
        Returns:
            True si se envió correctamente
        """
        if not self.slack_enabled or not REQUESTS_AVAILABLE:
            return False
        
        if self.test_mode:
            logger.info(f"🧪 [TEST MODE] Mensaje Slack:\n{message}")
            return True
        
        try:
            webhook_url = self.config['alerts']['slack']['webhook_url']
            
            if not webhook_url or webhook_url == "":
                logger.warning("⚠️  Slack webhook no configurado")
                return False
            
            payload = {"text": message}
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("✅ Mensaje Slack enviado correctamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje Slack: {e}")
            return False
    
    def format_change_message(self, change: Dict) -> str:
        """
        Formatear un cambio individual para Telegram (Markdown)
        
        Args:
            change: Diccionario con info del cambio
        
        Returns:
            Mensaje formateado
        """
        change_type = change['type']
        keyword = change['keyword']
        country = change['country']
        prev_rank = change['prev_rank']
        current_rank = change['current_rank']
        diff = change['diff']
        
        if change_type == 'drop':
            emoji = "⬇️🚨"
            action = "BAJÓ"
            severity = change.get('severity', 'medium')
            severity_emoji = "🔴" if severity == 'high' else "🟡"
        else:
            emoji = "⬆️🎉"
            action = "SUBIÓ"
            severity_emoji = "🟢"
        
        message = f"{emoji} *¡CAMBIO DETECTADO!*\n\n"
        message += f"{severity_emoji} Keyword: `{keyword}`\n"
        message += f"🌍 País: *{country}*\n"
        message += f"📊 Ranking: #{prev_rank} → *#{current_rank}* ({diff:+d} posiciones)\n"
        message += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        return message
    
    def send_changes_alert(self, changes: List[Dict], stats: Dict = None) -> bool:
        """
        Enviar alerta con todos los cambios detectados
        
        Args:
            changes: Lista de cambios detectados
            stats: Estadísticas opcionales del tracking
        
        Returns:
            True si se envió al menos una alerta
        """
        if not changes:
            logger.info("No hay cambios para alertar")
            return False
        
        # Separar por tipo
        drops = [c for c in changes if c['type'] == 'drop']
        rises = [c for c in changes if c['type'] == 'rise']
        
        # Crear mensaje consolidado
        app_name = self.config['app']['name']
        message = f"🔔 *ASO RANK GUARD - {app_name}*\n"
        message += f"{'=' * 40}\n\n"
        message += f"📅 {datetime.now().strftime('%d de %B, %Y - %H:%M')}\n\n"
        
        if drops:
            message += f"⬇️ *CAÍDAS DETECTADAS: {len(drops)}*\n\n"
            for drop in drops[:5]:  # Máximo 5 para no saturar
                kw = drop['keyword']
                country = drop['country']
                prev = drop['prev_rank']
                curr = drop['current_rank']
                diff = drop['diff']
                severity = "🔴" if abs(diff) > 10 else "🟡"
                message += f"{severity} `{kw}` ({country})\n"
                message += f"   #{prev} → *#{curr}* ({diff:+d})\n\n"
            
            if len(drops) > 5:
                message += f"... y {len(drops) - 5} caídas más\n\n"
        
        if rises:
            message += f"⬆️ *SUBIDAS DETECTADAS: {len(rises)}*\n\n"
            for rise in rises[:3]:  # Máximo 3
                kw = rise['keyword']
                country = rise['country']
                prev = rise['prev_rank']
                curr = rise['current_rank']
                diff = rise['diff']
                message += f"🟢 `{kw}` ({country})\n"
                message += f"   #{prev} → *#{curr}* ({diff:+d})\n\n"
            
            if len(rises) > 3:
                message += f"... y {len(rises) - 3} subidas más\n\n"
        
        # Añadir stats si están disponibles
        if stats:
            message += f"{'─' * 40}\n"
            message += f"📊 *Resumen General*\n"
            message += f"Visibilidad: {stats.get('visibility_rate', 'N/A')}\n"
            message += f"Ranking promedio: {stats.get('avg_rank', 'N/A')}\n"
        
        message += f"\n🛡️ _ASO Rank Guard - Auto-monitoring_"
        
        # Enviar por Telegram
        success = self.send_telegram_message(message)
        
        # También enviar por Slack si está habilitado
        if self.slack_enabled:
            # Convertir Markdown a texto plano para Slack
            slack_message = message.replace('*', '').replace('`', '')
            self.send_slack_message(slack_message)
        
        return success
    
    def send_daily_summary(self, stats: Dict) -> bool:
        """
        Enviar resumen diario completo (sin cambios, solo info)
        
        Args:
            stats: Estadísticas del tracking
        
        Returns:
            True si se envió correctamente
        """
        app_name = self.config['app']['name']
        
        # Obtener datos completos del CSV
        import pandas as pd
        from pathlib import Path
        
        try:
            ranks_file = Path(self.config['storage']['ranks_file'])
            df = pd.read_csv(ranks_file)
            df['date'] = pd.to_datetime(df['date'])
            df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
            df['date_only'] = df['date'].dt.date
            
            # Últimos datos
            latest_date = df['date_only'].max()
            latest = df[df['date_only'] == latest_date].copy()
            
            # Eliminar duplicados
            latest = latest.drop_duplicates(subset=['keyword', 'country'], keep='last')
            latest = latest.sort_values('rank')
            
            visible = latest[latest['rank'] < 250]
            invisible = latest[latest['rank'] >= 250]
            
            # Crear mensaje completo
            message = f"🛡️ *ASO RANK GUARD - {app_name}*\n"
            message += f"{'=' * 40}\n\n"
            message += f"📅 {latest_date.strftime('%d/%m/%Y')}\n"
            message += f"📱 Keywords: {len(latest)}\n"
            message += f"🌍 Store: US\n\n"
            
            # Stats generales
            visibility_pct = len(visible)/len(latest)*100 if len(latest) > 0 else 0
            message += f"✅ *Visibles:* {len(visible)}/{len(latest)} ({visibility_pct:.1f}%)\n"
            
            if len(visible) > 0:
                avg_rank = visible['rank'].mean()
                best_rank = visible['rank'].min()
                message += f"📈 *Promedio:* #{avg_rank:.1f}\n"
                message += f"🏆 *Mejor:* #{int(best_rank)}\n"
            
            # Stats por categoría
            top10 = len(visible[visible['rank'] <= 10])
            top30 = len(visible[visible['rank'] <= 30])
            top50 = len(visible[visible['rank'] <= 50])
            top100 = len(visible[visible['rank'] <= 100])
            
            message += f"\n📊 *Por categoría:*\n"
            message += f"🥇 Top 10: {top10}\n"
            message += f"🥈 Top 30: {top30}\n"
            message += f"🥉 Top 50: {top50}\n"
            message += f"🎯 Top 100: {top100}\n"
            
            # Top 10 keywords
            message += f"\n{'─' * 40}\n"
            message += f"🏆 *TOP 10 KEYWORDS*\n\n"
            
            top_kws = visible.head(10)
            for _, row in top_kws.iterrows():
                rank = int(row['rank'])
                keyword = row['keyword']
                
                if rank <= 10:
                    emoji = "🥇"
                elif rank <= 30:
                    emoji = "🥈"
                else:
                    emoji = "🥉"
                
                # Truncar keyword si es muy largo
                if len(keyword) > 30:
                    keyword = keyword[:27] + "..."
                
                message += f"{emoji} #{rank:3d} - `{keyword}`\n"
            
            # Peores 5
            if len(visible) > 10:
                message += f"\n{'─' * 40}\n"
                message += f"⚠️ *PEOR PERFORMANCE (Top 5)*\n\n"
                
                worst5 = visible.tail(5)
                for _, row in worst5.iterrows():
                    rank = int(row['rank'])
                    keyword = row['keyword']
                    if len(keyword) > 30:
                        keyword = keyword[:27] + "..."
                    message += f"📉 #{rank:3d} - `{keyword}`\n"
            
            # Keywords no visibles
            if len(invisible) > 0:
                message += f"\n{'─' * 40}\n"
                message += f"❌ *NO VISIBLES:* {len(invisible)} keywords\n\n"
                for _, row in invisible.head(5).iterrows():
                    keyword = row['keyword']
                    if len(keyword) > 35:
                        keyword = keyword[:32] + "..."
                    message += f"• {keyword}\n"
                
                if len(invisible) > 5:
                    message += f"... y {len(invisible) - 5} más\n"
            
            message += f"\n{'=' * 40}\n"
            message += f"⏰ {pd.Timestamp.now().strftime('%H:%M')}"
            
        except Exception as e:
            # Fallback al mensaje simple
            logger.warning(f"Error generando reporte completo: {e}")
            message = f"📊 *Resumen Diario - {app_name}*\n\n"
            message += f"✅ Check completado\n"
            message += f"Visibilidad: {stats.get('visibility_rate', 'N/A')}\n"
            message += f"Ranking promedio: {stats.get('avg_rank', 'N/A')}\n"
        
        return self.send_telegram_message(message)
    
    def get_expert_analysis(self) -> Optional[str]:
        """
        Generar análisis experto SIN enviarlo (solo retornar el texto)
        
        Returns:
            String con el análisis formateado, o None si hay error
        """
        # Intentar versión PRO primero
        if EXPERT_PRO_AVAILABLE:
            try:
                expert = ASOExpertPro(self.config)
                analysis = expert.analyze_comprehensive()
                
                if 'error' in analysis:
                    logger.error(f"Error en análisis PRO: {analysis['error']}")
                    return None
                
                message = expert.format_telegram_report(analysis)
                return message
                
            except Exception as e:
                logger.error(f"❌ Error en análisis PRO: {e}")
                # Fallback a versión básica
        
        # Fallback: versión básica
        if EXPERT_AVAILABLE:
            try:
                expert = ASOExpert(self.config)
                analysis = expert.analyze_comprehensive()
                
                if 'error' in analysis:
                    logger.error(f"Error en análisis experto: {analysis['error']}")
                    return None
                
                message = expert.format_telegram_report(analysis)
                return message
                
            except Exception as e:
                logger.error(f"❌ Error generando análisis experto: {e}")
                return None
        
        logger.warning("⚠️ No hay módulo de análisis experto disponible")
        return None
    
    def send_expert_analysis(self) -> bool:
        """
        Enviar análisis experto completo de ASO (versión PRO si disponible)
        
        Returns:
            True si se envió correctamente
        """
        message = self.get_expert_analysis()
        
        if message:
            return self.send_telegram_message(message)
        else:
            return False
    
    def send_test_alert(self) -> bool:
        """Enviar alerta de prueba para verificar configuración"""
        message = f"🧪 *Test de ASO Rank Guard*\n\n"
        message += f"✅ Telegram configurado correctamente\n"
        message += f"App: {self.config['app']['name']}\n"
        message += f"App ID: {self.config['app']['id']}\n"
        message += f"Keywords: {len(self.config['keywords'])}\n"
        message += f"Países: {', '.join(self.config['countries'])}\n\n"
        message += f"🚀 Sistema listo para monitorizar rankings\n"
        message += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        return self.send_telegram_message(message)


def test_alerts():
    """Función de test para probar alertas"""
    import yaml
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    manager = AlertManager(config)
    
    # Test 1: Mensaje simple
    print("\n🧪 Test 1: Alerta de prueba...")
    manager.send_test_alert()
    
    # Test 2: Cambios simulados
    print("\n🧪 Test 2: Cambios simulados...")
    fake_changes = [
        {
            'type': 'drop',
            'keyword': 'audio bible stories',
            'country': 'ES',
            'prev_rank': 42,
            'current_rank': 49,
            'diff': -7,
            'severity': 'medium'
        },
        {
            'type': 'rise',
            'keyword': 'bible chat ai',
            'country': 'US',
            'prev_rank': 87,
            'current_rank': 72,
            'diff': 15,
            'severity': 'positive'
        }
    ]
    
    fake_stats = {
        'visibility_rate': '75.0%',
        'avg_rank': '68.5',
        'visible_in_top250': 9,
        'total_tracked': 12,
        'top_keywords': [
            {'keyword': 'cuentos biblicos audio', 'country': 'ES', 'rank': 34},
            {'keyword': 'audio bible stories', 'country': 'US', 'rank': 49}
        ]
    }
    
    manager.send_changes_alert(fake_changes, fake_stats)
    
    print("\n✅ Tests completados")


if __name__ == "__main__":
    test_alerts()
