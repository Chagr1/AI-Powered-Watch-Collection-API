from pydantic import BaseModel, Field, ConfigDict
from typing import List
from typing import Dict



class WatchTextPrompt(BaseModel):
    description: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Find me an automatic Seiko under 1000 dollars around 40mm"
            }
        }
    )

class WatchAutoCreate(BaseModel):
    brand: str
    model_name: str

class AIWatchData(BaseModel):
    is_automatic: bool | None = None
    movement_type: str | None = "Unknown"
    case_size_mm: float | None = None
    crystal_type: str | None = "Unknown"
    water_resistance_m: int | None = None
    strap_type: str | None = "Unknown"
    power_reserve_hours: int | None = None
    ai_confidence: float = Field(ge=0.0, le=1.0)

class WatchUpdate(BaseModel):
    brand: str | None = None
    model_name: str | None = None
    is_automatic: bool | None = None
    movement_type: str | None = None
    case_size_mm: float | None = None
    crystal_type: str | None = None
    water_resistance_m: int | None = None
    strap_type: str | None = None
    power_reserve_hours: int | None = None

class WatchResponse(WatchAutoCreate):
    id: int
    is_automatic: bool | None
    movement_type: str | None
    case_size_mm: float | None
    crystal_type: str | None
    water_resistance_m: int | None
    strap_type: str | None
    power_reserve_hours: int | None
    ai_confidence: float
    needs_verification: bool
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedWatchResponse(BaseModel):
    items: List[WatchResponse]
    page: int
    limit: int
    total: int
    pages: int

class WatchStatistics(BaseModel):
    total_watches: int
    average_price: float
    automatic_count: int
    quartz_count: int
    brand_distribution: Dict[str, int]

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    comment: str | None = Field(None, description="Optional text review")

class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: str | None
    user_id: int
    watch_id: int

    model_config = ConfigDict(from_attributes=True)