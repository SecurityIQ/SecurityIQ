import logging
import importlib
import os
from typing import Any

from fastapi import FastAPI

from api.threat_analysis import ThreatAnalysis
from api.typings.models.indicators import ThreatIndicatorsBody

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize ThreatAnalysis class
threat_analysis = ThreatAnalysis()

app = FastAPI()

def load_processor_modules():
    processor_dir = "processors"

    for filename in os.listdir(processor_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"api.{processor_dir}.{module_name}")
            logging.info(f"Loaded module {module_name}")

load_processor_modules()

@app.get("/")
def root() -> dict[str, Any]:
    return {"success": True, "message": "SecurityIQ is running"}


@app.post("/api/v1/threat-analysis")
def query_analysis(body: ThreatIndicatorsBody) -> dict[str, Any]:
    info = threat_analysis.analyse_threat(body.indicators)
    logger.info(info)
    return info
