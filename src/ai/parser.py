import json
import logging
from datetime import date

from openai import AsyncOpenAI

from src.ai.fallback import parse_fallback
from src.ai.prompts import RETRY_USER, SYSTEM_PROMPT
from src.api.schemas import ParsedQuery, SearchFilters
from src.config import get_settings

logger = logging.getLogger(__name__)


def _normalize_parsed(data: dict, raw_query: str) -> ParsedQuery:
    check_in = data.get("check_in")
    check_out = data.get("check_out")
    filters_raw = data.get("filters") or {}
    filters = SearchFilters.model_validate(filters_raw) if filters_raw else SearchFilters()

    parsed = ParsedQuery(
        location=data.get("location"),
        country=data.get("country"),
        check_in=date.fromisoformat(check_in) if check_in else None,
        check_out=date.fromisoformat(check_out) if check_out else None,
        dates_approximate=bool(data.get("dates_approximate", False)),
        budget_max=data.get("budget_max"),
        budget_min=data.get("budget_min"),
        nights=data.get("nights"),
        preferences=list(data.get("preferences") or []),
        missing_fields=list(data.get("missing_fields") or []),
        confidence=float(data.get("confidence") or 0.5),
        raw_query=raw_query,
        filters=filters,
    )
    if not parsed.location and "location" not in parsed.missing_fields:
        parsed.missing_fields.append("location")
    if not parsed.check_in and not parsed.check_out and "dates" not in parsed.missing_fields:
        parsed.missing_fields.append("dates")
    return parsed


async def parse_query(
    query: str,
    reference_date: date | None = None,
    web_context: str | None = None,
) -> ParsedQuery:
    ref = reference_date or date.today()
    settings = get_settings()
    if not settings.openai_api_key:
        logger.info("OpenAI key missing, using fallback parser")
        return parse_fallback(query, ref)

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    user_content = f"reference_date: {ref.isoformat()}\nquery: {query}"
    if web_context:
        user_content += f"\nweb_context: {web_context}"

    for attempt in range(2):
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content if attempt == 0 else RETRY_USER + "\n" + user_content},
                ],
                temperature=0.2,
                timeout=25.0,
            )
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            return _normalize_parsed(data, query)
        except Exception as exc:
            logger.warning("OpenAI parse attempt %s failed: %s", attempt + 1, exc)

    logger.info("Falling back to rule-based parser")
    return parse_fallback(query, ref)
