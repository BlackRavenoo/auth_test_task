from pydantic import BaseModel, Field

class UserFilter(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=10, le=100, default=50)

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

class Role(BaseModel):
    id: int
    name: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    is_active: bool