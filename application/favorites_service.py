from typing import List
from domain.repositories import FavoritesRepository


class FavoritesService:
    def __init__(self, repo: FavoritesRepository):
        self.repo = repo

    def list_favorites(self, user_id: int) -> List[dict]:
        return self.repo.list_favorites(user_id)

    def add_favorite(self, user_id: int, station_key: str) -> dict:
        return self.repo.add_favorite(user_id, station_key)

    def remove_favorite(self, user_id: int, station_key: str) -> bool:
        return self.repo.remove_favorite(user_id, station_key)
