from datetime import datetime, timedelta, timezone
import uuid

from jwt import DecodeError, ExpiredSignatureError, decode, encode
import bcrypt

from src.config import settings
from src.domain.entities.user import UserEntity
from src.domain.exceptions import AlreadyExistsException, UnauthorizedException, ValidationException
from src.domain.repositories.user import UserRepository
from src.domain.repositories.token import TokenRepository
from src.schemas.user import UserCreate

class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: TokenRepository) -> None:
        self._user_repo = user_repo
        self._token_repo = token_repo

    async def register(self, name: str, email: str, password: str, password_repeat: str) -> None:
        if password != password_repeat:
            raise ValidationException("Passwords do not match")

        user = await self._user_repo.get_by_email(email)
        if user:
            raise AlreadyExistsException("Email already registered")

        user_data = UserCreate(
            name=name,
            email=email,
            password=password
        )
        await self._user_repo.create(user_data)

    async def login(self, email: str, password: str) -> tuple[str, str]:
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("User was deleted")

        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            raise UnauthorizedException("Invalid email or password")

        access_token = self._create_access_token(user)
        refresh_token = str(uuid.uuid4())

        await self._token_repo.save_refresh_token(
            user_id=user.id,
            token=refresh_token,
            expires_in=timedelta(days=settings.jwt_refresh_token_expire_days)
        )

        return access_token, refresh_token

    def _create_access_token(self, user: UserEntity) -> str:
        jti = str(uuid.uuid4())
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role_id": user.role.id,
            "type": "access",
            "jti": jti,
        }
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        payload.update({"exp": expire})
        return encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        user_id = await self._token_repo.get_user_id_by_refresh_token(refresh_token)
        if not user_id:
            raise UnauthorizedException("Refresh token not found or revoked")

        user = await self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        access_token = self._create_access_token(user)
        new_refresh_token = str(uuid.uuid4())

        await self._token_repo.save_refresh_token(
            user_id=user.id,
            token=new_refresh_token,
            expires_in=timedelta(days=settings.jwt_refresh_token_expire_days)
        )
        await self._token_repo.revoke_refresh_token(refresh_token)

        return access_token, new_refresh_token

    async def logout(self, refresh_token: str, access_token: str) -> None:
        token_metadata = self._extract_access_token_data(access_token)
        if token_metadata:
            jti, expires_at = token_metadata
            expires_in = expires_at - datetime.now(timezone.utc)
            if expires_in.total_seconds() > 0:
                await self._token_repo.add_to_blacklist(jti, expires_in)

        await self._token_repo.revoke_refresh_token(refresh_token)

    def _extract_access_token_data(self, token: str) -> tuple[str, datetime] | None:
        try:
            payload = decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False},
            )
            token_type = payload.get("type")
            jti = payload.get("jti")
            exp_raw = payload.get("exp")
            if token_type != "access" or not isinstance(jti, str):
                return None

            expires_at = datetime.fromtimestamp(int(exp_raw), tz=timezone.utc)
            return jti, expires_at
        except (DecodeError, ExpiredSignatureError, TypeError, ValueError):
            return None

    async def get_current_user(self, token: str) -> UserEntity:
        try:
            payload = decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            if payload.get("type") != "access":
                raise UnauthorizedException("Invalid token")

            user_id = int(payload.get("sub"))
            jti = payload.get("jti")
            if not isinstance(jti, str):
                raise UnauthorizedException("Invalid token")
        except (DecodeError, ExpiredSignatureError, TypeError, ValueError):
            raise UnauthorizedException("Invalid token")

        if await self._token_repo.is_blacklisted(jti):
            raise UnauthorizedException("Token was revoked")

        user = await self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        return user