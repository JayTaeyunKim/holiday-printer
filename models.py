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
    country: Optional[str]   # "KR", "US", 또는 None(전체)
    year: int
    month: Optional[int] = None   # 1~12 또는 None