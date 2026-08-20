from typing import Optional

from domain.repositories import ProfileRepository


class AuthService:
    def __init__(self, repo: ProfileRepository):
        # Reuse profile repository for DB ops related to profile/auth
        self.repo = repo

    def register_user(self, user_data: dict) -> dict:
        # For now delegate to repo-level SQL used previously
        # repo should implement register-like behavior via existing SQL
        if hasattr(self.repo, 'register'):
            return self.repo.register(user_data)
        raise NotImplementedError('register not implemented in repository')

    def send_verification(self, email: str) -> dict:
        if hasattr(self.repo, 'create_verification'):
            return self.repo.create_verification(email)
        raise NotImplementedError('create_verification not implemented in repository')

    def verify_email(self, email: str, code: str) -> bool:
        if hasattr(self.repo, 'verify_code'):
            return self.repo.verify_code(email, code)
        raise NotImplementedError('verify_code not implemented in repository')

    def login_user(self, email: str, password: str) -> Optional[dict]:
        if hasattr(self.repo, 'login'):
            return self.repo.login(email, password)
        raise NotImplementedError('login not implemented in repository')
