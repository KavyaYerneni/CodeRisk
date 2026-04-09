"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from coderisk import __version__
from coderisk.api.dependencies import init_predictor
from coderisk.api.routes import router
from coderisk.config import get_env_settings
from coderisk.logging_config import get_logger, setup_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_env_settings()
    setup_logging(level=settings.coderisk_log_level)
    logger = get_logger(__name__)
    state = init_predictor()
    if state.load_error:
        logger.warning("startup_model_not_ready detail=%s", state.load_error)
    else:
        logger.info("startup_model_ready model_dir=%s", state.model_dir)
    yield


app = FastAPI(
    title="CodeRisk API",
    version=__version__,
    description="PR risk scoring service",
    lifespan=lifespan,
)
app.include_router(router)
