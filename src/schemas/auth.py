from pydantic import BaseModel, EmailStr, Field, model_validator

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)

class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=1)

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)
    password_repeat: str = Field(min_length=8, max_length=255)

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "RegisterRequest":
        if self.password != self.password_repeat:
            raise ValueError("Passwords do not match")
        return self