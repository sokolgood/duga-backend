from fastapi import APIRouter

from src.api.v1.endpoints import auth, location, user, web

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(location.router)
api_router.include_router(web.router)
