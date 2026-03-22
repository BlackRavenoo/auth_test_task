from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import AlreadyExistsException, DomainException, ForbiddenException, UnauthorizedException, NotFoundException, ValidationException

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UnauthorizedException)
    async def unauthorized_handler(request: Request, exc: UnauthorizedException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc) or "Unauthorized"},
        )

    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc) or "Resource not found"},
        )

    @app.exception_handler(AlreadyExistsException)
    async def already_exists_handler(request: Request, exc: AlreadyExistsException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc) or "Resource already exists"},
        )

    @app.exception_handler(ValidationException)
    async def validation_handler(request: Request, exc: ValidationException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc) or "Validation error"},
        )

    @app.exception_handler(ForbiddenException)
    async def forbidden_handler(request: Request, exc: ForbiddenException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc) or "Access denied"},
        )

    @app.exception_handler(DomainException)
    async def domain_handler(request: Request, exc: DomainException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc) or "Internal server error"},
        )
