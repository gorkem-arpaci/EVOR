from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    name: Optional[str]
    surname: Optional[str]
    email: str
    phone: Optional[str]
    address: Optional[str]


@dataclass
class EmailVerification:
    id: int
    email: str
    code: str
    expires_at: str
    used: bool
