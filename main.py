# main.py

import argparse
import asyncio
from pathlib import Path
import json

from utils.logger import setup_logger
from tg.notifier import send_alert_messages
from core.geo_downloader import download_firms_data, load_local_archives
from core.geo_processor import load_polygons, find_matches_with_tolerance
from core.alert_generator import generate_alerts
from core.notifier import format_alert_message

def print_available_fields(df, label):
    print(f"\n📋 Доступные поля в {label}:")
    for col in df.columns:
        print(f" - {col}")

def run_main(source="online"):
    setup_logger()

    if source == "local":
        fire_gdf = load_local_archives()
    else:
        fire_gdf = download_firms_data()

    poly_gdf = load_polygons()
    matched = find_matches_with_tolerance(fire_gdf, poly_gdf)
    if matched.empty:
        print("❗ Совпадений не найдено.")
        return

    alerts = generate_alerts(matched)
    Path("data/last_alerts.json").write_text(json.dumps(alerts, ensure_ascii=False, indent=2))
    asyncio.run(send_alert_messages(alerts))

def debug_main(source="online"):
    setup_logger()

    if source == "local":
        print("📁 Загрузка термоточек из локального архива...")
        fire_gdf = load_local_archives()
    else:
        print("🌐 Загрузка термоточек с FIRMS (онлайн)...")
        fire_gdf = download_firms_data()

    print(f"🔥 Получено точек: {len(fire_gdf)}")
    print("\n📦 Загрузка полигонов...")
    poly_gdf = load_polygons()
    print(f"🗺️ Загружено полигонов: {len(poly_gdf)}")

    print("\n📌 Пример геометрии первой термоточки:")
    print(fire_gdf.iloc[0].geometry)

    print("\n📌 Центроид первого полигона:")
    print(poly_gdf.iloc[0].geometry.centroid)

    print("\n🔍 Анализ пересечений с учётом погрешности...")
    matched = find_matches_with_tolerance(fire_gdf, poly_gdf)
    print(f"✅ Найдено совпадений: {len(matched)}")

    if matched.empty:
        print("\n❗ Совпадений не найдено.")
        return

    alerts = generate_alerts(matched)
    print(f"\n🚨 Найдено АЛЕРТов: {len(alerts)}")
    for alert in alerts[:5]:
        print("\n📤 Пример сообщения:")
        print(format_alert_message(alert))

    Path("data/last_alerts.json").write_text(json.dumps(alerts, ensure_ascii=False, indent=2))
    print(f"💾 Сохранено {len(alerts)} алертов.")
    asyncio.run(send_alert_messages(alerts))

def parse_args():
    parser = argparse.ArgumentParser(description="Анализ термоточек")
    parser.add_argument("--source", choices=["online", "local"], default="online", help="Источник термоточек")
    parser.add_argument("--debug", action="store_true", help="Выводить отладочные сообщения")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        debug_main(source=args.source)
    else:
        run_main(source=args.source)
