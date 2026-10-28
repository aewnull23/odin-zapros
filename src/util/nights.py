from src.api.schemas import ParsedQuery


def trip_nights(parsed: ParsedQuery) -> int:
    if parsed.nights:
        return max(parsed.nights, 1)
    if parsed.check_in and parsed.check_out:
        delta = (parsed.check_out - parsed.check_in).days
        return max(delta, 1)
    return 2
