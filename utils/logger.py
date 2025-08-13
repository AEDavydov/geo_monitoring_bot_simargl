import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS
import traceback

# === Настройка логирования ===
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/bot.log"),
            logging.StreamHandler()
        ]
    )

# === Централизованный обработчик ошибок ===
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Exception while handling update:", exc_info=context.error)

    try:
        tb = traceback.format_exception(None, context.error, context.error.__traceback__)
        msg = ''.join(tb)[-4000:]

        if ADMIN_IDS:
            await context.bot.send_message(
                chat_id=ADMIN_IDS[0],
                text="⚠️ Ошибка:\n<pre>{}</pre>".format(msg),
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error("Failed to send error to admin: %s", e)

# === Явный вызов при ошибке вручную ===
async def notify_admin_of_error(text: str, context: ContextTypes.DEFAULT_TYPE):
    logging.warning(text)
    if ADMIN_IDS:
        try:
            await context.bot.send_message(ADMIN_IDS[0], f"⚠️ {text}")
        except Exception as e:
            logging.error("Ошибка при отправке админу: %s", e)
