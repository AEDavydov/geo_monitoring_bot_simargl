# bot_main.py

import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from tg.handlers import my_regions
from tg.handlers import (
    start, help_command, about, contacts, unsubscribe,
    regions, region_callback, my_alerts, analyze
)

from utils.logger import setup_logger, error_handler

# Загрузка токена и логов
load_dotenv()
setup_logger()

TOKEN = os.getenv("TELEGRAM_TOKEN")
application = ApplicationBuilder().token(TOKEN).build()

# Команды пользователя
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about))
application.add_handler(CommandHandler("contacts", contacts))
application.add_handler(CommandHandler("unsubscribe", unsubscribe))
application.add_handler(CommandHandler("regions", regions))
application.add_handler(CommandHandler("my_alerts", my_alerts))

# Админ-команды
application.add_handler(CommandHandler("analyze", analyze))

# Callback кнопок
application.add_handler(CallbackQueryHandler(region_callback, pattern="^region_"))
application.add_handler(CallbackQueryHandler(region_callback, pattern="^region_save$"))
application.add_handler(CallbackQueryHandler(my_alerts, pattern="^my_alerts$"))
application.add_handler(CallbackQueryHandler(about, pattern="^about$"))
application.add_handler(CallbackQueryHandler(contacts, pattern="^contacts$"))
application.add_handler(CallbackQueryHandler(unsubscribe, pattern="^unsubscribe$"))
application.add_handler(CallbackQueryHandler(regions, pattern="^region_open$"))
application.add_handler(CallbackQueryHandler(my_regions, pattern="^my_regions$"))

# Ошибки
application.add_error_handler(error_handler)

# Запуск
application.run_polling()
