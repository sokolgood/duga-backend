from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.core.exceptions import (
    InvalidVerificationCodeError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


async def user_already_exists_handler(
    _: Request,
    exc: UserAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Пользователь с таким номером телефона уже существует"},
    )


async def invalid_verification_code_handler(
    _: Request,
    exc: InvalidVerificationCodeError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Неверный код верификации"},
    )


async def user_not_found_handler(
    _: Request,
    exc: UserNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Пользователь не найден"},
    )


exception_handlers = {
    UserAlreadyExistsError: user_already_exists_handler,
    InvalidVerificationCodeError: invalid_verification_code_handler,
    UserNotFoundError: user_not_found_handler,
}
