import json
from pathlib import Path
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_IDS, send_if_no_region
from main import run_main
from utils.logger import notify_admin_of_error

USERS_FILE = Path("data/users.json")
REGIONS_FILE = Path("data/user_regions.json")
ALERTS_FILE = Path("data/last_alerts.json")

AVAILABLE_REGIONS = [
    "Владимирская область", "Ивановская область", "Калужская область",
    "Костромская область", "Московская область", "Рязанская область",
    "Смоленская область", "Тверская область", "Ярославская область",
]

def load_users():
    return json.loads(USERS_FILE.read_text()) if USERS_FILE.exists() else []

def save_user(user_id: int):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        USERS_FILE.write_text(json.dumps(users))

def remove_user(user_id: int):
    users = load_users()
    if user_id in users:
        users.remove(user_id)
        USERS_FILE.write_text(json.dumps(users))

def load_user_regions():
    return json.loads(REGIONS_FILE.read_text()) if REGIONS_FILE.exists() else {}

def save_user_regions(data):
    REGIONS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def load_last_alerts():
    return json.loads(ALERTS_FILE.read_text()) if ALERTS_FILE.exists() else []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        save_user(user_id)
        user_regions = load_user_regions().get(str(user_id), [])
        regions_info = f"\n📍 Выбранные регионы: {', '.join(user_regions)}" if user_regions else ""

        text = (
            "Привет!\n"
            "Я — *торфяной хранитель* команды Симаргл.\n"
            "Буду каждый день присылать вам термоточки в торфяниках или рядом с ними "
            "в выбранных вами регионах.\n\n"
            "📡 Точки обрабатываются около полуночи,\n"
            "📬 Приходят в 8 утра.\n"
            "Вместе с каждой точкой вы получите координаты, регион, ID торфяника и ссылку "
            "на его карточку в нашей базе.\n"
            f"{regions_info}"
        )

        keyboard = [
            [InlineKeyboardButton("📍 Выбрать регионы", callback_data="region_open")],
            [InlineKeyboardButton("🗺 Мои регионы", callback_data="my_regions")],
            [InlineKeyboardButton("🔥 Вчерашние термоточки", callback_data="my_alerts")],
            [InlineKeyboardButton("ℹ Как бот работает", callback_data="about")],
            [InlineKeyboardButton("📬 Наши контакты", callback_data="contacts")],
            [InlineKeyboardButton("🚫 Отписаться", callback_data="unsubscribe")],
        ]

        msg = update.message or update.callback_query.message
        await msg.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await notify_admin_of_error(f"Ошибка в /start: {e}", context)

async def my_regions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.callback_query.message
        user_id = update.effective_user.id
        user_regions = load_user_regions()
        selected = user_regions.get(str(user_id))

        if selected:
            text = "📍 *Ваши регионы:*\n" + "\n".join(f"• {r}" for r in selected)
        else:
            text = "📍 *Вы не выбрали регионы.*\nВы будете получать оповещения по всем регионам:\n" + \
                   "\n".join(f"• {r}" for r in AVAILABLE_REGIONS)

        await msg.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await notify_admin_of_error(f"Ошибка в /my_regions: {e}", context)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.message or update.callback_query.message
        text = (
            "*Как бот работает*\n\n"
            "Бот каждый день проверяет, попадают ли термоточки в границы крупных и горимых торфяников "
            "Центральной России: Владимирская, Ивановская, Калужская, Костромская, Московская, Рязанская, "
            "Смоленская, Тверская, Ярославская. Всего в базе около 300 торфяников.\n\n"
            "Анализируются термоточки VIIRS, MODIS, Suomi NPP с учётом погрешности.\n"
            "Данные приходят в 8 утра.\n\n"
            "Каждое сообщение содержит координаты, регион, ID торфяника и ссылку. "
            "_Около 30% пожаров не имеют термоточек._"
        )
        await msg.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await notify_admin_of_error(f"Ошибка в /about: {e}", context)

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.message or update.callback_query.message
        text = (
            "*Контакты команды Симаргл*\n\n"
            "Этот бот создан командой добровольных лесных пожарных Симаргл.\n"
            "📬 info@simargl-team.ru\n"
            "💬 Telegram: @simargl_team\n"
            "🌐 ВКонтакте: vk.com/simargl_team\n\n"
            "Хотите стать волонтёром? Пишите нам!"
        )
        await msg.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await notify_admin_of_error(f"Ошибка в /contacts: {e}", context)

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        remove_user(user_id)
        regions = load_user_regions()
        if str(user_id) in regions:
            del regions[str(user_id)]
            save_user_regions(regions)
        msg = update.message or update.callback_query.message
        await msg.reply_text("❎ Вы отписались от рассылки. Вернуться — /start")
    except Exception as e:
        await notify_admin_of_error(f"Ошибка в /unsubscribe: {e}", context)

