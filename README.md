# 🌀 duga backend

Backend API for a route discovery and planning service based on user interests and preferences.

## Features

- **User Authentication:** Phone-based authentication with verification codes
- **Location Management:** CRUD operations for locations with photos, categories, and tags
- **Swipe Interface:** Tinder-like swipe cards for location discovery and interaction tracking
- **Route Generation:** Intelligent route planning based on user preferences and geographic proximity
- **User Preferences:** Customizable interests and preferences for personalized recommendations

## Tech Stack

- **Framework:** FastAPI (async REST API)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Migrations:** Alembic
- **Authentication:** JWT tokens (python-jose, bcrypt)
- **File Storage:** Yandex Cloud S3 (with local fallback)
- **Caching:** Redis (optional)
- **Validation:** Pydantic v2
- **Package Manager:** Poetry

## Requirements

- Python 3.11.9 - 3.11.13
- PostgreSQL 14+
- Redis (optional, for caching)
- Poetry

## Quick Start

### Installation

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Configuration

Create environment files in the `env/` directory:

- `env/.env.local` - for local development
- `env/.env.test` - for test
- `env/.env.prod` - for production

Example configuration:

```env
# Database
DB_HOST=localhost
DB_NAME=duga
DB_USER=postgres
DB_PASS=postgres
DB_PORT=5432

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=30

# S3 (Yandex Cloud)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ru-central1
AWS_BUCKET_NAME=duga-bucket

# File Storage
FILE_STORAGE_PATH=./data/locations

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASS=
```

### Database Setup

```bash
# Run migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "description"
```

### Running the Application

```bash
# Development mode
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8080

# Or using the run script
./run.sh
```

The API will be available at `http://localhost:8080`

### Health Check

```bash
curl http://localhost:8080/health
```

## API Documentation

Once the application is running, interactive API documentation is available at:

- **Swagger UI:** `http://localhost:8080/api/v1/docs`
- **ReDoc:** `http://localhost:8080/api/v1/redoc`
- **OpenAPI JSON:** `http://localhost:8080/api/v1/openapi.json`

### Main Endpoints

#### Authentication
- `POST /api/v1/auth/request-code` - Request verification code
- `POST /api/v1/auth/verify` - Verify code and get JWT token

#### Users
- `GET /api/v1/users/me` - Get current user info
- `PATCH /api/v1/users/me` - Update user profile

#### Locations
- `GET /api/v1/locations` - List locations (with pagination and filtering)
- `POST /api/v1/locations` - Create location
- `GET /api/v1/locations/{id}` - Get location details
- `PATCH /api/v1/locations/{id}` - Update location
- `DELETE /api/v1/locations/{id}` - Delete location
- `POST /api/v1/locations/{id}/photos` - Upload photos

#### Swipe
- `GET /api/v1/swipe/candidates` - Get location candidates for swiping
- `POST /api/v1/swipe/action` - Record swipe action (like/dislike)
- `GET /api/v1/swipe/history` - Get swipe history

## Project Structure

```
duga/
├── alembic.ini              # Alembic configuration
├── docker/                  # Docker configuration
│   ├── docker-compose.yaml
│   └── Dockerfile
├── migrations/              # Database migrations
│   ├── env.py
│   └── versions/
├── scripts/                 # Utility scripts
├── src/
│   ├── api/                # API layer
│   │   ├── deps.py        # Dependency injection
│   │   └── v1/
│   │       ├── api.py     # Main router
│   │       ├── errors.py  # Error handlers
│   │       └── endpoints/ # API endpoints
│   │           ├── auth.py
│   │           ├── location.py
│   │           ├── swipe.py
│   │           ├── user.py
│   │           └── web.py
│   ├── core/              # Core application
│   │   ├── config.py      # Settings
│   │   ├── database.py    # Database connection
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── types.py       # Type definitions
│   ├── models/            # SQLAlchemy models
│   │   ├── base.py
│   │   ├── location.py
│   │   ├── route.py
│   │   ├── swipe.py
│   │   └── user.py
│   ├── repositories/      # Database layer
│   │   ├── location.py
│   │   ├── swipe.py
│   │   └── user.py
│   ├── schemas/           # Pydantic schemas
│   │   ├── auth.py
│   │   ├── location.py
│   │   ├── swipe.py
│   │   └── user.py
│   ├── services/          # Business logic
│   │   ├── auth.py
│   │   ├── file_storage.py
│   │   ├── location.py
│   │   ├── s3.py
│   │   ├── swipe.py
│   │   └── user.py
│   ├── static/            # Static files
│   ├── templates/         # HTML templates
│   └── main.py           # FastAPI application
├── pyproject.toml         # Poetry configuration
├── requirements.txt       # Dependencies (legacy)
└── README.md
```

## Development

### Architecture

The project follows a layered architecture with clear separation of concerns:

1. **API Layer** (`api/v1/endpoints/`)
   - FastAPI routers
   - Request/response validation via Pydantic schemas
   - Connected in `api/v1/api.py`

2. **Services** (`services/`)
   - Business logic
   - Work with database models (not API schemas)
   - Raise exceptions from `core/exceptions.py`
   - No router or HTTP exception logic

3. **Repositories** (`repositories/`)
   - Database access layer
   - Abstraction over SQLAlchemy
   - All DB operations go through repositories

4. **Models** (`models/`)
   - SQLAlchemy ORM models
   - Define database schema

5. **Schemas** (`schemas/`)
   - Pydantic models for API validation
   - Request/Response DTOs

### Code Style

- Use Python 3.11+ modern type hints:
  - ✅ `str | None` (not `Optional[str]`)
  - ✅ `list[int]` (not `List[int]`)
  - ✅ `dict[str, Any]` (not `Dict[str, Any]`)
- Follow SOLID principles
- Use common naming conventions
- No unnecessary docstrings
- Max line length: 120 characters
- Use `ruff` for linting and formatting

### Error Handling

- Business logic in services raises exceptions from `core/exceptions.py`
- Routers handle exceptions via handlers in `api/v1/errors.py`

### Dependency Injection

- Use FastAPI's `Depends()` for dependency injection
- All dependencies are defined in `api/deps.py`

### Database

- All database operations go through repositories
- Use async SQLAlchemy sessions
- Create migrations with Alembic

### Adding Dependencies

```bash
# Add a dependency
poetry add package-name

# Add a dev dependency
poetry add --group dev package-name
```

### Linting and Formatting

```bash
# Check code
poetry run ruff check .

# Auto-fix issues
poetry run ruff check --fix .

# Format code
poetry run ruff format .
```

### Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=src
```

## Docker

```bash
# Run with Docker Compose
docker-compose -f docker/docker-compose.yaml up
```

## License
-

## Authors

- Fedor Sokolov <itsfedorsokolov.gmail.com>
