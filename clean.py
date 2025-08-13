import os
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path("data")
DAYS_TO_KEEP = 10

def is_old(file: Path):
    if not file.name.startswith("last_alerts"):
        return False
    modified = datetime.fromtimestamp(file.stat().st_mtime)
    return datetime.now() - modified > timedelta(days=DAYS_TO_KEEP)

def main():
    for file in DATA_DIR.glob("last_alerts*.json"):
        if is_old(file):
            print(f"Удаляю устаревший файл: {file}")
            file.unlink()

if __name__ == "__main__":
    main()
