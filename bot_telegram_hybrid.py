#!/usr/bin/env python3
"""
Bot de Telegram para ASO Rank Guard - Versión Híbrida
Soporta tanto CSV (legacy) como Supabase (nuevo)
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Cargar variables de entorno
load_dotenv()

# Ensure src/ is in the import path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HybridASOBot:
    """Bot de Telegram para Supabase"""
    
    def __init__(self, use_supabase: bool = True):
        """
        Inicializar bot
        
        Args:
            use_supabase: Si True usa Supabase, si False usa CSV, si None auto-detecta
        """
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.allowed_chat_id = int(os.getenv("TELEGRAM_ALLOWED_CHATS", "0").split(",")[0])
        
        # Forzar modo Supabase
        self.use_supabase = True
        logger.info("🔧 Modo: Supabase")
        
        # Inicializar Supabase
        from supabase_client import get_supabase_client
        from rank_tracker_supabase import RankTrackerSupabase
        
        self.supabase = get_supabase_client(use_service_role=True)
        self.tracker_class = RankTrackerSupabase
        
        # Obtener o crear usuario admin
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@aso-rank-guard.local')
        self.user_id = self._get_or_create_admin_user(admin_email)
        logger.info(f"👤 Usuario admin: {admin_email}")
        
        # Teclado persistente
        self.keyboard = [
            [KeyboardButton("/track"), KeyboardButton("/rankings")],
            [KeyboardButton("/changes"), KeyboardButton("/status")],
            [KeyboardButton("/alerts"), KeyboardButton("/help")]
        ]
        self.reply_markup = ReplyKeyboardMarkup(
            self.keyboard,
            resize_keyboard=True,
            is_persistent=True
        )
    
    def _get_or_create_admin_user(self, email: str) -> str:
        """Obtener o crear usuario admin en Supabase"""
        try:
            user = self.supabase.get_user_by_email(email)
            if user:
                return user['id']
            
            # Crear usuario admin si no existe
            logger.info(f"Creando usuario admin: {email}")
            new_user = {
                "email": email,
                "tier": "pro",
                "max_apps": 10,
                "max_keywords_per_app": 200,
                "is_active": True
            }
            result = self.supabase.client.table("profiles").insert(new_user).execute()
            return result.data[0]['id']
        
        except Exception as e:
            logger.error(f"Error obteniendo/creando usuario: {e}")
            # Usar UUID por defecto
            return "00000000-0000-0000-0000-000000000000"
    
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
            await update.message.reply_text("❌ Unauthorized")
            return
        
        welcome = f"""
    🚀 *ASO Rank Guard Bot* (Supabase)

    Available commands:

    📊 /track - Run keyword tracking
    📈 /status - Current status
    🏆 /rankings - Current rankings
    ⚡ /changes - Recent changes
    🚨 /alerts - Alerts
    ℹ️ /help - Help

    _Use the buttons below to navigate_
    """
        await update.message.reply_text(
            welcome,
            parse_mode='Markdown',
            reply_markup=self.reply_markup
        )
    
    async def track_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /track - Ejecutar tracking"""
        if not self._check_authorization(update):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        await update.message.reply_text(
            "📊 Starting tracking (Supabase)...\n_This will take a few minutes_",
            parse_mode='Markdown'
        )
        
        try:
            tracker = self.tracker_class(user_id=self.user_id)
            
            # Obtener primera app activa del usuario
            apps = self.supabase.get_user_apps(self.user_id, active_only=True)
            
            if not apps:
                await update.message.reply_text(
                    "❌ No apps configured.\n\n"
                    "💡 Run `python import_csv_to_supabase.py` first"
                )
                return
            
            app_id = apps[0]['id']
            result = tracker.track_app(app_id, send_alerts=False)
            
            if result['success']:
                message = f"""
✅ *Tracking Completed*

📱 App: {result['app_name']}
📊 Rankings: {result['rankings_tracked']}
🕐 Timestamp: {datetime.fromisoformat(result['timestamp']).strftime('%H:%M:%S')}

💡 Use /rankings to see results
"""
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Error: {result['error']}")
        
        except Exception as e:
            logger.error(f"❌ Error in tracking: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Error:\n`{str(e)}`",
                parse_mode='Markdown'
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Ver estado actual"""
        if not self._check_authorization(update):
            return
        
        try:
            apps = self.supabase.get_user_apps(self.user_id, active_only=True)
            
            if not apps:
                await update.message.reply_text("❌ No apps configured")
                return
            
            app = apps[0]
            
            # Obtener keywords activas
            keywords = self.supabase.client.table('keywords')\
                .select('id, keyword')\
                .eq('app_id', app['id'])\
                .eq('is_active', True)\
                .execute()
            
            total_kw = len(keywords.data)
            
            # Obtener últimos rankings
            top10 = 0
            top30 = 0
            
            for kw in keywords.data[:50]:  # Limitar para performance
                ranking = self.supabase.client.table('rankings')\
                    .select('rank')\
                    .eq('keyword_id', kw['id'])\
                    .order('tracked_at', desc=True)\
                    .limit(1)\
                    .execute()
                
                if ranking.data:
                    rank = ranking.data[0]['rank']
                    if rank <= 10:
                        top10 += 1
                    if rank <= 30:
                        top30 += 1
            
                        message = f"""
📊 *Current Status* (Supabase)

📱 App: {app['name']}
📦 Active keywords: {total_kw}

🏆 Distribution:
    • Top 10: {top10}
    • Top 30: {top30}

🕐 Last updated: {datetime.now().strftime('%H:%M')}
"""
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error in status: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def rankings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /rankings - Ver rankings actuales"""
        if not self._check_authorization(update):
            return

        await update.message.reply_text("📊 Fetching rankings...", parse_mode='Markdown')

        try:
            if self.use_supabase:
                apps = self.supabase.get_user_apps(self.user_id, active_only=True)
                if not apps:
                    await update.message.reply_text("❌ No apps configured")
                    return

                app = apps[0]
                keywords = self.supabase.client.table("keywords")\
                    .select("id, keyword, country")\
                    .eq("app_id", app["id"])\
                    .eq("is_active", True)\
                    .execute()

                rankings_list = []
                for kw in keywords.data:
                    ranking = self.supabase.client.table("rankings")\
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

                rankings_list.sort(key=lambda x: x[0])

                message = "📊 *Current Rankings*\n\n"
                message += "\n".join([r[1] for r in rankings_list[:20]])
                message += f"\n\n_Showing top 20 of {len(rankings_list)}_"

            else:
                import pandas as pd
                ranks_file = Path(self.config['storage']['ranks_file'])
                if not ranks_file.exists():
                    await update.message.reply_text("❌ No hay datos. Ejecuta /track primero")
                    return

                df = pd.read_csv(ranks_file)
                df['date'] = pd.to_datetime(df['date'])
                latest = df[df['date'] == df['date'].max()]
                latest = latest.sort_values('rank')

                rows = []
                for _, row in latest.head(20).iterrows():
                    rank = int(row['rank'])
                    emoji = "🏆" if rank <= 10 else "⭐" if rank <= 50 else "📍"
                    rows.append(f"{emoji} #{rank:3d} - {row['keyword']} ({row['country']})")

                message = "📊 *Rankings Actuales*\n\n" + "\n".join(rows)

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in rankings: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def changes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /changes - Cambios últimas 24h"""
        if not self._check_authorization(update):
            return

        await update.message.reply_text("⚡ Calculating changes...", parse_mode='Markdown')

        try:
            since = datetime.now() - timedelta(hours=24)

            if self.use_supabase:
                apps = self.supabase.get_user_apps(self.user_id, active_only=True)
                if not apps:
                    await update.message.reply_text("❌ No apps configured")
                    return

                app = apps[0]
                keywords = self.supabase.client.table("keywords")\
                    .select("id, keyword")\
                    .eq("app_id", app["id"])\
                    .eq("is_active", True)\
                    .limit(30)\
                    .execute()

                changes = []
                for kw in keywords.data:
                    recent = self.supabase.client.table("rankings")\
                        .select("rank, tracked_at")\
                        .eq("keyword_id", kw["id"])\
                        .order("tracked_at", desc=True)\
                        .limit(1)\
                        .execute()

                    previous = self.supabase.client.table("rankings")\
                        .select("rank, tracked_at")\
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

                message = "⚡ *Changes in the last 24h*\n\n"
                if changes:
                    for _, change, keyword, old, new in changes[:15]:
                        if change < 0:
                            emoji = "📈"
                            text = f"↑{abs(change)}"
                        else:
                            emoji = "📉"
                            text = f"↓{change}"
                        message += f"{emoji} {text} - {keyword}\n"
                        message += f"   #{old} → #{new}\n\n"
                else:
                    message += "_No significant changes_"

            else:
                message = "⚡ *Cambios últimas 24h*\n\n_No disponible en modo CSV_"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in changes: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /alerts"""
        if not self._check_authorization(update):
            return

        await update.message.reply_text("🚨 Alerts are under development. Use /changes for now.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        if not self._check_authorization(update):
            return
        
        help_text = f"""
    ℹ️ *Help - ASO Rank Guard Bot*

    *Mode:* Supabase

    *Commands:*
    📊 /track - Run tracking
    📈 /status - Current status
    🏆 /rankings - Current rankings
    ⚡ /changes - Changes (24h)
    🚨 /alerts - Alerts
    ℹ️ /help - Help

    *Notes:*
    • Tracking takes ~4 min
    • Data is stored in Supabase
    • Use the buttons to navigate
    """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_button_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar texto de los botones"""
        text = update.message.text
        
        if "/track" in text:
            await self.track_command(update, context)
        elif "/status" in text:
            await self.status_command(update, context)
        elif "/rankings" in text:
            await self.rankings_command(update, context)
        elif "/changes" in text:
            await self.changes_command(update, context)
        elif "/alerts" in text:
            await self.alerts_command(update, context)
        elif "/help" in text:
            await self.help_command(update, context)
    
    def run(self):
        """Iniciar el bot"""
        logger.info("🤖 Iniciando ASO Rank Guard Bot (Hybrid)...")
        logger.info(f"📱 Chat ID autorizado: {self.allowed_chat_id}")
        logger.info(f"🔧 Modo: {'Supabase' if self.use_supabase else 'CSV'}")
        
        app = Application.builder().token(self.token).build()
        
        # Registrar comandos
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("track", self.track_command))
        app.add_handler(CommandHandler("status", self.status_command))
        app.add_handler(CommandHandler("rankings", self.rankings_command))
        app.add_handler(CommandHandler("changes", self.changes_command))
        app.add_handler(CommandHandler("alerts", self.alerts_command))
        
        # Handler para botones
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_button_text
        ))
        
        logger.info("✅ Bot iniciado - Esperando comandos...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Punto de entrada"""
    try:
        # Auto-detectar modo
        bot = HybridASOBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n👋 Bot detenido")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
