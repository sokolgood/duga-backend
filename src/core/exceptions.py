from fastapi import HTTPException, status


class UserAlreadyExistsError(Exception):
    pass


class InvalidVerificationCodeError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class LocationNotFoundError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )


class InvalidLocationDataError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class PhotoNotFoundError(HTTPException):
    def __init__(self, detail: str = "Photo not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )
