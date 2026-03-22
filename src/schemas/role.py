from pydantic import BaseModel

from src.domain.enums import ResourceType

class RoleCreate(BaseModel):
    name: str

class RoleUpdate(BaseModel):
    name: str

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