import importlib
import json
import logging
import logging.config
import jwt
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

import dotenv
from fastapi import FastAPI, Request, Response, status
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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
    processor_dir = "processors"
    logger = get_logger()
    for root, _, files in os.walk(processor_dir):
        for filename in files:
            if filename.endswith(".py") and filename not in (
                "__init__.py",
                "baseclass.py",
            ):
                module_name = filename[:-3]
                # Generate the import path dynamically
                relative_path = Path(root).relative_to(processor_dir)

                if relative_path.parts:
                    module_import_path = f"api.{'.'.join(['processors',
                                                          *relative_path.parts])}.{module_name}"
                else:
                    module_import_path = f"api.processors.{module_name}"

                importlib.import_module(module_import_path)
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
security = HTTPBearer()

@app.get("/")
def root() -> dict[str, Any]:
    return {"success": True, "message": "SecurityIQ is running"}


@app.post("/api/v1/threat-analysis")
def query_analysis(body: ThreatIndicatorsBody, credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], response: Response) -> dict[str, Any]:
    logger = get_logger()
    try:
        jwt.decode(credentials.credentials, os.environ["CLERK_JWT_PUBKEY"], algorithms=["RS256"])
    except jwt.exceptions.PyJWTError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"success": False, "message": "Invalid Token"}

    threat_analysis = get_threat_analysis()

    logger.debug("Received request: %s", body)
    # temporary returning everything, will add pre-processing and scoring system later
    return threat_analysis.analyse_threat(body.indicators)
