from contextlib import asynccontextmanager
import importlib
import json
import logging
import logging.config
import os
import colorlog
from pathlib import Path
from typing import Any, AsyncContextManager, AsyncGenerator

import dotenv
from fastapi import FastAPI

from api.threat_analysis import ThreatAnalysis
from api.typings.models.indicators import ThreatIndicatorsBody

dotenv.load_dotenv()


def setup_logging() -> None:
    # a directory to store logs files
    log_path = Path("logs")
    if not log_path.exists():
        log_path.mkdir(parents=True)
        log_path.chmod(0o740)

    config_file = "configs/logging.json"
    with open(config_file) as f:
        logging.config.dictConfig(json.load(f))


def load_processors() -> None:
    processor_dir = "processors"

    for filename in os.listdir(processor_dir):
        if filename.endswith(".py") and filename not in ("__init__.py", "baseclass.py"):
            module_name = filename[:-3]
            importlib.import_module(f"api.{processor_dir}.{module_name}")
            assert logger is not None
            logger.info("Loaded module %s", module_name)


threat_analysis = None
logger = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # runs before the server starts
    global threat_analysis
    global logger
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("SecurityIQ is starting up")
    load_processors()
    threat_analysis = ThreatAnalysis()
    logger.info("SecurityIQ is ready")
    yield
    # runs after the server stops
    logger.info("SecurityIQ is shutting down, Goodbye")
    threat_analysis = None
    logger = None

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root() -> dict[str, Any]:
    return {"success": True, "message": "SecurityIQ is running"}


@app.post("/api/v1/threat-analysis")
def query_analysis(body: ThreatIndicatorsBody) -> dict[str, Any]:
    assert logger is not None
    logger.debug("Received request: %s", body)
    # temporary returning everything, will add pre-processing and scoring system later
    assert threat_analysis is not None
    return threat_analysis.analyse_threat(body.indicators)