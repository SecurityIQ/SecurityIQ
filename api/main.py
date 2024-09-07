import json
import logging
import importlib
import os
import dotenv
from typing import Any

from fastapi import FastAPI

from api.threat_analysis import ThreatAnalysis
from api.typings.models.indicators import ThreatIndicatorsBody

dotenv.load_dotenv()

def setup_logging():
    # a directory to store logs files
    if not os.path.exists("logs"):
        os.makedirs("logs")

    config_file = "configs/logging.json"
    with open(config_file, "r") as f:
        logging.config.dictConfig(json.load(f))


setup_logging()
logger = logging.getLogger("securityiq.api")
    

def load_processors():
    processor_dir = "processors"

    for filename in os.listdir(processor_dir):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "baseclass.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"api.{processor_dir}.{module_name}")
            logging.info(f"Loaded module {module_name}")

# Initialize ThreatAnalysis class
threat_analysis = ThreatAnalysis()

app = FastAPI()

@app.get("/")
def root() -> dict[str, Any]:
    return {"success": True, "message": "SecurityIQ is running"}


@app.post("/api/v1/threat-analysis")
def query_analysis(body: ThreatIndicatorsBody) -> dict[str, Any]:
    info = threat_analysis.analyse_threat(body.indicators)
    return info

load_processors()