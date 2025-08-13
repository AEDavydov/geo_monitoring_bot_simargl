# tg/notifier.py

import logging
from telegram import Bot
from telegram.constants import ParseMode
from core.notifier import format_alert_message
from config import ADMIN_IDS
import asyncio
import json
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))

USERS_FILE = Path("data/users.json")
LOG_FILE = Path("data/sent_log.json")
REGIONS_FILE = Path("data/user_regions.json")


def load_user_ids():
    if USERS_FILE.exists():
        return json.loads(USERS_FILE.read_text())
    return []


def load_sent_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return []


def save_sent_log(log: list):
    LOG_FILE.write_text(json.dumps(log, ensure_ascii=False, indent=2))


def was_alert_sent(alert: dict, user_id: int, sent_log: list) -> bool:
    return any(
        entry["alert_id"] == alert["id"] and entry["user_id"] == user_id
        for entry in sent_log
    )


def log_sent_alert(alert: dict, user_id: int, sent_log: list):
    entry = {
        "user_id": user_id,
        "alert_id": alert["id"],
        "region": alert["region"],
        "title": alert["title"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "sent"
    }
    sent_log.append(entry)


def load_user_regions():
    if REGIONS_FILE.exists():
        return json.loads(REGIONS_FILE.read_text())
    return {}


async def send_alert_messages(alerts: list[dict]):
    if not alerts:
        logger.info("[TG] Нет АЛЕРТов для отправки.")
        return

    user_ids = load_user_ids()
    recipients = list(set(user_ids + ADMIN_IDS))
    sent_log = load_sent_log()
    user_regions = load_user_regions()

    for alert in alerts:
        message = format_alert_message(alert)

        for user_id in recipients:
            # 🔍 Фильтрация по интересующим регионам
            regions = user_regions.get(str(user_id), [])
            if regions and alert["region"] not in regions:
                continue

            if was_alert_sent(alert, user_id, sent_log):
                logger.info(f"[TG] ⚠️ Уже отправлялся → {user_id}, alert {alert['id']}")
                continue

            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                logger.info(f"[TG] ✅ Сообщение отправлено → {user_id}")
                log_sent_alert(alert, user_id, sent_log)
            except Exception as e:
                logger.error(f"[TG] ❌ Ошибка при отправке → {user_id}: {e}")

    save_sent_log(sent_log)
