# send_cached_alerts.py

import json
from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv()
from tg.notifier import send_alert_messages
import asyncio
ALERTS_FILE = Path("data/last_alerts.json")

if ALERTS_FILE.exists():
    alerts = json.loads(ALERTS_FILE.read_text())
    if alerts:
        print(f"📤 Отправка {len(alerts)} алертов подписчикам...")
        asyncio.run(send_alert_messages(alerts))
    else:
        print("⚠️ Нет алертов для отправки.")
else:
    print("⚠️ Файл с алертами не найден.")
