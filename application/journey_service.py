from typing import List, Optional
from domain.repositories import JourneyRepository


class JourneyService:
    def __init__(self, repo: JourneyRepository):
        self.repo = repo

    def save_journey(self, user_id: int, data: dict) -> dict:
        return self.repo.save_journey(user_id, data)

    def list_journeys(self, user_id: int) -> List[dict]:
        return self.repo.list_journeys(user_id)

    def get_journey_detail(self, user_id: int, journey_id: int) -> Optional[dict]:
        return self.repo.get_journey_detail(user_id, journey_id)
