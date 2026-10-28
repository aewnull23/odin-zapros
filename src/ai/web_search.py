import asyncio
import logging
import re

from src.config import get_settings

logger = logging.getLogger(__name__)


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


def _search_sync(query: str, max_results: int) -> list[dict[str, str]]:
    DDGS = _get_ddgs_client()
    if DDGS is None:
        logger.warning("Install ddgs or duckduckgo-search for web lookup")
        return []

    results: list[dict[str, str]] = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, region="ru-ru", max_results=max_results):
            results.append(
                {
                    "title": item.get("title") or "",
                    "snippet": item.get("body") or "",
                    "url": item.get("href") or "",
                }
            )
    return results


async def fetch_travel_web_context(user_query: str, location: str | None) -> tuple[list[dict[str, str]], str]:
    """Поиск в интернете: подсказки по направлению и ценам для AI."""
    settings = get_settings()
    if not settings.enable_web_search:
        return [], ""

    loc = location or _guess_location_from_query(user_query)
    search_q = f"{loc} отели туры цены 2026" if loc else f"{user_query} отели туры"
    try:
        raw = await asyncio.wait_for(
            asyncio.to_thread(_search_sync, search_q, settings.web_search_max_results),
            timeout=12.0,
        )
    except Exception as exc:
        logger.warning("Web search failed: %s", exc)
        return [], ""

    if not raw:
        return [], ""

    lines = []
    for i, r in enumerate(raw[:3], 1):
        snippet = re.sub(r"\s+", " ", r["snippet"])[:220]
        lines.append(f"{i}. {r['title']}: {snippet}")

    insight = "Кратко из интернета: " + " | ".join(lines)
    return raw, insight[:900]


def _guess_location_from_query(query: str) -> str | None:
    from src.geo.cities import detect_city_in_text

    return detect_city_in_text(query)
