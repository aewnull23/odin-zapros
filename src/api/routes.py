from fastapi import APIRouter, HTTPException

from src.ai.intent import analyze_travel_query
from src.api.schemas import (
    BookRequest,
    BookResponse,
    Hotel,
    SearchRequest,
    SearchResponse,
    SessionResponse,
)
from src.api.telegram_auth import validate_init_data
from src.config import get_settings
from src.search.engine import load_hotels, search_hotels
from src.search.tours import search_tours
from src.store.sessions import create_session, get_session
from src.util.query_helpers import needs_clarification

router = APIRouter(prefix="/api")


def _optional_validate(init_data: str | None) -> None:
    if init_data:
        validate_init_data(init_data)


async def _run_search(
    query: str,
    user_id: int | None = None,
    use_web: bool | None = None,
) -> SearchResponse:
    settings = get_settings()
    web = settings.enable_web_search if use_web is None else use_web

    parsed, filters, web_insight = await analyze_travel_query(query, use_web=web)
    if needs_clarification(parsed):
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Нужно уточнить детали запроса",
                "parsed": parsed.model_dump(mode="json"),
                "missing_fields": parsed.missing_fields,
            },
        )

    hotels: list = []
    tours: list = []
    if filters.product_type in ("hotel", "both"):
        hotels = search_hotels(parsed, filters)
    if filters.product_type in ("tour", "both"):
        tours = search_tours(parsed, filters)

    session = create_session(
        query,
        parsed,
        filters,
        hotels,
        tours,
        user_id=user_id,
        web_insight=web_insight,
    )
    return SearchResponse(
        session_id=session.id,
        parsed=parsed,
        filters=filters,
        hotels=hotels,
        tours=tours,
        web_insight=web_insight,
    )


@router.post("/search", response_model=SearchResponse)
async def api_search(body: SearchRequest):
    _optional_validate(body.init_data)
    return await _run_search(body.query.strip(), use_web=body.use_web)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def api_get_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return SessionResponse(
        session_id=session.id,
        query=session.query,
        parsed=session.parsed,
        filters=session.filters,
        hotels=session.hotels,
        tours=session.tours,
        web_insight=session.web_insight,
    )


@router.get("/hotels/{hotel_id}", response_model=Hotel)
async def api_get_hotel(hotel_id: str):
    for h in load_hotels():
        if h.id == hotel_id:
            return h
    raise HTTPException(status_code=404, detail="Hotel not found")


@router.post("/book/{hotel_id}", response_model=BookResponse)
async def api_book(hotel_id: str, body: BookRequest):
    _optional_validate(body.init_data)
    hotel = None
    for h in load_hotels():
        if h.id == hotel_id:
            hotel = h
            break
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    city_slug = hotel.city.replace(" ", "+")
    url = f"https://ostrovok.ru/hotel/{city_slug}/?q={hotel.name.replace(' ', '+')}"
    return BookResponse(
        status="ok",
        message="Успешно забронировано! (демо)",
        booking_url=url,
    )


@router.get("/config/webapp")
async def webapp_config():
    settings = get_settings()
    return {"webapp_url": settings.webapp_url}
