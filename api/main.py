import logging
from typing import Any

from fastapi import FastAPI

from api.typings.models.indicators import ThreatIndicatorsBody

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def root() -> dict[str, Any]:
    return {"success": True, "message": "SecurityIQ is running"}


@app.post("/api/v1/threat-analysis")
def query_analysis(body: ThreatIndicatorsBody) -> dict[str, Any]:
    logger.debug(body)
    return {}
