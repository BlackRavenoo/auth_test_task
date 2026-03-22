from pydantic import BaseModel, Field

from src.domain.enums import ResourceType

class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=64)

class RoleUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=64)

class RoleResponse(BaseModel):
    id: int
    name: str

class RolePermissionUpdate(BaseModel):
    can_read: bool
    can_write: bool
    can_delete: bool

class RolePermissionResponse(BaseModel):
    resource: ResourceType
    can_read: bool
    can_write: bool
    can_delete: bool