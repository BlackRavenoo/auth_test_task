from fastapi import APIRouter, status

from src.api.deps import AccessTokenDep, AuthServiceDep
from src.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RefreshRequest, RefreshResponse, LogoutRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    auth_service: AuthServiceDep,
):
    await auth_service.register(
        name=data.name,
        email=data.email,
        password=data.password,
        password_repeat=data.password_repeat,
    )

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    data: LoginRequest,
    auth_service: AuthServiceDep,
):
    access_token, refresh_token = await auth_service.login(data.email, data.password)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=RefreshResponse, status_code=status.HTTP_200_OK)
async def refresh(
    data: RefreshRequest,
    auth_service: AuthServiceDep,
):
    access_token, refresh_token = await auth_service.refresh(data.refresh_token)
    return RefreshResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    data: LogoutRequest,
    auth_service: AuthServiceDep,
    access_token: AccessTokenDep,
):
    await auth_service.logout(data.refresh_token, access_token)
