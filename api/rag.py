from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.tools import Tool, create_retriever_tool
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

from langchain_text_splitters import RecursiveJsonSplitter

@lru_cache
def _get_chroma() -> Chroma:
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        collection_name="investigation-context", embedding_function=embedding_function, persist_directory="chroma-db"
    )

@lru_cache
def initialize_rag() -> tuple[Chroma, Tool, RecursiveJsonSplitter]:
    db = _get_chroma()
    retriever = db.as_retriever(search_kwargs={"k": 5})
    retreival_tool = create_retriever_tool(retriever, "investigation_context", "Context for the investigation that came from tools, use it to answer the user's question.")

    splitter = RecursiveJsonSplitter()

    return (db, retreival_tool, splitter)
