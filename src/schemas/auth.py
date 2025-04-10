from typing import Annotated

from pydantic import BaseModel, StringConstraints

PhoneNumber = Annotated[str, StringConstraints(pattern=r"^7\d{10}$")]
VerificationCode = Annotated[str, StringConstraints(pattern=r"^\d{4}$")]


class PhoneNumberRequest(BaseModel):
    phone_number: PhoneNumber


class VerificationRequest(PhoneNumberRequest):
    code: VerificationCode


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
