import logging

logger = logging.getLogger(__name__)

ALERT_TEMPLATE = (
    "🛑 АЛЕРТ: Обнаружена термоточка в торфянике \"{title}\"!\n"
    "📍 Координаты в регионе {region}: <a href=\"{map_url}\">{lat:.5f}, {lon:.5f}</a>\n"
    "🚨 Необходимо выездное обследование!\n"
    "🔗 <a href=\"{wiki_url}\">Подробности в вики</a>"
)

def format_alert_message(alert: dict) -> str:
    try:
        return ALERT_TEMPLATE.format(**alert)
    except KeyError as e:
        logger.error(f"[NOTIFIER] Пропущено поле при генерации сообщения: {e}")
        return f"[Ошибка генерации уведомления для {alert.get('id')}]"
