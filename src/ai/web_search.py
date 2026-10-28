import asyncio
import logging
import re
from urllib.parse import urlparse

from src.config import get_settings

logger = logging.getLogger(__name__)

# Сайты-агрегаторы новостей часто попадают в DDG вместо travel-выдачи
BLOCKED_HOST_FRAGMENTS = (
    "lenta.ru",
    "mk.ru",
    "dzen.ru",
    "zen.yandex",
    "ria.ru",
    "rbc.ru",
    "tass.ru",
    "gazeta.ru",
    "interfax",
    "news.",
    "novosti",
)

TRAVEL_KEYWORDS = re.compile(
    r"отел|гостин|тур|экскурс|прожив|бронир|booking|ostrovok|travel|"
    r"курорт|номер|ноч|travel|trip|hotel|hostel|апарт|sea|мор|пляж",
    re.I,
)

PREFERRED_HOST_FRAGMENTS = (
    "ostrovok",
    "booking.",
    "trip.",
    "travel",
    "101hotels",
    "sutochno",
    "tutu.",
    "level.travel",
    "onlinetours",
    "travelata",
    "cian.ru/travel",
    "tripadvisor",
)


def _get_ddgs_client():
    try:
        from ddgs import DDGS

        return DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS

            return DDGS
        except ImportError:
            return None


def _host(url: str) -> str:
    try:
        return (urlparse(url).netloc or "").lower()
    except Exception:
        return ""


def _is_blocked(result: dict[str, str]) -> bool:
    h = _host(result.get("url") or "")
    title_snip = (result.get("title") or "") + " " + (result.get("snippet") or "")
    if any(b in h for b in BLOCKED_HOST_FRAGMENTS):
        return True
    if re.search(r"новост|news today|главные новости|события в мире", title_snip, re.I):
        return True
    return False


def _is_travel_relevant(result: dict[str, str], location: str | None) -> bool:
    if _is_blocked(result):
        return False
    text = f"{result.get('title', '')} {result.get('snippet', '')}"
    if not TRAVEL_KEYWORDS.search(text):
        return False
    if location:
        loc_lower = location.lower()
        # хотя бы город или регион в тексте, либо trusted travel site
        h = _host(result.get("url") or "")
        if loc_lower.split()[0] not in text.lower() and not any(p in h for p in PREFERRED_HOST_FRAGMENTS):
            return False
    return True


def _score_result(result: dict[str, str]) -> int:
    h = _host(result.get("url") or "")
    score = 0
    if any(p in h for p in PREFERRED_HOST_FRAGMENTS):
        score += 10
    if TRAVEL_KEYWORDS.search(result.get("title") or ""):
        score += 3
    if TRAVEL_KEYWORDS.search(result.get("snippet") or ""):
        score += 1
    return score


def _search_sync(queries: list[str], max_results: int) -> list[dict[str, str]]:
    DDGS = _get_ddgs_client()
    if DDGS is None:
        logger.warning("Install ddgs or duckduckgo-search for web lookup")
        return []

    seen_urls: set[str] = set()
    merged: list[dict[str, str]] = []

    with DDGS() as ddgs:
        for query in queries:
            try:
                for item in ddgs.text(query, region="ru-ru", max_results=max_results):
                    url = item.get("href") or ""
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    merged.append(
                        {
                            "title": item.get("title") or "",
                            "snippet": item.get("body") or "",
                            "url": url,
                        }
                    )
            except Exception as exc:
                logger.warning("DDG query failed %r: %s", query, exc)

    return merged


def _build_queries(user_query: str, location: str | None) -> list[str]:
    loc = location or "Россия"
    return [
        f"{loc} отели бронирование цены",
        f"{loc} туры экскурсии отдых",
        f"site:ostrovok.ru {loc}" if location else f"{user_query} отель",
    ]


async def fetch_travel_web_context(user_query: str, location: str | None) -> tuple[list[dict[str, str]], str]:
    """Поиск в интернете: только travel-релевантные snippets (без ленты новостей)."""
    settings = get_settings()
    if not settings.enable_web_search:
        return [], ""

    loc = location or _guess_location_from_query(user_query)
    queries = _build_queries(user_query, loc)

    try:
        raw = await asyncio.wait_for(
            asyncio.to_thread(_search_sync, queries, settings.web_search_max_results),
            timeout=14.0,
        )
    except Exception as exc:
        logger.warning("Web search failed: %s", exc)
        return [], ""

    relevant = [r for r in raw if _is_travel_relevant(r, loc)]
    relevant.sort(key=_score_result, reverse=True)
    relevant = relevant[:3]

    if not relevant:
        logger.info("Web search: no travel-relevant results, hiding insight")
        return [], ""

    lines = []
    for i, r in enumerate(relevant, 1):
        snippet = re.sub(r"\s+", " ", r["snippet"])[:180]
        lines.append(f"{i}. {r['title']}: {snippet}")

    insight = "Подсказки из открытых источников (только про поездки): " + " | ".join(lines)
    return relevant, insight[:900]


def _guess_location_from_query(query: str) -> str | None:
    from src.geo.cities import detect_city_in_text

    return detect_city_in_text(query)
