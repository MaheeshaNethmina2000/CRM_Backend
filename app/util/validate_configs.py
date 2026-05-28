import logging
import sys
from app.config.config import settings

logger = logging.getLogger("app")

def validate_startup_configurations() -> None:
    # Pydantic validates presence automatically; this function enforces logical correctness and security
    try:
        # Enforce that critical database connection variables are not populated with empty strings
        critical_vars = [
            ("POSTGRES_USERNAME", settings.POSTGRES_USERNAME),
            ("POSTGRES_PASSWORD", settings.POSTGRES_PASSWORD),
            ("POSTGRES_DB_NAME", settings.POSTGRES_DB_NAME),
            ("POSTGRES_HOST", settings.POSTGRES_HOST)
        ]
        for name, value in critical_vars:
            assert value.strip() != "", f"Configuration variable {name} cannot be an empty string"

        # Verify the dynamically computed URL utilizes the required asynchronous driver
        assert settings.DATABASE_URL.startswith("postgresql+asyncpg://"), "DATABASE_URL must use the asyncpg postgres driver"

        # Enforce absolute cryptographic security boundaries for authentication token generation
        assert len(settings.JWT_SECRET) >= 32, "JWT_SECRET must be at least 32 characters long to ensure production security"

        logger.info("System startup configuration validation completed successfully.")

    except AssertionError as error:
        # Intercepts the failure and logs a critical alert before gracefully terminating the server container
        logger.critical(f"Configuration initialization safety check failed: {error}")
        sys.exit(1)