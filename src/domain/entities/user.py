from dataclasses import dataclass

from src.domain.entities.role import RoleEntity

@dataclass
class UserEntity:
    id: int
    name: str
    email: str
    password_hash: str
    role: RoleEntity
    is_active: bool