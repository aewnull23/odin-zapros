from src.api.schemas import ParsedQuery, Hotel

PREF_LABELS: dict[str, str] = {
    "sea": "у моря",
    "pool": "с бассейном",
    "metro": "рядом с метро",
    "family": "для семьи",
    "center": "в центре",
    "nevsky": "рядом с Невским",
    "spa": "со SPA",
}


def build_ai_reason(hotel: Hotel, parsed: ParsedQuery, nights: int, total_price: int) -> str:
    parts: list[str] = []
    matched = [PREF_LABELS.get(p, p) for p in parsed.preferences if p in hotel.tags]
    if matched:
        parts.append("Подходит по вашим пожеланиям: " + ", ".join(matched[:3]))
    if parsed.budget_max and total_price <= parsed.budget_max:
        parts.append(f"укладывается в бюджет ({total_price:,} ₽ за {nights} н.".replace(",", " "))
    elif parsed.budget_max:
        parts.append(f"близко к вашему бюджету ({total_price:,} ₽)".replace(",", " "))
    if hotel.rating >= 4.5:
        parts.append(f"высокий рейтинг {hotel.rating}")
    if hotel.distance_to_center_km <= 1.0 and ("center" in parsed.preferences or "nevsky" in parsed.preferences):
        parts.append("удобное расположение в центре")
    if not parts:
        parts.append(f"хороший баланс цены ({hotel.price_per_night:,} ₽/ночь) и рейтинга".replace(",", " "))
    return parts[0].capitalize() + (". " + ". ".join(p.capitalize() for p in parts[1:]) if len(parts) > 1 else ".")
