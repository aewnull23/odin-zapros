import logging
from datetime import date

from src.ai.filters_builder import build_filters, merge_filters
from src.ai.parser import parse_query
from src.ai.web_search import fetch_travel_web_context
from src.api.schemas import ParsedQuery, SearchFilters
from src.util.nights import trip_nights

logger = logging.getLogger(__name__)


async def analyze_travel_query(
    query: str,
    *,
    use_web: bool = True,
    reference_date: date | None = None,
) -> tuple[ParsedQuery, SearchFilters, str | None]:
    """Полный цикл: интернет-контекст → NLP → автоматические фильтры."""
    prelim = await parse_query(query, reference_date=reference_date)
    web_insight: str | None = None
    if use_web:
        _, web_insight = await fetch_travel_web_context(query, prelim.location)
        if web_insight:
            enriched = await parse_query(
                query,
                reference_date=reference_date,
                web_context=web_insight,
            )
            if enriched.confidence >= prelim.confidence or enriched.location:
                prelim = enriched

    nights = trip_nights(prelim)
    filters = build_filters(prelim, query, nights)
    if prelim.filters and prelim.filters.model_dump(exclude_defaults=True):
        filters = merge_filters(filters, prelim.filters.model_dump(exclude_none=True))

    prelim.filters = filters
    return prelim, filters, web_insight
