from pydantic import BaseModel, Field

class WatchTextPrompt(BaseModel):
    description: str

    class Config:
        json_schema_extra = {
            "example": {
                "description": "I just bought a blue dial Tissot PRX Powermatic 80 automatic watch."
            }
        }

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

    class Config:
        from_attributes = True