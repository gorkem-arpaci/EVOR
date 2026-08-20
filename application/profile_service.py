from typing import Optional
from domain.repositories import ProfileRepository


class ProfileService:
    def __init__(self, repo: ProfileRepository):
        self.repo = repo

    def get_profile(self, user_id: int) -> Optional[dict]:
        return self.repo.get_profile(user_id)

    def update_profile(self, user_id: int, data: dict) -> Optional[dict]:
        return self.repo.update_profile(user_id, data)

    def add_car(self, user_id: int, car_key: str, plate: str) -> dict:
        return self.repo.add_car(user_id, car_key, plate)

    def delete_car(self, user_id: int, car_id: int) -> bool:
        return self.repo.delete_car(user_id, car_id)

    def set_default_car(self, user_id: int, car_id: int) -> bool:
        return self.repo.set_default_car(user_id, car_id)

    def get_charging_history(self, user_id: int) -> list:
        return self.repo.get_charging_history(user_id)
