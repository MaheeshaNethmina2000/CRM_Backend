"""
Session-level fixtures shared across all tests.

DB strategy:
- Uses a dedicated PostgreSQL test database (same engine as prod — no SQLite shortcuts).
- Creates all tables once per session, then wraps every test in a transaction
  that is rolled back after the test completes. This gives full isolation
  without the cost of dropping/recreating schema on every test.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config.database_config import Base, get_database
from app.config.config import (
    POSTGRES_USERNAME,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB_NAME,
)
from main import app

# ---------------------------------------------------------------------------
# Test database — same engine as production (PostgreSQL)
# Override POSTGRES_DB_NAME with a dedicated test DB in your .env.test
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}_test"
)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ---------------------------------------------------------------------------
# Schema lifecycle — create once, drop after the session
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_schema():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# ---------------------------------------------------------------------------
# Transaction rollback isolation — each test gets a clean slate
# ---------------------------------------------------------------------------
@pytest.fixture()
def db():
    """
    Yields a DB session wrapped in a transaction that is rolled back
    after each test. No data persists between tests.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Propagate savepoints so nested transactions work correctly
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    session.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# HTTP test client — uses the rolled-back DB session above
# ---------------------------------------------------------------------------
@pytest.fixture()
def client(db):
    def override_get_database():
        yield db

    app.dependency_overrides[get_database] = override_get_database
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Auth helpers — pre-built JWT tokens for role-based endpoint testing
# ---------------------------------------------------------------------------
@pytest.fixture()
def user_token():
    from app.util.security import create_access_token
    return create_access_token(user_id="test-user-uuid")


@pytest.fixture()
def admin_token():
    from app.util.security import create_access_token
    return create_access_token(user_id="test-admin-uuid")


@pytest.fixture()
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
