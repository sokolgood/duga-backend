import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.v1.api import api_router
from src.api.v1.errors import exception_handlers
from src.core.config import get_settings

# Настройка логгирования
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    logger.info("Starting FastAPI app...")
    yield
    logger.info("Shutting down FastAPI app...")

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_version}/openapi.json",
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

# Монтируем статические файлы для загруженных фотографий
static_dir = Path("data/locations")
if not static_dir.exists():
    static_dir.mkdir(parents=True)
app.mount("/static/locations", StaticFiles(directory=static_dir), name="static")

app.mount("/static", StaticFiles(directory=Path("src/static")), name="static_assets")

app.include_router(api_router, prefix=settings.api_version)

@app.get("/")
async def root() -> dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "duga backend"}

@app.get("/health")
def health() -> Response:
    logger.info("Health check endpoint accessed")
    return Response(status_code=status.HTTP_200_OK)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response