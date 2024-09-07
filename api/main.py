import importlib
import json
import logging
import logging.config
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import dotenv
from fastapi import FastAPI

from api.exceptions.init_exceptions import ClassUninitializedError
from api.threat_analysis import ThreatAnalysis
from api.typings.models.indicators import ThreatIndicatorsBody

dotenv.load_dotenv()


class AppState:
    def __init__(self) -> None:
        self.threat_analysis: ThreatAnalysis | None = None
        self.logger: logging.Logger | None = None


app_state = AppState()


def get_logger() -> logging.Logger:
    if not app_state.logger:
        raise ClassUninitializedError(logging.Logger.__name__)
    return app_state.logger


def get_threat_analysis() -> ThreatAnalysis:
    if not app_state.threat_analysis:
        raise ClassUninitializedError(ThreatAnalysis.__name__)
    return app_state.threat_analysis


def setup_logging() -> None:
    # a directory to store logs files
    log_path = Path("logs")
    if not log_path.exists():
        log_path.mkdir(parents=True)
        log_path.chmod(0o740)

    config_file = "configs/logging.json"
    with Path(config_file).open() as f:
        logging.config.dictConfig(json.load(f))


def load_processors() -> None:
    processor_dir = "processors/indicator"
    logger = get_logger()
    for filename in os.listdir(processor_dir):
        if filename.endswith(".py") and filename not in ("__init__.py", "baseclass.py"):
            module_name = filename[:-3]
            importlib.import_module(
                f"api.{'.'.join(processor_dir.split('/'))}.{module_name}",
            )
            logger.info("Loaded module %s", module_name)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    # runs before the server starts
    setup_logging()
    app_state.logger = logging.getLogger(__name__)
    app_state.logger.info("SecurityIQ is starting up")
    load_processors()
    app_state.threat_analysis = ThreatAnalysis()
    app_state.logger.info("SecurityIQ is ready")
    yield
    # runs after the server stops
    app_state.logger.info("SecurityIQ is shutting down, Goodbye")
    app_state.threat_analysis = None
    app_state.logger = None


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root() -> dict[str, Any]:
    return {"success": True, "message": "SecurityIQ is running"}


@app.post("/api/v1/threat-analysis")
def query_analysis(body: ThreatIndicatorsBody) -> dict[str, Any]:
    logger = get_logger()
    threat_analysis = get_threat_analysis()
    if logger is None:
        logging.error("Logger is not initialized")
        return {"success": False, "message": "Logger is not initialized"}

    logger.debug("Received request: %s", body)
    # temporary returning everything, will add pre-processing and scoring system later
    if threat_analysis is None:
        logger.error("ThreatAnalysis is not initialized")
        return {"success": False, "message": "ThreatAnalysis is not initialized"}

    return threat_analysis.analyse_threat(body.indicators)
