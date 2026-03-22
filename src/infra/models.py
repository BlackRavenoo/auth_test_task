from __future__ import annotations

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.domain.enums import ItemRarity, ResourceType

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="restrict"))

    role: Mapped[Role] = relationship(back_populates="users")

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    users: Mapped[list[User]] = relationship(back_populates="role")
    permissions: Mapped[list[RolePermission]] = relationship(back_populates="role")

class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="cascade"), primary_key=True)
    resource: Mapped[ResourceType] = mapped_column(Enum(ResourceType), primary_key=True)
    can_read: Mapped[bool] = mapped_column(Boolean, default=False)
    can_write: Mapped[bool] = mapped_column(Boolean, default=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False)

    role: Mapped[Role] = relationship(back_populates="permissions")

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256))
    type: Mapped[str] = mapped_column(String(32))
    rarity: Mapped[ItemRarity] = mapped_column(Enum(ItemRarity))
    source: Mapped[str] = mapped_column(String(16))
    source_name: Mapped[str] = mapped_column(String(64))