import logging
import typing

from fastapi import FastAPI

from api.rag import initialize_rag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
chroma, retreival_tool, splitter = initialize_rag()
logger.info("RAG model initialized")


@app.get("/")
def root() -> dict[str, typing.Any]:
    return {"success": True, "message": "SecurityIQ is running"}
