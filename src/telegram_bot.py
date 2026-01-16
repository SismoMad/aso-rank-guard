#!/usr/bin/env python3
"""
Bot de Telegram para ASO Rank Guard
Escucha comandos y ejecuta análisis bajo demanda
"""

import asyncio
import logging
import yaml
import sys
import os
from pathlib import Path
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Agregar el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar componentes del sistema
from rank_tracker import RankTracker
from telegram_alerts import AlertManager
from report_formatter import ReportFormatter

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ASOBot:
    """Bot de Telegram para controlar ASO Rank Guard"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        # Cargar configuración
        self.config_path = config_path
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.token = self.config['alerts']['telegram']['bot_token']
        self.allowed_chat_id = int(self.config['alerts']['telegram']['chat_id'])
        self.tracker = None
        self.telegram = None
        self.formatter = ReportFormatter()  # Inicializar formateador
        
        # Definir teclado persistente
        self.keyboard = [
            [KeyboardButton("📊 /track"), KeyboardButton("🔍 /analyze")],
            [KeyboardButton("🚀 /full"), KeyboardButton("📈 /status")],
            [KeyboardButton("🔔 /alerts"), KeyboardButton("ℹ️ /help")]
        ]
        self.reply_markup = ReplyKeyboardMarkup(
            self.keyboard, 
            resize_keyboard=True,
            is_persistent=True
        )
    
    def _check_authorization(self, update: Update) -> bool:
        """Verificar que el usuario está autorizado"""
        user_id = update.effective_chat.id
        if user_id != self.allowed_chat_id:
            logger.warning(f"⚠️ Intento no autorizado de chat_id: {user_id}")
            return False
        return True
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        if not self._check_authorization(update):
            await update.message.reply_text("❌ No autorizado")
            return
        
        welcome = """
🚀 *ASO Rank Guard Bot*

Comandos disponibles:

📊 /track - Tracking de keywords (sin análisis)
🔍 /analyze - Ejecutar análisis PRO completo
🚀 /full - Tracking + Análisis completo
📈 /status - Ver estado actual
ℹ️ /help - Ver esta ayuda

_Usa los botones de abajo para ejecutar comandos_
"""
        await update.message.reply_text(
            welcome, 
            parse_mode='Markdown',
            reply_markup=self.reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        if not self._check_authorization(update):
            return
        
        # Mostrar mensaje personalizado con /history
        help_text = """
🤖 *ASO Rank Guard Bot*

📊 `/track` - Estado actual
🔍 `/analyze` - Análisis PRO  
📈 `/status` - Estadísticas
🚀 `/full` - Tracking + Análisis
� `/alerts` - Ver alertas detectadas
📖 `/history <keyword>` - Evolución
ℹ️ `/help` - Ayuda

*Ejemplos:*
`/history bible stories`

