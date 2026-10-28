import json
from functools import lru_cache

from src.config import HOTELS_PATH, TOURS_PATH

STATIC_ALIASES: dict[str, str] = {
    "питер": "Санкт-Петербург",
    "спб": "Санкт-Петербург",
    "санкт-петербург": "Санкт-Петербург",
    "санкт петербург": "Санкт-Петербург",
    "москва": "Москва",
    "мск": "Москва",
    "сочи": "Сочи",
    "казань": "Казань",
    "махачкала": "Махачкала",
    "махачкале": "Махачкала",
    "дагестан": "Махачкала",
}


@lru_cache
def city_aliases() -> dict[str, str]:
    aliases = dict(STATIC_ALIASES)
    for path in (HOTELS_PATH, TOURS_PATH):
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            items = json.load(f)
        for item in items:
            city = item.get("city")
            if not city:
                continue
            key = city.lower()
            aliases[key] = city
    return aliases


def detect_city_in_text(text: str) -> str | None:
    lowered = text.lower()
    # длинные алиасы первыми
    for alias in sorted(city_aliases(), key=len, reverse=True):
        if alias in lowered:
            return city_aliases()[alias]
    return None


def normalize_city(location: str | None) -> str | None:
    if not location:
        return None
    key = location.lower().strip()
    return city_aliases().get(key, location.strip())
