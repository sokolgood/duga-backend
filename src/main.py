from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.api import api_router
from src.api.v1.errors import exception_handlers
from src.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    # log about starting a project

    # app.state.redis_client = ...

    # logger.info("FastAPI app started")
    yield

    # Этот код исполняется uvicorn после выключения сервиса
    # logger.info("Shutting down FastAPI app...")


app = FastAPI(
    title=settings.project_name,
    openapi_url="/openapi.json",
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_version)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "duga backend"}


@app.get("/health")
def health() -> Response:
    return Response(status_code=status.HTTP_200_OK)
