from enum import Enum
from typing import Any

from pydantic import BaseModel


class IndicatorType(Enum):
    IP = "ip"
    HASH = "hash"
    DOMAIN = "domain"
    URL = "url"


class Indicator(BaseModel):
    type: IndicatorType
    value: str


# for the API request only
class ThreatIndicatorsBody(BaseModel):
    indicators: list[Indicator]
    metadata: dict[str, Any] | None
