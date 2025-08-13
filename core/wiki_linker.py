import requests
import json
from pathlib import Path

CACHE_FILE = Path("data/wiki_cache.json")
BASE_SEARCH_URL = "https://wiki.simargl-team.ru/public/index.php?search="
BASE_ARTICLE_URL = "https://wiki.simargl-team.ru/index.php/"

# === Загрузка / сохранение кэша ===
def load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}

def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2))

# === Основная функция ===
def get_wiki_url(unique_id: str) -> str | None:
    cache = load_cache()
    if unique_id in cache:
        return cache[unique_id]

    try:
        resp = requests.get(BASE_SEARCH_URL + unique_id, timeout=5)
        if resp.status_code != 200:
            return None

        # Простая эвристика: ищем первую ссылку на статью
        for line in resp.text.splitlines():
            if "/index.php/" in line and "redlink=1" not in line:
                start = line.find("/index.php/")
                end = line.find("\"", start)
                if start != -1 and end != -1:
                    link = line[start:end].replace("&amp;", "&")
                    full_url = "https://wiki.simargl-team.ru" + link
                    cache[unique_id] = full_url
                    save_cache(cache)
                    return full_url

        # Если ничего не нашли
        cache[unique_id] = None
        save_cache(cache)
        return None

    except Exception as e:
        print(f"[wiki_linker] Ошибка при получении wiki для {unique_id}: {e}")
        return None
