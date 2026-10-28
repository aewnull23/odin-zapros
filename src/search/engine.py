import json
from functools import lru_cache

from src.api.schemas import Hotel, ParsedQuery, SearchFilters, SearchHotelResult
from src.config import HOTELS_PATH
from src.geo.cities import normalize_city
from src.search.rank_reasons import build_ai_reason
from src.util.nights import trip_nights

WEIGHT_TAG = 12.0
WEIGHT_RATING = 8.0
WEIGHT_BUDGET = 10.0
WEIGHT_CENTER = 6.0
PENALTY_DISTANCE = 2.0


@lru_cache
def load_hotels() -> list[Hotel]:
    with open(HOTELS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return [Hotel.model_validate(h) for h in raw]


def _score_hotel(hotel: Hotel, parsed: ParsedQuery, nights: int) -> float:
    score = 0.0
    for pref in parsed.preferences:
        if pref in hotel.tags:
            score += WEIGHT_TAG
    score += hotel.rating * WEIGHT_RATING

    total = hotel.price_per_night * nights
    if parsed.budget_max:
        if total <= parsed.budget_max:
            ratio = total / parsed.budget_max
            score += WEIGHT_BUDGET * (1.0 - abs(ratio - 0.75))
        else:
            score -= (total - parsed.budget_max) / max(parsed.budget_max, 1) * 15

    if "center" in parsed.preferences or "nevsky" in parsed.preferences:
        if hotel.distance_to_center_km <= 1.0:
            score += WEIGHT_CENTER
        score -= hotel.distance_to_center_km * PENALTY_DISTANCE

    if "nevsky" in parsed.preferences and "nevsky" in hotel.tags:
        score += 5.0

    return round(score, 2)


def _passes_filters(hotel: Hotel, filters: SearchFilters, nights: int) -> bool:
    if hotel.stars < filters.min_stars:
        return False
    if filters.max_price_per_night and hotel.price_per_night > filters.max_price_per_night:
        return False
    total = hotel.price_per_night * nights
    if filters.max_total_price and total > filters.max_total_price * 1.1:
        return False
    if hotel.distance_to_center_km > filters.max_distance_km:
        return False
    for tag in filters.required_tags:
        if tag not in hotel.tags:
            return False
    return True


def search_hotels(
    parsed: ParsedQuery,
    filters: SearchFilters | None = None,
    limit: int = 10,
) -> list[SearchHotelResult]:
    filters = filters or parsed.filters
    hotels = load_hotels()
    city = normalize_city(parsed.location)
    nights = trip_nights(parsed)

    filtered: list[Hotel] = []
    for h in hotels:
        if city and h.city.lower() != city.lower():
            continue
        if not _passes_filters(h, filters, nights):
            continue
        filtered.append(h)

    if not filtered and city:
        filtered = [h for h in hotels if h.city.lower() == city.lower()]
    if not filtered:
        filtered = hotels[:]

    scored: list[SearchHotelResult] = []
    for h in filtered:
        total = h.price_per_night * nights
        score = _score_hotel(h, parsed, nights)
        reason = build_ai_reason(h, parsed, nights, total)
        scored.append(
            SearchHotelResult(
                **h.model_dump(),
                match_score=score,
                ai_reason=reason,
                total_price=total,
            )
        )

    if filters.sort_by == "price":
        scored.sort(key=lambda x: x.price_per_night)
    elif filters.sort_by == "rating":
        scored.sort(key=lambda x: x.rating, reverse=True)
    else:
        scored.sort(key=lambda x: x.match_score, reverse=True)

    return scored[:limit]
