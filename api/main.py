import importlib
import json
import logging
import logging.config
import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import dotenv
import jwt
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

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


def verify_jwt(token: str, client_host: str) -> bool:
    try:
        jwt.decode(
            token,
            os.environ["CLERK_JWT_PUBKEY"],
            algorithms=["RS256"],
        )
    except jwt.exceptions.PyJWTError as e:
        get_logger().warning("%s > Authentication Failed: %s", client_host, e)
        return False
    else:
        return True


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


PROTECTED_ROUTES = ["/api/v1/threat-analysis"]


app = FastAPI(lifespan=lifespan)
security = HTTPBearer()


async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path in PROTECTED_ROUTES:
        token = await security(request)
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "detail": "Missing Token"},
            )
        client_host = request.client.host if request.client else "unknown_host"
        if not verify_jwt(token.credentials, client_host):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "detail": "Invalid Token"},
            )
    return await call_next(request)


app.middleware("http")(auth_middleware)


@app.get("/")
def root() -> dict[str, Any]:
    return {"success": True, "message": "SecurityIQ is running"}


@app.post("/api/v1/threat-analysis")
def query_analysis(
    body: ThreatIndicatorsBody,
) -> dict[str, Any]:
    logger = get_logger()
    threat_analysis = get_threat_analysis()

    logger.debug("Received request: %s", body)
    # temporary returning everything, will add pre-processing and scoring system later
    return threat_analysis.analyse_threat(body.indicators)
