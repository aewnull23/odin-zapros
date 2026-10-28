from src.api.schemas import ParsedQuery


def needs_clarification(parsed: ParsedQuery) -> bool:
    critical = {"location", "dates"}
    return bool(critical.intersection(set(parsed.missing_fields)))
