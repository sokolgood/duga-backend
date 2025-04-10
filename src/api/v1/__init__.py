from fastapi import APIRouter

from .endpoints.locations import router as locations_router

router = APIRouter(prefix="/v1")
router.include_router(locations_router)
