from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


ProductType = Literal["hotel", "tour", "both"]


class SearchFilters(BaseModel):
    """Фильтры, которые AI выставляет автоматически из запроса."""

    product_type: ProductType = "both"
    min_stars: int = 0
    max_price_per_night: int | None = None
    max_total_price: int | None = None
    max_distance_km: float = 15.0
    required_tags: list[str] = Field(default_factory=list)
    sort_by: Literal["relevance", "price", "rating"] = "relevance"


class ParsedQuery(BaseModel):
    location: str | None = None
    country: str | None = None
    check_in: date | None = None
    check_out: date | None = None
    dates_approximate: bool = False
    budget_max: int | None = None
    budget_min: int | None = None
    nights: int | None = None
    preferences: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    raw_query: str = ""
    filters: SearchFilters = Field(default_factory=SearchFilters)


class Hotel(BaseModel):
    id: str
    name: str
    city: str
    stars: int
    price_per_night: int
    rating: float
    photo_url: str
    description: str
    amenities: list[str]
    distance_to_center_km: float
    tags: list[str]


class Tour(BaseModel):
    id: str
    name: str
    city: str
    duration_days: int
    price_total: int
    rating: float
    photo_url: str
    description: str
    includes: list[str]
    tags: list[str]


class SearchHotelResult(Hotel):
    match_score: float
    ai_reason: str
    total_price: int | None = None


class SearchTourResult(Tour):
    match_score: float
    ai_reason: str


class SearchRequest(BaseModel):
    query: str
    init_data: str | None = None
    use_web: bool | None = None


class SearchResponse(BaseModel):
    session_id: str
    parsed: ParsedQuery
    filters: SearchFilters
    hotels: list[SearchHotelResult]
    tours: list[SearchTourResult] = Field(default_factory=list)
    web_insight: str | None = None


class SessionResponse(BaseModel):
    session_id: str
    query: str
    parsed: ParsedQuery
    filters: SearchFilters
    hotels: list[SearchHotelResult]
    tours: list[SearchTourResult] = Field(default_factory=list)
    web_insight: str | None = None


class BookRequest(BaseModel):
    init_data: str | None = None
    check_in: date | None = None
    check_out: date | None = None


class BookResponse(BaseModel):
    status: str
    message: str
    booking_url: str | None = None
