from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Car:
    id: int
    car_key: str
    plate: Optional[str]
    is_default: bool
    added_at: Optional[str]


@dataclass
class Profile:
    id: int
    name: Optional[str]
    surname: Optional[str]
    email: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    cars: List[Car]


def profile_to_dict(p: Profile) -> dict:
    return {
        "id": str(p.id),
        "name": p.name,
        "surname": p.surname,
        "email": p.email,
        "address": p.address,
        "phone": p.phone,
        "cars": [
            {
                "id": str(c.id),
                "car_key": c.car_key,
                "plate": c.plate,
                "is_default": c.is_default,
                "added_at": str(c.added_at) if c.added_at else None,
            }
            for c in p.cars
        ],
    }
