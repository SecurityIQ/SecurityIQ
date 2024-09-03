import typing

from fastapi import FastAPI

from api.prompt import chat_system
from api.rag import initialize_rag

app = FastAPI()
chroma, retreival_tool, splitter = initialize_rag()


@app.get("/")
def root() -> dict[str, typing.Any]:
    print(chat_system)
    return {"success": True, "message": "SecurityIQ is running"}
