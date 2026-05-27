# python-fastapi-folder-structure

A standardised Python FastAPI project template with a clean layered architecture, AI provider integration, JWT authentication, and CI/CD workflows.

---

## Folder Structure

```
python-fastapi-folder-structure/
|
+-- .github/
|   +-- workflows/
|       +-- be-dev.yml              <- Auto-deploy on push to dev
|       +-- be-prod.yml             <- Auto-deploy on push to main
|
+-- app/
|   +-- ai/                         <- AI provider integration
|   |   +-- base_provider.py        <- Abstract BaseAIProvider + ExtractionResult
|   |   +-- provider_factory.py     <- Registry pattern, no if/else chains
|   |   +-- prompts/
|   |   |   +-- sample_prompt.py    <- Define extraction prompts here
|   |   +-- providers/
|   |       +-- gemini_provider.py  <- Google Gemini (REST, vision)
|   |       +-- openai_provider.py  <- OpenAI GPT-4o (vision)
|   |       +-- mock_provider.py    <- Deterministic mock for local dev/testing
|   |
|   +-- config/
|   |   +-- config.py               <- All env vars loaded via dotenv
|   |   +-- constants.py            <- App-wide constants
|   |   +-- database_config.py      <- SQLAlchemy engine + session + Base
|   |   +-- logging_config.py       <- Coloured console logger
|   |
|   +-- controller/                 <- FastAPI routers (add per feature)
|   |   +-- __init__.py             <- Aggregates all routers + health endpoint
|   |
|   +-- entity/                     <- SQLAlchemy ORM models (add per feature)
|   |   +-- base.py                 <- UUIDPrimaryKeyMixin, TimestampMixin, etc.
|   |
|   +-- enums/
|   |   +-- enums.py                <- Shared enums (UserRole, SortOrderEnum)
|   |
|   +-- exceptions/
|   |   +-- base_exception.py       <- BaseAppException
|   |   +-- exception.py            <- NotFoundException, BadRequestException
|   |   +-- exception_handler.py    <- Global FastAPI exception handlers
|   |
|   +-- model/                      <- Pydantic request/response schemas
|   |   +-- generic_response.py     <- GenericResponse (success / failed)
|   |   +-- generic_pagination_response.py
|   |
|   +-- repository/                 <- Data access layer (add per feature)
|   |   +-- base_repository.py      <- save / get_by_id / update
|   |
|   +-- service/                    <- Business logic layer (add per feature)
|   |
|   +-- templates/
|   |   +-- email/                  <- Jinja2 HTML email templates
|   |
|   +-- util/
|       +-- security.py             <- JWT creation, password hashing, auth deps
|       +-- validate_configs.py     <- Startup env var validation
|       +-- pagination.py           <- normalize_pagination() helper
|
+-- tests/
|   +-- conftest.py                 <- Session fixtures: DB rollback, TestClient, JWT tokens
|   +-- unit/
|   |   +-- conftest.py             <- Mock fixtures (AI provider, email, DB session)
|   |   +-- test_pagination.py
|   |   +-- test_generic_response.py
|   |   +-- test_exceptions.py
|   +-- integration/
|   |   +-- conftest.py             <- Integration fixtures (seeded DB records)
|   |   +-- test_health.py          <- Full HTTP cycle via TestClient
|   +-- factories/
|       +-- base_factory.py         <- factory_boy + Faker test data factories
|
+-- .env.example                    <- Copy to .env and fill in values
+-- .gitignore
+-- Dockerfile
+-- docker-compose.dev.yml
+-- docker-compose.prod.yml
+-- main.py                         <- FastAPI app entry point
+-- pytest.ini                      <- Pytest configuration
+-- requirements.txt
+-- requirements-dev.txt            <- Dev/test dependencies (pytest, httpx)
```

---

## Architecture

This project follows a layered architecture:

```
Controller -> Service -> Repository -> Entity
```

| Layer         | Responsibility                                      |
|---------------|-----------------------------------------------------|
| controller/   | HTTP routing, request validation, response shaping  |
| service/      | Business logic, orchestration                       |
| repository/   | Database queries (extends BaseRepository)           |
| entity/       | SQLAlchemy ORM table definitions                    |
| model/        | Pydantic schemas for request/response               |

---

## AI Provider System

The AI layer uses a strategy + registry pattern. Swapping providers requires only an env var change:

| Provider | Env var value | Notes                               |
|----------|---------------|-------------------------------------|
| Gemini   | gemini        | Default. Requires GEMINI_API_KEY    |
| OpenAI   | openai        | Requires pip install openai + OPENAI_API_KEY |
| Mock     | mock          | No API calls. For local dev/testing |

Set in .env:

```
AI_PROVIDER=gemini
```

---

## Getting Started

### 1. Clone and set up environment

```bash
cp .env.example .env
# Fill in your values in .env
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run locally

```bash
uvicorn main:app --reload
```

### 4. Run with Docker

```bash
docker compose -f docker-compose.dev.yml up --build
```

---

## Running Tests

### Install dev dependencies
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Run all tests (with coverage)
```bash
pytest
```

### Run by type using markers
```bash
pytest -m unit         # unit tests only  — fast, no DB
pytest -m integration  # integration tests — requires test DB
```

### Coverage report
```bash
pytest --cov=app --cov-report=html
# Open coverage-report/index.html
```

### Test DB setup
Integration tests require a dedicated PostgreSQL database:
```env
# .env (test DB name = POSTGRES_DB_NAME + _test)
POSTGRES_DB_NAME=my_database   # tests will use: my_database_test
```

---

## Adding a New Feature

1. Entity     - add app/entity/<name>.py (extend UUIDPrimaryKeyMixin, TimestampMixin)
2. Repository - add app/repository/<name>_repository.py (extend BaseRepository)
3. Service    - add app/service/<name>_service.py
4. Model      - add app/model/<name>_model.py (Pydantic schemas)
5. Controller - add app/controller/<name>_controller.py and register the router in app/controller/__init__.py

---

## CI/CD

| Branch | Workflow     | Action                   |
|--------|--------------|--------------------------|
| dev    | be-dev.yml   | SSH deploy to dev server |
| main   | be-prod.yml  | SSH deploy to prod server|

Configure the following GitHub secrets: SSH_HOST, SSH_USER, SSH_KEY, SSH_PORT, DEPLOY_PATH.