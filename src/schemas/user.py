from pydantic import BaseModel, EmailStr, Field, model_validator

class UserFilter(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=10, le=100, default=50)

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None

    @model_validator(mode="after")
    def validate_any_field_present(self) -> "UserUpdate":
        if self.name is None and self.email is None:
            raise ValueError("At least one field must be provided")
        return self

class Role(BaseModel):
    id: int
    name: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    is_active: bool