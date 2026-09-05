from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class WeatherCondition(BaseModel):
    operator: str
    value: Union[int, float, str]


class SOP(BaseModel):
    id: str
    category: str
    severity: str
    priority: int = 0

    description: str

    intent_keywords: List[str] = Field(default_factory=list)

    weather_conditions: Dict[str, WeatherCondition] = Field(
        default_factory=dict
    )

    user_conditions: Dict[str, Any] = Field(
        default_factory=dict
    )

    guidance: str

    escalation: Optional[str] = None


class UserContext(BaseModel):
    activity: Optional[str] = None
    location: Optional[str] = None
    time_reference: Optional[str] = "now"

    vulnerable_group: Optional[str] = None

    raw_message: str


class WeatherData(BaseModel):
    temperature_2m: Optional[float] = None
    wind_speed_10m: Optional[float] = None
    precipitation: Optional[float] = None
    precipitation_probability: Optional[float] = None
    uv_index: Optional[float] = None
    weather_code: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str
    protocol_id: Optional[str] = None
    severity: Optional[str] = None