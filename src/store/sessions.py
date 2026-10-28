import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from src.api.schemas import ParsedQuery, SearchFilters, SearchHotelResult, SearchTourResult

SESSION_TTL = timedelta(hours=1)


@dataclass
class SearchSession:
    id: str
    user_id: int | None
    query: str
    parsed: ParsedQuery
    filters: SearchFilters
    hotels: list[SearchHotelResult]
    tours: list[SearchTourResult]
    web_insight: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) - self.created_at > SESSION_TTL


_sessions: dict[str, SearchSession] = {}


def create_session(
    query: str,
    parsed: ParsedQuery,
    filters: SearchFilters,
    hotels: list[SearchHotelResult],
    tours: list[SearchTourResult],
    user_id: int | None = None,
    web_insight: str | None = None,
) -> SearchSession:
    session_id = str(uuid.uuid4())
    session = SearchSession(
        id=session_id,
        user_id=user_id,
        query=query,
        parsed=parsed,
        filters=filters,
        hotels=hotels,
        tours=tours,
        web_insight=web_insight,
    )
    _sessions[session_id] = session
    _purge_expired()
    return session


def get_session(session_id: str) -> SearchSession | None:
    _purge_expired()
    session = _sessions.get(session_id)
    if session and session.is_expired():
        _sessions.pop(session_id, None)
        return None
    return session


def _purge_expired() -> None:
    expired = [sid for sid, s in _sessions.items() if s.is_expired()]
    for sid in expired:
        _sessions.pop(sid, None)
