import re
from datetime import date, timedelta

from src.api.schemas import ParsedQuery
from src.geo.cities import detect_city_in_text

PREFERENCE_PATTERNS: list[tuple[str, str]] = [
    (r"мор[ея]|у моря|набереж|пляж", "sea"),
    (r"бассейн", "pool"),
    (r"метро", "metro"),
    (r"семь|семей|дет", "family"),
    (r"центр", "center"),
    (r"невск", "nevsky"),
    (r"spa|спа", "spa"),
    (r"гор", "mountain"),
    (r"экскурс", "excursion"),
]

MONTH_PATTERNS: list[tuple[str, int]] = [
    (r"январ", 1),
    (r"феврал", 2),
    (r"март", 3),
    (r"апрел", 4),
    (r"ма[йя]", 5),
    (r"июн", 6),
    (r"июл", 7),
    (r"август", 8),
    (r"сентябр", 9),
    (r"октябр", 10),
    (r"ноябр", 11),
    (r"декабр", 12),
]


def _next_weekend(ref: date) -> tuple[date, date]:
    days_until_sat = (5 - ref.weekday()) % 7
    if days_until_sat == 0 and ref.weekday() == 5:
        sat = ref
    elif days_until_sat == 0:
        sat = ref + timedelta(days=7)
    else:
        sat = ref + timedelta(days=days_until_sat)
    sun = sat + timedelta(days=1)
    return sat, sun


def _dates_from_month(text: str, ref: date) -> tuple[date | None, date | None, int | None]:
    for pattern, month_num in MONTH_PATTERNS:
        if re.search(pattern, text):
            year = ref.year
            if month_num < ref.month:
                year += 1
            check_in = date(year, month_num, 10)
            check_out = check_in + timedelta(days=2)
            return check_in, check_out, 2
    return None, None, None


def parse_fallback(query: str, reference_date: date | None = None) -> ParsedQuery:
    ref = reference_date or date.today()
    text = query.lower().strip()
    missing: list[str] = []
    preferences: list[str] = []

    location = detect_city_in_text(text)
    if not location:
        missing.append("location")

    check_in: date | None = None
    check_out: date | None = None
    nights: int | None = None
    dates_approximate = False

    if re.search(r"выходн|эти выходные|на выходные", text):
        check_in, check_out = _next_weekend(ref)
        nights = 2
        dates_approximate = True
    elif m := re.search(r"(\d+)\s*дн", text):
        nights = int(m.group(1))
        check_in = ref + timedelta(days=7)
        check_out = check_in + timedelta(days=nights)
        dates_approximate = True
    else:
        check_in, check_out, nights = _dates_from_month(text, ref)
        if check_in:
            dates_approximate = True

    budget_max: int | None = None
    if m := re.search(r"до\s*(\d+)\s*(?:тыс|т\.?р|k)?", text):
        val = int(m.group(1))
        if "тыс" in m.group(0) or val < 500:
            val *= 1000
        budget_max = val
    elif m := re.search(r"(\d+)\s*тысяч", text):
        budget_max = int(m.group(1)) * 1000

    for pattern, tag in PREFERENCE_PATTERNS:
        if re.search(pattern, text):
            if tag not in preferences:
                preferences.append(tag)

    if not check_in and not check_out:
        missing.append("dates")

    confidence = 0.55 if location else 0.35
    if check_in:
        confidence += 0.15
    if budget_max:
        confidence += 0.1

    return ParsedQuery(
        location=location,
        country="Россия" if location else None,
        check_in=check_in,
        check_out=check_out,
        dates_approximate=dates_approximate,
        budget_max=budget_max,
        budget_min=None,
        nights=nights,
        preferences=preferences,
        missing_fields=list(dict.fromkeys(missing)),
        confidence=min(confidence, 0.85),
        raw_query=query,
    )
