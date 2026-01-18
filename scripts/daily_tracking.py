#!/usr/bin/env python3
"""
Daily tracking runner for Supabase + Telegram notification.
Runs tracking for the admin user's apps and posts a summary to Telegram.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load env
load_dotenv()

# Ensure src/ is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import requests
from supabase_client import get_supabase_client
from rank_tracker_supabase import RankTrackerSupabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ALLOWED_CHATS", "").split(",")[0].strip()
    admin_email = os.getenv("ADMIN_EMAIL")

    if not token or not chat_id or not admin_email:
        logger.error("Missing TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_CHATS, or ADMIN_EMAIL")
        return

    supabase = get_supabase_client(use_service_role=True)
    user = supabase.get_user_by_email(admin_email)
    if not user:
        logger.error(f"Admin user not found: {admin_email}")
        return

    tracker = RankTrackerSupabase(user_id=user["id"])
    apps = supabase.get_user_apps(user["id"], active_only=True)

    if not apps:
        logger.warning("No active apps found for admin user")
        return

    results = []
    for app in apps:
        result = tracker.track_app(app["id"], send_alerts=False)
        results.append(result)

    # Build summary
    lines = ["✅ *Daily Tracking Completed*", ""]
    for r in results:
        if r.get("success"):
            lines.append(f"📱 {r['app_name']}: *{r['rankings_tracked']}* rankings")
        else:
            lines.append(f"❌ {r.get('app_name', 'App')}: {r.get('error', 'Error')}")

    lines.append("")
    lines.append(f"🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

    message = "\n".join(lines)
    send_telegram_message(token, chat_id, message)
    logger.info("Telegram summary sent")


if __name__ == "__main__":
    main()
