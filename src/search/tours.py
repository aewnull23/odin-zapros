import json
from functools import lru_cache

from src.api.schemas import ParsedQuery, SearchFilters, SearchTourResult, Tour
from src.config import TOURS_PATH
from src.geo.cities import normalize_city

WEIGHT_TAG = 10.0
WEIGHT_RATING = 7.0


@lru_cache
def load_tours() -> list[Tour]:
    if not TOURS_PATH.exists():
        return []
    with open(TOURS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return [Tour.model_validate(t) for t in raw]


def _passes_tour_filters(tour: Tour, filters: SearchFilters) -> bool:
    if filters.max_total_price and tour.price_total > filters.max_total_price * 1.1:
        return False
    for tag in filters.required_tags:
        if tag not in tour.tags:
            return False
    return True


def _tour_reason(tour: Tour, parsed: ParsedQuery) -> str:
    bits = [f"Тур на {tour.duration_days} дн. в {tour.city}"]
    if parsed.budget_max and tour.price_total <= parsed.budget_max:
        bits.append(f"укладывается в бюджет ({tour.price_total:,} ₽)".replace(",", " "))
    matched = [t for t in parsed.preferences if t in tour.tags]
    if matched:
        bits.append("совпадает с пожеланиями: " + ", ".join(matched))
    return ". ".join(bits) + "."


def search_tours(
    parsed: ParsedQuery,
    filters: SearchFilters | None = None,
    limit: int = 8,
) -> list[SearchTourResult]:
    filters = filters or parsed.filters
    tours = load_tours()
    city = normalize_city(parsed.location)

    filtered: list[Tour] = []
    for t in tours:
        if city and t.city.lower() != city.lower():
            continue
        if not _passes_tour_filters(t, filters):
            continue
        filtered.append(t)

    if not filtered and city:
        filtered = [t for t in tours if t.city.lower() == city.lower()]

    scored: list[SearchTourResult] = []
    for t in filtered:
        score = t.rating * WEIGHT_RATING
        for pref in parsed.preferences:
            if pref in t.tags:
                score += WEIGHT_TAG
        if parsed.budget_max and t.price_total <= parsed.budget_max:
            score += 8.0
        scored.append(
            SearchTourResult(
                **t.model_dump(),
                match_score=round(score, 2),
                ai_reason=_tour_reason(t, parsed),
            )
        )

    if filters.sort_by == "price":
        scored.sort(key=lambda x: x.price_total)
    elif filters.sort_by == "rating":
        scored.sort(key=lambda x: x.rating, reverse=True)
    else:
        scored.sort(key=lambda x: x.match_score, reverse=True)

    return scored[:limit]
