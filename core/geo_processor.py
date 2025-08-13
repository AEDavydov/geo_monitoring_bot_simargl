# core/geo_processor.py

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import logging

logger = logging.getLogger(__name__)

POLYGON_PATH = "data/Final_CFO(9region).geojson"

# Погрешности по источнику в метрах
SOURCE_TOLERANCE = {
    "modis": 1000,
    "viirs_suomi": 300,
    "viirs_noaa20": 375,
    "viirs_noaa21": 375
}

def load_polygons():
    """
    Загружает полигоны, переопределяет ошибочный CRS (в метрах) и переводит в EPSG:4326
    """
    try:
        gdf = gpd.read_file(POLYGON_PATH)

        # Принудительно переопределяем CRS как EPSG:3857 (метры)
        logger.warning("[POLYGONS] Переопределяем CRS вручную: EPSG:3857 (метры)")
        gdf.set_crs("EPSG:3857", inplace=True, allow_override=True)

        gdf = gdf.to_crs("EPSG:4326")
        logger.info("[POLYGONS] CRS приведён к EPSG:4326")
        logger.info(f"[POLYGONS] Загружено {len(gdf)} полигонов из {POLYGON_PATH}")
        return gdf

    except Exception as e:
        logger.error(f"[POLYGONS] Ошибка загрузки: {e}")
        return gpd.GeoDataFrame()

def find_matches_with_tolerance(fire_points_gdf, polygon_gdf):
    """
    Ищет пересечения с учётом буфера (погрешности) по источнику.
    """
    if fire_points_gdf.empty or polygon_gdf.empty:
        logger.warning("[MATCH+TOLERANCE] Нет данных для анализа")
        return gpd.GeoDataFrame()

    # Убедимся, что CRS совпадают
    if fire_points_gdf.crs != polygon_gdf.crs:
        polygon_gdf = polygon_gdf.to_crs(fire_points_gdf.crs)

    results = []

    for source, group in fire_points_gdf.groupby("source"):
        base_name = source.replace("_archive", "")  # удаляем _archive, если есть
        tolerance_m = SOURCE_TOLERANCE.get(base_name, 500)

        # Преобразуем в метры
        group = group.to_crs(epsg=3857)
        polygons_m = polygon_gdf.to_crs(epsg=3857)

        # Создаём буфер вокруг точки
        group["geometry"] = group.geometry.buffer(tolerance_m)

        # Ищем пересечения с полигонами
        matches = gpd.sjoin(group, polygons_m, how="inner", predicate="intersects")

        # Возвращаем в долготу/широту
        matches = matches.to_crs("EPSG:4326")
        results.append(matches)

        logger.info(f"[MATCH+TOLERANCE] {source}: {len(matches)} совпадений при ±{tolerance_m} м")

    if results:
        return pd.concat(results, ignore_index=True)
    else:
        logger.warning("[MATCH+TOLERANCE] Ни один источник не дал совпадений")
        return gpd.GeoDataFrame()
