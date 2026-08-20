from dataclasses import dataclass
from typing import Optional


@dataclass
class Favorite:
    id: int
    station_key: str
    added_at: Optional[str]
