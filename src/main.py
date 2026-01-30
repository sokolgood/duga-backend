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
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


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
    return {"message": "duga backend"}


@app.get("/health")
def health() -> Response:
    return Response(status_code=status.HTTP_200_OK)