💡 *Alertas automáticas:*
Cuando ejecutas `/track`, el sistema detecta automáticamente cambios importantes (entradas/salidas del Top 10, subidas/caídas >10 posiciones) y te envía notificaciones.
"""
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(self.keyboard, resize_keyboard=True)
        )
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /analyze - Ejecutar análisis PRO"""
        if not self._check_authorization(update):
            await update.message.reply_text("❌ No autorizado")
            return
        
        await update.message.reply_text("🔍 Ejecutando análisis PRO...\n_Esto puede tardar unos segundos_", parse_mode='Markdown')
        
        try:
            # Inicializar Alert Manager
            if not self.telegram:
                self.telegram = AlertManager(self.config)
            
            # Ejecutar análisis PRO (SIN enviar, solo obtener texto)
            logger.info("🎯 Ejecutando análisis PRO desde Telegram...")
            message = self.telegram.get_expert_analysis()
            
            if message:
                # Enviar como respuesta al comando (no como mensaje separado)
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("⚠️ Error al generar el análisis. Revisa que tengas datos de tracking.")
        
        except Exception as e:
            logger.error(f"❌ Error en análisis: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def track_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /track - Solo tracking sin análisis"""
        if not self._check_authorization(update):
            await update.message.reply_text("❌ No autorizado")
            return
        
        await update.message.reply_text("📊 Iniciando tracking de keywords...\n_Esto tomará unos minutos (83 keywords)_", parse_mode='Markdown')
        
        try:
            # Inicializar tracker
            if not self.tracker:
                self.tracker = RankTracker(self.config_path)
            
            # Ejecutar tracking
            logger.info("🔍 Ejecutando tracking desde Telegram...")
            df_results = self.tracker.track_all_keywords()
            
            # Cargar datos históricos
            import pandas as pd
            ranks_file = Path(self.config['storage']['ranks_file'])
            df_all = pd.read_csv(ranks_file)
            
            # Verificar si hay datos anteriores
            df_all['date'] = pd.to_datetime(df_all['date'])
            df_all['date_only'] = df_all['date'].dt.date
            unique_dates = sorted(df_all['date_only'].unique())
            has_previous = len(unique_dates) > 1
            
            # Generar reporte usando el formateador
            message = self.formatter.format_tracking_report(
                df_results=df_results,
                df_all=df_all,
                has_previous=has_previous
            )
            
            # Enviar mensaje (dividir si es muy largo)
            messages = self.formatter.split_long_message(message)
            for msg in messages:
                await update.message.reply_text(msg, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"❌ Error en tracking: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Error en tracking:\n`{str(e)}`\n\nRevisa los logs del bot", 
                parse_mode='Markdown'
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Ver estado actual"""
        if not self._check_authorization(update):
            await update.message.reply_text("❌ No autorizado")
            return
        
        try:
            import pandas as pd
            
            # Leer datos
            ranks_file = Path(self.config['storage']['ranks_file'])
            if not ranks_file.exists():
                await update.message.reply_text("❌ No hay datos históricos aún.\n\n💡 Ejecuta `/track` primero para generar datos.", parse_mode='Markdown')
                return
            
            df = pd.read_csv(ranks_file)
            
            # Validar que el CSV no esté vacío
            if len(df) == 0:
                await update.message.reply_text("❌ El archivo de datos está vacío.\n\n💡 Ejecuta `/track` para generar datos.", parse_mode='Markdown')
                return
            
            # Validar columnas necesarias
            required_columns = ['date', 'keyword', 'country', 'rank']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                await update.message.reply_text(f"❌ Archivo de datos corrupto (faltan columnas: {', '.join(missing_columns)}).\n\n💡 Contacta al desarrollador.", parse_mode='Markdown')
                return
            
            df['date'] = pd.to_datetime(df['date'])
            df['date_only'] = df['date'].dt.date
            
            unique_dates = sorted(df['date_only'].unique())
            if len(unique_dates) == 0:
                await update.message.reply_text("❌ No hay datos de fechas válidos.", parse_mode='Markdown')
                return
            
            latest_date = unique_dates[-1]
            latest_data = df[df['date_only'] == latest_date].drop_duplicates(subset=['keyword'], keep='last')
            
            if len(latest_data) == 0:
                await update.message.reply_text("❌ No hay datos para la fecha más reciente.", parse_mode='Markdown')
                return
            
            # Calcular métricas
            total_kws = len(latest_data)
            visible = len(latest_data[latest_data['rank'] < 250])
            top10 = len(latest_data[latest_data['rank'] <= 10])
            top30 = len(latest_data[latest_data['rank'] <= 30])
            
            best = latest_data.nsmallest(1, 'rank').iloc[0] if len(latest_data) > 0 else None
            
            status = f"""
📊 *Estado Actual - {self.config['app']['name']}*

📅 Última actualización: {latest_date}
📦 Keywords totales: {total_kws}
👁️ Visibles (top 250): {visible} ({visible/total_kws*100:.1f}%)

🏆 Distribución:
  • Top 10: {top10}
  • Top 30: {top30}

🥇 Mejor keyword: `{best['keyword']}` #{int(best['rank'])}

📈 Tracking dates: {len(unique_dates)}
"""
            await update.message.reply_text(status, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"❌ Error en status: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error inesperado: {str(e)}\n\nRevisa los logs del bot.", parse_mode='Markdown')
    
    async def full_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /full - Tracking + Análisis completo"""
        if not self._check_authorization(update):
            await update.message.reply_text("❌ No autorizado")
            return
        
        await update.message.reply_text("🚀 *Workflow completo iniciado*\n\n1️⃣ Tracking de keywords...\n_Esto tardará ~4 minutos_", parse_mode='Markdown')
        
        try:
            # Paso 1: Tracking
            if not self.tracker:
                self.tracker = RankTracker(self.config_path)  # Pasar ruta, no dict
            
            logger.info("🔍 Ejecutando tracking...")
            df_results = self.tracker.track_all_keywords()
            
            await update.message.reply_text(f"✅ Tracking completado ({len(df_results)} keywords)\n\n2️⃣ Generando análisis PRO...", parse_mode='Markdown')
            
            # Paso 2: Análisis
            if not self.telegram:
                self.telegram = AlertManager(self.config)
            
            logger.info("🎯 Ejecutando análisis PRO...")
            message = self.telegram.get_expert_analysis()
            
            if message:
                await update.message.reply_text("✅ *Workflow completado*\n\n", parse_mode='Markdown')
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("⚠️ Tracking OK pero hubo problema generando el análisis")
        
        except Exception as e:
            logger.error(f"❌ Error en workflow: {e}", exc_info=True)
            error_msg = f"❌ *Error en workflow:*\n\n`{str(e)}`\n\nRevisa los logs del bot para más detalles"
            await update.message.reply_text(error_msg, parse_mode='Markdown')
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar errores"""
        logger.error(f"Error: {context.error}")
    
    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /alerts - Ver alertas detectadas en el último tracking"""
        if not self._check_authorization(update):
            await update.message.reply_text("❌ No autorizado")
            return
        
        try:
            from auto_notifier import AutoNotifier
            
            await update.message.reply_text("🔍 Analizando cambios...")
            
            notifier = AutoNotifier(self.config)
            alerts = notifier.check_for_alerts()
            
            if not alerts:
                await update.message.reply_text("✅ No hay alertas. Todo normal 👍")
                return
            
            message = notifier.format_alert_message(alerts)
            if message:
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("⚠️ Error al generar el reporte de alertas")
        
        except Exception as e:
            logger.error(f"❌ Error en alerts: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Error: {str(e)}\n\n💡 Asegúrate de tener al menos 2 días de datos de tracking",
                parse_mode='Markdown'
            )
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /history <keyword> - Ver evolución de una keyword"""
        if not self._check_authorization(update):
            await update.message.reply_text("❌ No autorizado")
            return
        
        # Obtener keyword del argumento
        if not context.args:
            await update.message.reply_text(
                "❌ Uso: `/history <keyword>`\n\nEjemplo: `/history bible stories`",
                parse_mode='Markdown'
            )
            return
        
        keyword = ' '.join(context.args)
        
        try:
            import pandas as pd
            
            # Leer datos
            ranks_file = Path(self.config['storage']['ranks_file'])
            if not ranks_file.exists():
                await update.message.reply_text("❌ No hay datos históricos aún")
                return
            
            df = pd.read_csv(ranks_file)
            df['date'] = pd.to_datetime(df['date'])
            df['date_only'] = df['date'].dt.date
            
            # Buscar keyword (case insensitive)
            df_keyword = df[df['keyword'].str.lower() == keyword.lower()]
            
            if len(df_keyword) == 0:
                await update.message.reply_text(
                    f"❌ No se encontró la keyword `{keyword}`\n\n💡 Verifica que esté escrita correctamente.",
                    parse_mode='Markdown'
                )
                return
            
            # Agrupar por fecha y tomar el último rank de cada día
            df_history = df_keyword.sort_values('date').drop_duplicates(
                subset=['date_only'], keep='last'
            )
            
            # Ordenar por fecha
            df_history = df_history.sort_values('date_only')
            
            # Construir mensaje
            message = f"📊 *Historial: `{keyword}`*\n\n"
            
            for _, row in df_history.iterrows():
                date = row['date_only']
                rank = int(row['rank'])
                message += f"📅 {date} → #{rank}\n"
            
            # Calcular estadísticas
            best_rank = int(df_history['rank'].min())
            worst_rank = int(df_history['rank'].max())
            avg_rank = df_history['rank'].mean()
            current_rank = int(df_history.iloc[-1]['rank'])
            
            message += f"\n📈 *Estadísticas*\n"
            message += f"🥇 Mejor: #{best_rank}\n"
            message += f"📉 Peor: #{worst_rank}\n"
            message += f"📊 Promedio: #{avg_rank:.1f}\n"
            message += f"📍 Actual: #{current_rank}\n"
            
            # Tendencia
            if len(df_history) >= 2:
                first_rank = int(df_history.iloc[0]['rank'])
                trend_diff = first_rank - current_rank
                
                if trend_diff > 0:
                    trend = f"↑ Subió {trend_diff} posiciones desde el inicio"
                elif trend_diff < 0:
                    trend = f"↓ Bajó {abs(trend_diff)} posiciones desde el inicio"
                else:
                    trend = "= Sin cambios desde el inicio"
                
                message += f"\n🎯 Tendencia: {trend}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"❌ Error en history: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_button_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar texto de los botones (con emojis)"""
        text = update.message.text
        
        # Extraer el comando del texto del botón
        if "/track" in text:
            await self.track_command(update, context)
        elif "/analyze" in text:
            await self.analyze_command(update, context)
        elif "/full" in text:
            await self.full_command(update, context)
        elif "/status" in text:
            await self.status_command(update, context)
        elif "/alerts" in text:
            await self.alerts_command(update, context)
        elif "/help" in text:
            await self.help_command(update, context)
    
    def run(self):
        """Iniciar el bot"""
        logger.info("🤖 Iniciando ASO Rank Guard Bot...")
        logger.info(f"📱 Chat ID autorizado: {self.allowed_chat_id}")
        
        # Crear aplicación
        app = Application.builder().token(self.token).build()
        
        # Registrar comandos
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("analyze", self.analyze_command))
        app.add_handler(CommandHandler("track", self.track_command))
        app.add_handler(CommandHandler("status", self.status_command))
        app.add_handler(CommandHandler("full", self.full_command))
        app.add_handler(CommandHandler("history", self.history_command))
        app.add_handler(CommandHandler("alerts", self.alerts_command))
        
        # Handler para mensajes de texto (botones)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_button_text))
        
        # Error handler
        app.add_error_handler(self.error_handler)
        
        logger.info("✅ Bot iniciado - Esperando comandos...")
        logger.info("💡 Envía /start en Telegram para comenzar")
        
        # Iniciar polling
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Punto de entrada"""
    try:
        bot = ASOBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n👋 Bot detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
