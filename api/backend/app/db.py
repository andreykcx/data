from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

try:
    from alembic import command
    from alembic.config import Config
except ImportError:  # pragma: no cover - handled gracefully when Alembic is missing
    command = None
    Config = None

logger = logging.getLogger(__name__)


_engine: Optional[Engine] = None


def get_database_url() -> Optional[str]:
    return os.getenv("DATABASE_URL")


def get_engine() -> Engine:
    global _engine

    database_url = get_database_url()
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    if _engine is None:
        _engine = create_engine(database_url, pool_pre_ping=True)

    return _engine


def check_database_connection() -> bool:
    try:
        engine = get_engine()
    except RuntimeError as exc:
        logger.warning("Database URL is not configured: %s", exc)
        return False

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except OperationalError as exc:
        logger.warning("Database connectivity check failed: %s", exc)
        return False


def _get_alembic_config() -> Optional[Config]:
    if command is None or Config is None:
        logger.warning("Alembic is not installed; skipping migration setup.")
        return None

    database_url = get_database_url()
    if not database_url:
        logger.warning("DATABASE_URL is not set; skipping migration setup.")
        return None

    config_path = Path(__file__).resolve().parents[2] / "alembic.ini"
    if not config_path.exists():
        raise FileNotFoundError(f"Alembic config not found at {config_path}")

    config = Config(str(config_path))
    config.set_main_option("sqlalchemy.url", database_url)

    script_location = (config_path.parent / config.get_main_option("script_location")).resolve()
    config.set_main_option("script_location", str(script_location))

    return config


def run_migrations_with_retry(*, attempts: int = 5, backoff_seconds: int = 2) -> bool:
    try:
        config = _get_alembic_config()
    except Exception as exc:  # pragma: no cover - defensive catch-all
        logger.error("Failed to prepare Alembic configuration: %s", exc, exc_info=True)
        return False

    if config is None:
        return False

    for attempt in range(1, attempts + 1):
        try:
            command.upgrade(config, "head")
            logger.info("Database migrations applied successfully.")
            return True
        except OperationalError as exc:
            logger.warning(
                "Database not ready (attempt %s/%s): %s",
                attempt,
                attempts,
                exc,
            )
            time.sleep(backoff_seconds * attempt)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            logger.error("Unexpected migration error: %s", exc, exc_info=True)
            break

    logger.error("Migrations did not complete after %s attempts; continuing without applying migrations.", attempts)
    return False
