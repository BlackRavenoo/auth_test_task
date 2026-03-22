from abc import ABC, abstractmethod
from datetime import timedelta

class TokenRepository(ABC):
    @abstractmethod
    async def save_refresh_token(self, user_id: int, token: str, expires_in: timedelta):
        pass

    @abstractmethod
    async def get_user_id_by_refresh_token(self, token: str) -> int | None:
        pass

    @abstractmethod
    async def revoke_refresh_token(self, token: str):
        pass

    @abstractmethod
    async def add_to_blacklist(self, jti: str, expires_in: timedelta):
        pass

    @abstractmethod
    async def is_blacklisted(self, jti: str) -> bool:
        pass