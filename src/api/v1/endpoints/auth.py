from fastapi import APIRouter, Depends, status

from src.api.deps import get_auth_service
from src.schemas.auth import PhoneNumberRequest, TokenResponse, VerificationRequest
from src.services.auth import AuthService

router = APIRouter()


@router.post("/request-code", status_code=status.HTTP_200_OK)
async def request_verification_code(
    phone_data: PhoneNumberRequest, auth_service: AuthService = Depends(get_auth_service)
) -> dict[str, str]:
    await auth_service.send_verification_code(phone_data.phone_number)
    return {"message": "Код верификации отправлен"}


@router.post("/verify", response_model=TokenResponse)
async def verify_code(
    verification_data: VerificationRequest, auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    token = await auth_service.verify_code(verification_data.phone_number, verification_data.code)
    return TokenResponse(access_token=token)
