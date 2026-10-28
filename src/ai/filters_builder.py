import re

from src.api.schemas import ParsedQuery, SearchFilters


def build_filters(parsed: ParsedQuery, query: str, nights: int) -> SearchFilters:
    text = query.lower()
    has_tour = bool(re.search(r"\bтур", text))
    has_hotel = bool(
        re.search(r"\bотел", text)
        or re.search(r"ноч|прожив|u моря|у моря|номер", text)
    )
    if has_tour and has_hotel:
        product_type = "both"
    elif has_tour:
        product_type = "tour"
    elif has_hotel:
        product_type = "hotel"
    else:
        product_type = "both"

    min_stars = 0
    if re.search(r"5\s*зв|пятиз|люкс|premium|премиум", text):
        min_stars = 5
    elif re.search(r"4\s*зв|четырех", text):
        min_stars = 4
    elif re.search(r"3\s*зв|три\s*зв", text):
        min_stars = 3
    elif "бюджет" in text or "недорог" in text or "эконом" in text:
        min_stars = 0
    elif parsed.budget_max and nights and parsed.budget_max // max(nights, 1) < 4000:
        min_stars = 2

    max_ppn: int | None = None
    if parsed.budget_max and nights:
        max_ppn = max(parsed.budget_max // nights, 1500)

    max_dist = 15.0
    if "центр" in text or "невск" in text:
        max_dist = 2.0
    elif "метро" in text:
        max_dist = 3.5
    elif "мор" in text or "пляж" in text:
        max_dist = 8.0

    sort_by = "relevance"
    if "дешев" in text or "бюджет" in text:
        sort_by = "price"
    elif "лучш" in text or "рейтинг" in text or "топ" in text:
        sort_by = "rating"

    return SearchFilters(
        product_type=product_type,  # type: ignore[arg-type]
        min_stars=min_stars,
        max_price_per_night=max_ppn,
        max_total_price=parsed.budget_max,
        max_distance_km=max_dist,
        required_tags=list(parsed.preferences),
        sort_by=sort_by,  # type: ignore[arg-type]
    )


def merge_filters(base: SearchFilters, override: dict) -> SearchFilters:
    data = base.model_dump()
    for key, val in override.items():
        if val is not None and key in data:
            data[key] = val
    return SearchFilters.model_validate(data)
