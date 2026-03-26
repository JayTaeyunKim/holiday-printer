from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Holiday:
    country: str
    day: date
    name: str
    note: str = ""


@dataclass
class Query:
    target: Optional[str]   # "KR", "US", "USM", "USB", "USS", 또는 None
    year: int
    month: Optional[int] = None