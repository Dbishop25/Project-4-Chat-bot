import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _required_value(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(
            f"Missing required setting {name}. Set it in the environment or .env file."
        )
    return value.strip()


def _int_setting(name: str, *, minimum: int) -> int:
    raw_value = _required_value(name)
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer; got {raw_value!r}.") from exc
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _float_setting(name: str, *, minimum: float, maximum: float) -> float:
    raw_value = _required_value(name)
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number; got {raw_value!r}.") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _origins_setting() -> list[str]:
    origins = [
        origin.strip() for origin in _required_value("FRONTEND_ORIGINS").split(",")
    ]
    if not origins or any(not origin for origin in origins):
        raise ValueError(
            "FRONTEND_ORIGINS must contain comma-separated, non-empty origins."
        )
    return origins


@dataclass(frozen=True)
class Settings:
    chroma_persist_directory: str
    ollama_chat_model: str
    ollama_embedding_model: str
    ollama_base_url: str
    rag_top_k: int
    rag_relevance_threshold: float
    rag_session_history_exchanges: int
    frontend_origins: list[str]


settings = Settings(
    chroma_persist_directory=_required_value("CHROMA_PERSIST_DIRECTORY"),
    ollama_chat_model=_required_value("OLLAMA_CHAT_MODEL"),
    ollama_embedding_model=_required_value("OLLAMA_EMBEDDING_MODEL"),
    ollama_base_url=_required_value("OLLAMA_BASE_URL"),
    rag_top_k=_int_setting("RAG_TOP_K", minimum=1),
    rag_relevance_threshold=_float_setting(
        "RAG_RELEVANCE_THRESHOLD", minimum=0.0, maximum=1.0
    ),
    rag_session_history_exchanges=_int_setting(
        "RAG_SESSION_HISTORY_EXCHANGES", minimum=1
    ),
    frontend_origins=_origins_setting(),
)
