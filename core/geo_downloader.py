# core/geo_downloader.py

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import datetime
import logging

logger = logging.getLogger(__name__)

# Онлайн-источники (обновлённые ссылки)
SOURCES = {
    "modis": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Russia_Asia_24h.csv",
    "viirs_suomi": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Russia_Asia_24h.csv",
    "viirs_noaa20": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Russia_Asia_24h.csv",
    "viirs_noaa21": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-21-viirs-c2/csv/J2_VIIRS_C2_Russia_Asia_24h.csv"
}

def download_firms_data():
    """
    Загружает термоточки из FIRMS (онлайн-источники по России и Азии).
    """
    frames = []
    broken_sources = []

    for name, url in SOURCES.items():
        try:
            logger.info(f"[FIRMS] Загрузка {name} → {url}")
            df = pd.read_csv(url)

            if df.empty:
                logger.warning(f"[FIRMS] Пустой CSV: {name}")
                continue

            geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
            gdf["source"] = name
            gdf["downloaded_at"] = datetime.datetime.utcnow().isoformat()
            frames.append(gdf)

        except Exception as e:
            logger.error(f"[FIRMS] Ошибка загрузки {name}: {e}")
            broken_sources.append((name, url))

    if broken_sources:
        logger.warning("[FIRMS] ⚠️ Не удалось загрузить источники:")
        for name, url in broken_sources:
            logger.warning(f"  ⛔ {name}: {url}")

    if not frames:
        logger.error("[FIRMS] ❌ Ни один источник не сработал.")
        return gpd.GeoDataFrame()

    result = pd.concat(frames, ignore_index=True)
    logger.info(f"[FIRMS] ✅ Загружено {len(result)} термоточек из {len(frames)} источников.")
    return result
def load_local_archives():
    """
    Загружает термоточки из локальных архивных CSV (апрель).
    """
    base_dir = "data/firms_april"
    files = {
        "modis_archive": f"{base_dir}/fire_nrt_M-C61_638549.csv",
        "viirs_suomi_archive": f"{base_dir}/fire_nrt_SV-C2_638552.csv",
        "viirs_noaa20_archive": f"{base_dir}/fire_nrt_J1V-C2_638550.csv",
        "viirs_noaa21_archive": f"{base_dir}/fire_nrt_J2V-C2_638551.csv"
    }

    frames = []
    for source, path in files.items():
        try:
            df = pd.read_csv(path)
            if df.empty:
                logger.warning(f"[ARCHIVE] Пустой CSV: {path}")
                continue

            geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
            gdf["source"] = source
            gdf["downloaded_at"] = datetime.datetime.utcnow().isoformat()
            frames.append(gdf)
            logger.info(f"[ARCHIVE] ✅ {source}: загружено {len(gdf)} точек")

        except Exception as e:
            logger.error(f"[ARCHIVE] Ошибка чтения {source}: {e}")

    if not frames:
        logger.error("[ARCHIVE] ❌ Ни один архив не загружен")
        return gpd.GeoDataFrame()

    return pd.concat(frames, ignore_index=True)
