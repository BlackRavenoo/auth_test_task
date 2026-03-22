from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    password_repeat: str