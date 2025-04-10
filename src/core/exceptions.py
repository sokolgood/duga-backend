class UserAlreadyExistsError(Exception):
    pass


class InvalidVerificationCodeError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class LocationNotFoundError(Exception):
    pass


class InvalidLocationDataError(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)
