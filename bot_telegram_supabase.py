#!/usr/bin/env python3
"""
Bot de Telegram para ASO Rank Guard - Versión Supabase
Comandos para ver rankings, alertas y estadísticas en tiempo real
"""
import asyncio
import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ASOTelegramBot:
    """Bot de Telegram conectado a Supabase"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.allowed_chat_ids = os.getenv("TELEGRAM_ALLOWED_CHATS", "").split(",")
        
        # Supabase client
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        self.app_id = "d30da119-98d7-4c12-9e9f-13f3726c82fe"
        
        # Teclado persistente
        self.keyboard = [
            [KeyboardButton("/rankings"), KeyboardButton("/stats")],
            [KeyboardButton("/alerts"), KeyboardButton("/changes")],
            [KeyboardButton("/top"), KeyboardButton("/help")]
        ]
        self.reply_markup = ReplyKeyboardMarkup(
            self.keyboard,
            resize_keyboard=True,
            is_persistent=True
        )
    
    def _check_auth(self, update: Update) -> bool:
        """Verificar autorización"""
        chat_id = str(update.effective_chat.id)
        if self.allowed_chat_ids and chat_id not in self.allowed_chat_ids:
            logger.warning(f"Unauthorized access from {chat_id}")
            return False
        return True
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        if not self._check_auth(update):
            await update.message.reply_text("❌ No autorizado")
            return
        
        welcome = """
🚀 *ASO Rank Guard Bot*

Tu asistente personal de rankings ASO.

*Comandos disponibles:*

📊 /rankings - Ver todos los rankings actuales
📈 /stats - Estadísticas generales
🔝 /top - Top 10 keywords
⚡ /changes - Cambios recientes (24h)
🚨 /alerts - Alertas activas
ℹ️ /help - Ver esta ayuda

