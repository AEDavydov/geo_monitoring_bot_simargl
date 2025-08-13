import logging
from core.wiki_linker import get_wiki_url
from urllib.parse import unquote

logger = logging.getLogger(__name__)

def generate_alerts(matched_gdf) -> list[dict]:
    if matched_gdf.empty:
        logger.warning("[ALERT] Нет совпадений — АЛЕРТы не формируются.")
        return []

    alerts = []
    grouped = matched_gdf.groupby("unique_id")

    for uid, group in grouped:
        count = len(group)
        row = group.iloc[0]
        region = row.get("region", "")
        district = row.get("district", "")
        name = f"{region} — {district}".strip("— ")
        lat = row["latitude"]
        lon = row["longitude"]

        try:
            unique_id_str = str(int(row.get("unique_id", 0))).strip()
        except Exception as e:
            logger.warning(f"[ALERT] Невозможно извлечь unique_id: {e}")
            unique_id_str = ""

        wiki_url = get_wiki_url(unique_id_str) if unique_id_str else "https://wiki.simargl-team.ru"

        # Формируем читаемый заголовок
        title_raw = wiki_url.split("/")[-1]
        title_decoded = unquote(title_raw)
        parts = title_decoded.split("_")

        if parts and parts[-1].isdigit():
            title_text = " ".join(parts[:-1])
            title_id = parts[-1]
            title = f"{title_text} (id {title_id})"
        else:
            title = title_decoded

        map_url = f"https://yandex.ru/maps/?ll={lon},{lat}&z=13"

        alert = {
            "id": uid,
            "name": name,
            "count": count,
            "lat": lat,
            "lon": lon,
            "wiki_url": wiki_url,
            "region": region,
            "title": title,
            "map_url": map_url
        }

        logger.info(f"[ALERT] 🛑 {uid} — {count} точек → {wiki_url}")
        alerts.append(alert)

    return alerts
