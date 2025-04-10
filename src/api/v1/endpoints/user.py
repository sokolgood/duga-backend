from fastapi import APIRouter, Depends

from src.api.deps import get_current_user, get_user_service
from src.models import User
from src.schemas.user import UserResponse, UserUpdate
from src.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> User:
    return await user_service.update_user(
        user=current_user,
        email=update_data.email,
        full_name=update_data.full_name,
        preferences=update_data.preferences,
    )