_Usa los botones de abajo para navegar_
"""
        await update.message.reply_text(
            welcome,
            parse_mode='Markdown',
            reply_markup=self.reply_markup
        )
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats - Estadísticas generales"""
        if not self._check_auth(update):
            return
        
        await update.message.reply_text("📊 Calculando estadísticas...")
        
        try:
            # Total keywords
            keywords = self.supabase.table("keywords")\
                .select("id", count="exact")\
                .eq("app_id", self.app_id)\
                .eq("is_active", True)\
                .execute()
            
            total_kw = keywords.count
            
            # Rankings más recientes
            latest_ranks = {}
            for kw in keywords.data[:100]:  # Limitar para performance
                ranking = self.supabase.table("rankings")\
                    .select("rank")\
                    .eq("keyword_id", kw["id"])\
                    .order("tracked_at", desc=True)\
                    .limit(1)\
                    .execute()
                
                if ranking.data:
                    latest_ranks[kw["id"]] = ranking.data[0]["rank"]
            
            top_10 = sum(1 for r in latest_ranks.values() if r <= 10)
            top_50 = sum(1 for r in latest_ranks.values() if r <= 50)
            top_100 = sum(1 for r in latest_ranks.values() if r <= 100)
            
            # Promedio
            avg_rank = sum(latest_ranks.values()) / len(latest_ranks) if latest_ranks else 0
            
            message = f"""
📊 *Estadísticas ASO Rank Guard*

🎯 Total Keywords: *{total_kw}*

📈 Distribución de Rankings:
• Top 10: *{top_10}* keywords
• Top 50: *{top_50}* keywords  
• Top 100: *{top_100}* keywords

📉 Promedio: *#{avg_rank:.1f}*

🕐 Actualizado: {datetime.now().strftime("%H:%M")}
"""
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en /stats: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def rankings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /rankings - Lista completa de rankings"""
        if not self._check_auth(update):
            return
        
        await update.message.reply_text("📊 Obteniendo rankings...")
        
        try:
            # Obtener keywords con rankings
            keywords = self.supabase.table("keywords")\
                .select("id, keyword, country")\
                .eq("app_id", self.app_id)\
                .eq("is_active", True)\
                .limit(30)\
                .execute()
            
            rankings_list = []
            for kw in keywords.data:
                ranking = self.supabase.table("rankings")\
                    .select("rank, tracked_at")\
                    .eq("keyword_id", kw["id"])\
                    .order("tracked_at", desc=True)\
                    .limit(1)\
                    .execute()
                
                if ranking.data:
                    rank = ranking.data[0]["rank"]
                    emoji = "🏆" if rank <= 10 else "⭐" if rank <= 50 else "📍"
                    rankings_list.append((rank, f"{emoji} #{rank:3d} - {kw['keyword']} ({kw['country']})"))
                else:
                    rankings_list.append((999, f"❓ --- - {kw['keyword']} ({kw['country']})"))
            
            # Ordenar por ranking
            rankings_list.sort(key=lambda x: x[0])
            
            message = "📊 *Rankings Actuales*\n\n"
            message += "\n".join([r[1] for r in rankings_list[:20]])
            message += f"\n\n_Mostrando top 20 de {len(rankings_list)}_"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en /rankings: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def top(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /top - Top 10 keywords"""
        if not self._check_auth(update):
            return
        
        try:
            keywords = self.supabase.table("keywords")\
                .select("id, keyword, country")\
                .eq("app_id", self.app_id)\
                .eq("is_active", True)\
                .execute()
            
            top_10_list = []
            for kw in keywords.data:
                ranking = self.supabase.table("rankings")\
                    .select("rank")\
                    .eq("keyword_id", kw["id"])\
                    .order("tracked_at", desc=True)\
                    .limit(1)\
                    .execute()
                
                if ranking.data and ranking.data[0]["rank"] <= 10:
                    top_10_list.append((
                        ranking.data[0]["rank"],
                        kw["keyword"],
                        kw["country"]
                    ))
            
            top_10_list.sort(key=lambda x: x[0])
            
            message = "🏆 *Top 10 Keywords*\n\n"
            for rank, keyword, country in top_10_list:
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
                message += f"{medal} #{rank} - {keyword} ({country})\n"
            
            if not top_10_list:
                message += "_No hay keywords en Top 10 aún_"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en /top: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def changes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /changes - Cambios en últimas 24h"""
        if not self._check_auth(update):
            return
        
        await update.message.reply_text("⚡ Calculando cambios...")
        
        try:
            since = datetime.now() - timedelta(hours=24)
            
            keywords = self.supabase.table("keywords")\
                .select("id, keyword")\
                .eq("app_id", self.app_id)\
                .eq("is_active", True)\
                .limit(30)\
                .execute()
            
            changes = []
            for kw in keywords.data:
                # Ranking actual
                recent = self.supabase.table("rankings")\
                    .select("rank, tracked_at")\
                    .eq("keyword_id", kw["id"])\
                    .order("tracked_at", desc=True)\
                    .limit(1)\
                    .execute()
                
                # Ranking hace 24h
                previous = self.supabase.table("rankings")\
                    .select("rank")\
                    .eq("keyword_id", kw["id"])\
                    .lt("tracked_at", since.isoformat())\
                    .order("tracked_at", desc=True)\
                    .limit(1)\
                    .execute()
                
                if recent.data and previous.data:
                    new_rank = recent.data[0]["rank"]
                    old_rank = previous.data[0]["rank"]
                    change = new_rank - old_rank
                    
                    if change != 0:
                        changes.append((abs(change), change, kw["keyword"], old_rank, new_rank))
            
            changes.sort(reverse=True)
            
            message = "⚡ *Cambios últimas 24h*\n\n"
            
            if changes:
                for _, change, keyword, old, new in changes[:15]:
                    if change < 0:  # Mejoró
                        emoji = "📈"
                        text = f"↑{abs(change)}"
                    else:  # Empeoró
                        emoji = "📉"
                        text = f"↓{change}"
                    
                    message += f"{emoji} {text} - {keyword}\n"
                    message += f"   #{old} → #{new}\n\n"
            else:
                message += "_No hay cambios significativos_"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en /changes: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /alerts - Ver alertas recientes"""
        if not self._check_auth(update):
            return
        
        try:
            # Obtener alertas recientes
            alerts = self.supabase.table("alert_history")\
                .select("message, sent_at, status")\
                .order("sent_at", desc=True)\
                .limit(10)\
                .execute()
            
            message = "🚨 *Alertas Recientes*\n\n"
            
            if alerts.data:
                for alert in alerts.data:
                    status_emoji = "✅" if alert["status"] == "sent" else "⏳"
                    date = datetime.fromisoformat(alert["sent_at"].replace("Z", "+00:00"))
                    message += f"{status_emoji} {alert['message']}\n"
                    message += f"   _{date.strftime('%d/%m %H:%M')}_\n\n"
            else:
                message += "_No hay alertas registradas_"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en /alerts: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        if not self._check_auth(update):
            return
        
        help_text = """
ℹ️ *Ayuda - ASO Rank Guard Bot*

*Comandos disponibles:*

📊 /rankings - Ver todos los rankings
📈 /stats - Estadísticas generales  
🏆 /top - Top 10 keywords
⚡ /changes - Cambios últimas 24h
🚨 /alerts - Alertas recientes
ℹ️ /help - Esta ayuda

*Tips:*
• Usa los botones para navegar rápido
• Los datos se actualizan en tiempo real
• Recibirás alertas automáticas de cambios

_Powered by Supabase_ ⚡
"""
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=self.reply_markup
        )
    
    def run(self):
        """Iniciar el bot"""
        logger.info("🤖 Iniciando ASO Telegram Bot...")
        
        application = Application.builder().token(self.token).build()
        
        # Registrar handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats))
        application.add_handler(CommandHandler("rankings", self.rankings))
        application.add_handler(CommandHandler("top", self.top))
        application.add_handler(CommandHandler("changes", self.changes))
        application.add_handler(CommandHandler("alerts", self.alerts))
        
        logger.info("✅ Bot listo. Escuchando comandos...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = ASOTelegramBot()
    bot.run()
