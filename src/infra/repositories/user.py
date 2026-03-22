import bcrypt

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.exceptions import ValidationException
from src.domain.entities.role import RoleEntity
from src.domain.entities.user import UserEntity
from src.domain.repositories.user import UserRepository
from src.infra.models import Role, User
from src.schemas.user import UserCreate, UserFilter, UserUpdate

class SqlUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: User) -> UserEntity:
        return UserEntity(
            id=model.id,
            name=model.name,
            email=model.email,
            password_hash=model.password_hash,
            role=RoleEntity(
                id=model.role_id,
                name=model.role.name
            ),
            is_active=not model.is_deleted,
        )

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    async def create(self, schema: UserCreate) -> UserEntity:
        default_role_id = await self._session.scalar(
            select(Role.id).where(Role.name == "user")
        )
        
        if default_role_id is None:
            raise ValidationException("Default user role is not configured")

        password_hash = self._hash_password(schema.password)
        model = User(
            name=schema.name,
            email=schema.email,
            password_hash=password_hash,
            role_id=default_role_id,
        )
        self._session.add(model)
        await self._session.flush()

        await self._session.refresh(model, ["role"])

        return self._to_entity(model)

    async def get_by_id(self, id: int) -> UserEntity | None:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_page(self, filters: UserFilter) -> list[UserEntity]:
        query = (
            select(User)
            .options(selectinload(User.role))
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, id: int, schema: UserUpdate):
        values = schema.model_dump(exclude_none=True)

        if not values:
            return

        await self._session.execute(
            update(User)
            .where(User.id == id)
            .values(**values)
        )

    async def delete(self, id: int):
        await self._session.execute(
            delete(User)
            .where(User.id == id)
        )

    async def soft_delete(self, id: int):
        await self._session.execute(
            update(User)
            .where(User.id == id)
            .values(is_deleted=True)
        )
