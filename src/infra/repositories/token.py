import hashlib
import redis.asyncio as aioredis
from datetime import timedelta

from src.domain.repositories.token import TokenRepository

class RedisTokenRepository(TokenRepository):
    def __init__(self, redis: aioredis.Redis):
        self._redis = redis

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def save_refresh_token(self, user_id: int, token: str, expires_in: timedelta):
        token_hash = self._hash_token(token)
        key = f"refresh:{token_hash}"
        seconds = int(expires_in.total_seconds())
        await self._redis.setex(key, seconds, str(user_id))

    async def get_user_id_by_refresh_token(self, token: str) -> int | None:
        token_hash = self._hash_token(token)
        key = f"refresh:{token_hash}"
        result = await self._redis.get(key)
        return int(result) if result else None

    async def revoke_refresh_token(self, token: str):
        token_hash = self._hash_token(token)
        key = f"refresh:{token_hash}"
        await self._redis.delete(key)

    async def add_to_blacklist(self, jti: str, expires_in: timedelta):
        key = f"blacklist:{jti}"
        seconds = max(int(expires_in.total_seconds()), 1)
        await self._redis.setex(key, seconds, "1")

    async def is_blacklisted(self, jti: str) -> bool:
        key = f"blacklist:{jti}"
        return await self._redis.exists(key) == 1