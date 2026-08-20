from __future__ import annotations
from typing import Protocol, Optional, List, Dict
from domain.profile import Profile


class ProfileRepository(Protocol):
    def get_profile(self, user_id: int) -> Optional[Dict]:
        ...

    def update_profile(self, user_id: int, data: dict) -> Optional[Dict]:
        ...

    def add_car(self, user_id: int, car_key: str, plate: str) -> Dict:
        ...

    def delete_car(self, user_id: int, car_id: int) -> bool:
        ...

    def set_default_car(self, user_id: int, car_id: int) -> bool:
        ...

    def get_charging_history(self, user_id: int) -> List[Dict]:
        ...


class FavoritesRepository(Protocol):
    def list_favorites(self, user_id: int) -> List[Dict]:
        ...

    def add_favorite(self, user_id: int, station_key: str) -> Dict:
        ...

    def remove_favorite(self, user_id: int, station_key: str) -> bool:
        ...


class JourneyRepository(Protocol):
    def save_journey(self, user_id: int, data: dict) -> Dict:
        ...

    def list_journeys(self, user_id: int) -> List[Dict]:
        ...

    def get_journey_detail(self, user_id: int, journey_id: int) -> Optional[Dict]:
        ...

