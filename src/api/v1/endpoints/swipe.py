from fastapi import APIRouter, Depends, Query, status

from src.api.deps import get_current_user, get_swipe_service
from src.core.types import SwipeAction
from src.models.user import User
from src.schemas.swipe import (
    LocationCandidate,
    SwipeActionRequest,
    SwipeHistoryItem,
)
from src.services.swipe import SwipeService

router = APIRouter(prefix="/swipe", tags=["swipe"])


@router.get("/candidates", response_model=list[LocationCandidate])
async def get_candidates(
    interests: str | None = Query(None, description="Comma-separated list of interests"),
    start_lat: float | None = Query(None, ge=-90, le=90),
    start_lng: float | None = Query(None, ge=-180, le=180),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    swipe_service: SwipeService = Depends(get_swipe_service),
) -> list[LocationCandidate]:
    coordinates = None
    if start_lat is not None and start_lng is not None:
        coordinates = (start_lat, start_lng)

    interests_list = interests.split(",") if interests else None

    locations_with_distance = await swipe_service.get_candidates(
        user_id=current_user.id, interests=interests_list, coordinates=coordinates, limit=limit
    )

    return [
        LocationCandidate.model_validate(
            {**location.__dict__, "distance_km": round(distance, 1) if distance is not None else None}
        )
        for location, distance in locations_with_distance
    ]


@router.post("/action", status_code=status.HTTP_204_NO_CONTENT)
async def create_swipe_action(
    action_request: SwipeActionRequest,
    current_user: User = Depends(get_current_user),
    swipe_service: SwipeService = Depends(get_swipe_service),
) -> None:
    await swipe_service.create_swipe(
        user_id=current_user.id, location_id=action_request.location_id, action=action_request.action
    )


@router.get("/history", response_model=list[SwipeHistoryItem])
async def get_swipe_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    filter: SwipeAction | None = Query(None),
    current_user: User = Depends(get_current_user),
    swipe_service: SwipeService = Depends(get_swipe_service),
) -> list[SwipeHistoryItem]:
    swipes = await swipe_service.get_history(user_id=current_user.id, limit=limit, offset=offset, action_filter=filter)
    return [SwipeHistoryItem.model_validate(swipe) for swipe in swipes]
