# AI Coding Agent Guidelines

This document provides essential information for AI coding agents working on this project.

## Project Structure

The project follows a layered architecture with clear separation of concerns:

```
src/
├── api/              # API layer (routers, dependencies, error handlers)
├── core/             # Core (config, database, exceptions, types)
├── models/           # SQLAlchemy ORM models
├── repositories/     # Database access layer
├── schemas/          # Pydantic schemas for API validation
└── services/         # Business logic layer
```

## Layer Responsibilities

### API Layer (`api/v1/endpoints/`)
- FastAPI routers only
- Use Pydantic schemas from `schemas/` for request/response validation
- Inject services via `Depends()` from `api/deps.py`
- Register routers in `api/v1/api.py`
- Handle HTTP requests/responses only
- NO business logic

### Services (`services/`)
- Business logic goes here
- Work with database models (from `models/`), NOT API schemas
- Raise exceptions from `core/exceptions.py`
- NO router logic, NO HTTP exceptions
- Can depend on repositories and other services

### Repositories (`repositories/`)
- Database access only
- All DB operations go through repositories
- Use async SQLAlchemy sessions
- Return models or None

### Models (`models/`)
- SQLAlchemy ORM models
- Define database schema
- Use relationships for associations

### Schemas (`schemas/`)
- Pydantic models for API validation
- Request/Response DTOs
- Used only in API layer

## Code Style

### Type Hints
- Use Python 3.11+ modern syntax:
  - ✅ `str | None` (NOT `Optional[str]`)
  - ✅ `list[int]` (NOT `List[int]`)
  - ✅ `dict[str, Any]` (NOT `Dict[str, Any]`)
- Always type function parameters and return values

### Error Handling
- Business logic exceptions: `core/exceptions.py`
- HTTP exception handlers: `api/v1/errors.py`
- Services raise exceptions, routers handle them via handlers

### Dependency Injection
- All dependencies in `api/deps.py`
- Use `Depends()` from FastAPI
- Services receive dependencies via constructor

### Naming
- Follow Python conventions
- No unnecessary docstrings
- Max line length: 120 characters

## Running Tools

### Linting
```bash
make lint
# or
poetry run ruff check .
poetry run ruff check --fix .  # auto-fix
```

### Formatting
```bash
poetry run ruff format .
```

### Testing
```bash
make test
# or
poetry run pytest
```

### Database Migrations
```bash
# Create migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head
```

## Key Rules

1. **Never mix layers**: Services don't use API schemas, routers don't contain business logic
2. **Always use type hints**: Modern Python 3.11+ syntax
3. **Dependency injection**: All deps in `api/deps.py`
4. **Error handling**: Services raise, routers handle
5. **Database access**: Always through repositories
6. **Async everywhere**: Use `async/await` for all I/O operations

## Example: Adding a New Endpoint

1. Create Pydantic schemas in `schemas/`
2. Add business logic in `services/` (using models)
3. Create router in `api/v1/endpoints/`
4. Add dependency in `api/deps.py` if needed
5. Register router in `api/v1/api.py`
6. Add error handler in `api/v1/errors.py` if needed
