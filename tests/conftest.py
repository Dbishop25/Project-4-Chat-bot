import os  

TEST_ENV = {
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_CHAT_MODEL": "llama3.2:3b",
    "OLLAMA_EMBEDDING_MODEL": "nomic-embed-text",
    "CHROMA_PERSIST_DIRECTORY": "data/chroma",
    "RAG_TOP_K": "5",
    "RAG_RELEVANCE_THRESHOLD": "0.5",
    "RAG_SESSION_HISTORY_EXCHANGES": "5",
    "FRONTEND_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
}

for key, value in TEST_ENV.items():
    os.environ.setdefault(key, value)

from types import SimpleNamespace  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.embeddings import DeterministicFakeEmbedding  # noqa: E402

import backend.api.boardgame as boardgame  # noqa: E402
import backend.services.vector_service as vector_service  # noqa: E402
from backend.main import app  # noqa: E402
from backend.services.retrieval_service import RAGService  # noqa: E402

AZUL = Document(
    page_content="Each factory holds 4 tiles. The number of factories depends on the number of players.",
    metadata={"title": "Azul Rules", "page": 3},
)

class FakeLLM:
    """Stands in for ChatOllama. Returns `replies` in order (the last one repeats)."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.prompts = []
        self.error = None

    def invoke(self, messages):
        self.prompts.append("\n".join(str(m.content) for m in messages))
        if self.error:
            raise self.error
        reply = self.replies[min(len(self.prompts), len(self.replies)) - 1]
        return SimpleNamespace(content=reply)

class FakeRetriever:
    """Stands in for search_collection. Returns `matches` and records each call."""

    def __init__(self, matches):
        self.matches = matches
        self.calls = []
        self.error = None

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.matches

@pytest.fixture
def make_service():
    def _make(matches=None, replies=("Each factory holds 4 tiles",)):
        retriever = FakeRetriever([(AZUL, 0.9)] if matches is None else matches)
        llm = FakeLLM(*replies)
        service = RAGService(retriever=retriever, llm=llm, top_k=3,
                             relevance_threshold=0.5, history_exchanges=2)
        return service, retriever, llm
    return _make

@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def api(monkeypatch, make_service, client):
    service, retriever, llm = make_service()
    monkeypatch.setattr(boardgame, "rag_service", service)
    return SimpleNamespace(retriever=retriever, llm=llm, client=client)

@pytest.fixture
def isolate_store(monkeypatch, tmp_path):
    monkeypatch.setattr(vector_service, "PERSIST_DIRECTORY", str(tmp_path))
    monkeypatch.setattr(vector_service, "EMBEDDING_MODEL", DeterministicFakeEmbedding())
    monkeypatch.setattr(vector_service, "vector_store", {})  # Clear the in-memory store
    return vector_serviceimport os  

TEST_ENV = {
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_CHAT_MODEL": "llama3.2:3b",
    "OLLAMA_EMBEDDING_MODEL": "nomic-embed-text",
    "CHROMA_PERSIST_DIRECTORY": "data/chroma",
    "RAG_TOP_K": "5",
    "RAG_RELEVANCE_THRESHOLD": "0.5",
    "RAG_SESSION_HISTORY_EXCHANGES": "5",
    "FRONTEND_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
}

for key, value in TEST_ENV.items():
    os.environ.setdefault(key, value)

from types import SimpleNamespace  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.embeddings import DeterministicFakeEmbedding  # noqa: E402

import backend.api.boardgame as boardgame  # noqa: E402
import backend.services.vector_service as vector_service  # noqa: E402
from backend.main import app  # noqa: E402
from backend.services.retrieval_service import RAGService  # noqa: E402

AZUL = Document(
    page_content="Each factory holds 4 tiles. The number of factories depends on the number of players.",
    metadata={"title": "Azul Rules", "page": 3},
)

class FakeLLM:
    """Stands in for ChatOllama. Returns `replies` in order (the last one repeats)."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.prompts = []
        self.error = None

    def invoke(self, messages):
        self.prompts.append("\n".join(str(m.content) for m in messages))
        if self.error:
            raise self.error
        reply = self.replies[min(len(self.prompts), len(self.replies)) - 1]
        return SimpleNamespace(content=reply)

class FakeRetriever:
    """Stands in for search_collection. Returns `matches` and records each call."""

    def __init__(self, matches):
        self.matches = matches
        self.calls = []
        self.error = None

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.matches

@pytest.fixture
def make_service():
    def _make(matches=None, replies=("Each factory holds 4 tiles [S1].",)):
        retriever = FakeRetriever([(AZUL, 0.9)] if matches is None else matches)
        llm = FakeLLM(*replies)
        service = RAGService(retriever=retriever, llm=llm, top_k=3,
                             relevance_threshold=0.5, history_exchanges=2)
        return service, retriever, llm
    return _make

@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def api(monkeypatch, make_service, client):
    service, retriever, llm = make_service()
    monkeypatch.setattr(boardgame, "rag_service", service)
    return SimpleNamespace(retriever=retriever, llm=llm, client=client)

@pytest.fixture
def isolated_store(monkeypatch, tmp_path):
    monkeypatch.setattr(vector_service, "PERSISTY_DIRECTORY", str(tmp_path))
    monkeypatch.setattr(vector_service, "EMBEDDING_MODEL", DeterministicFakeEmbedding(size=64))
    monkeypatch.setattr(vector_service, "vector_store", {})  # Clear the in-memory store
    return vector_service