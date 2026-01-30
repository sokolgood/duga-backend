import logging

from fastapi import APIRouter

from src.api.v1.endpoints import auth, location, swipe, user, web

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_fastapi_app")

api_router = APIRouter()

@api_router.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@api_router.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")

api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(location.router)
api_router.include_router(web.router)
api_router.include_router(swipe.router)