async def regions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        current = load_user_regions().get(str(user_id), [])

        buttons = [
            [InlineKeyboardButton(f"{'✅' if r in current else '⬜️'} {r}", callback_data=f"region_{i}")]
            for i, r in enumerate(AVAILABLE_REGIONS)
        ]
        buttons.append([InlineKeyboardButton("💾 Сохранить", callback_data="region_save")])
        reply_markup = InlineKeyboardMarkup(buttons)

        if update.callback_query:
            try:
                await update.callback_query.message.delete()
            except:
                pass
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Выберите нужные вам регионы. Для этого нажмите на регион, затем нажмите «Сохранить».",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "Выберите нужные вам регионы. Для этого нажмите на регион, затем нажмите «Сохранить».",
                reply_markup=reply_markup
            )
    except Exception as e:
        await notify_admin_of_error(f"Ошибка в /regions: {e}", context)

async def region_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        data = query.data

        # Открытие выбора регионов
        if data == "region_open":
            full = load_user_regions()
            context.user_data["temp_regions"] = full.get(str(user_id), []).copy()
            return await regions(update, context)

        # Временный список выбранных
        temp = context.user_data.get("temp_regions", [])

        if data.startswith("region_") and data != "region_save":
            index = int(data.split("_")[1])
            region = AVAILABLE_REGIONS[index]
            if region in temp:
                temp.remove(region)
            else:
                temp.append(region)
            context.user_data["temp_regions"] = temp

            buttons = [
                [InlineKeyboardButton(f"{'✅' if r in temp else '⬜️'} {r}", callback_data=f"region_{i}")]
                for i, r in enumerate(AVAILABLE_REGIONS)
            ]
            buttons.append([InlineKeyboardButton("💾 Сохранить", callback_data="region_save")])
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
            return

        elif data == "region_save":
            user_regions = load_user_regions()
            selected = context.user_data.get("temp_regions", [])
            user_regions[str(user_id)] = selected
            save_user_regions(user_regions)

            if selected:
                await query.edit_message_text(f"✅ Вы подписаны на термоточки из: {', '.join(selected)}")
            else:
                await query.edit_message_text("📭 Вы не выбрали ни одного региона.")

            await start(update, context)

    except Exception as e:
        await notify_admin_of_error(f"Ошибка в region_callback: {e}", context)

async def my_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        alerts = load_last_alerts()
        regions = load_user_regions().get(str(user_id), [])
        results = {}

        for a in alerts:
            if not regions or a["region"] in regions:
                results.setdefault(a["region"], []).append(a)

        if not results:
            msg = update.message or update.callback_query.message
            await msg.reply_text("🔥 Вчера термоточек в ваших регионах не было.")
            return

        for region, region_alerts in results.items():
            text = f"📍 *{region}* — {len(region_alerts)} точек\n"
            for a in region_alerts:
                text += f"- {a.get('date', 'нет даты')} {a['lat']:.4f}, {a['lon']:.4f}\n"
            await update.effective_message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await notify_admin_of_error(f"Ошибка в /my_alerts: {e}", context)

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("⛔️ Недостаточно прав")
            return
        await update.message.reply_text("📡 Анализ начат…")
        count = await run_main()
        await update.message.reply_text(f"✅ Анализ завершён: найдено {count} совпадений.")
    except Exception as e:
        await notify_admin_of_error(f"Ошибка в /analyze: {e}", context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        regions = load_user_regions().get(str(user_id), [])
        regions_info = f"\n📍 Выбранные регионы: {', '.join(regions)}" if regions else ""

        base_cmds = (
            "/start — запустить бота\n"
            "/unsubscribe — отписаться\n"
            "/regions — выбрать регионы\n"
            "/my_alerts — вчерашние термоточки\n"
            "/about — как работает бот\n"
            "/contacts — контакты команды\n"
            "/help — справка"
        )
        if user_id in ADMIN_IDS:
            admin_cmds = "\n\n🔐 Админ-команды:\n/analyze — запустить анализ"
            await update.message.reply_text("ℹ️ Команды:\n" + base_cmds + admin_cmds + regions_info)
        else:
            await update.message.reply_text("ℹ️ Команды:\n" + base_cmds + regions_info)
    except Exception as e:
        await notify_admin_of_error(f"Ошибка в /help: {e}", context)
