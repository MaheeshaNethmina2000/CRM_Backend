import inspect

from app.config import config


def validate_config_vars():
    config_vars = {
        name: value
        for name, value in inspect.getmembers(config)
        if not name.startswith("__") and not inspect.ismodule(value)
    }
    required_vars = {
        name: value
        for name, value in config_vars.items()
        if name in {
            "POSTGRES_USERNAME",
            "POSTGRES_PASSWORD",
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_DB_NAME",
        }
    }
    missing_vars = [name for name, value in required_vars.items() if value in {None, ""}]
    if missing_vars:
        raise ValueError(f"Missing required configuration variables: {', '.join(missing_vars)}")
