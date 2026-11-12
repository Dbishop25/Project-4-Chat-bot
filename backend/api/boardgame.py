import logging
from pydantic import BaseModel
from typing import Any
from fastapi import APIRouter, HTTPException, Response

from backend.services.retrieval_service import RAGService, RAGServiceError
from backend.services.vector_service import ingest_json, ingest_text


logger = logging.getLogger(__name__)
rag_service = RAGService()

router = APIRouter(
    prefix="/boardgame",
    tags=["boardgame"]
)
chat_router = APIRouter(prefix="/api", tags=["chat"])


# Pydantic Model for ingesting JSON
class IngestData(BaseModel):
    id:str
    text:str
    metadata:Any = None # Lazy, didn't wanna make a whole new object


class IngestCollectionRequest(BaseModel):
    collection_name: str


class ChatRequest(BaseModel):
    question: str
    session_id: str


class SourceResponse(BaseModel):
    title: str
    content: str
    page: str | int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]



@router.post("/submit_json")
async def submit_json(items:list[IngestData]):


    ingested_items = ingest_json(
        collection_name="collection_text",
        items=[item.dict() for item in items]
    )

    return {"ingested_items": ingested_items}



@router.post("/submit_text")
async def submit_text(request: IngestCollectionRequest):


    ingested_items = ingest_text(collection_name=request.collection_name)

    return {"ingested_items": ingested_items}


@router.get("/rag_chat")
async def tools_rag(query:str):
    """Legacy stateless route; new clients should use POST /api/chat."""
    try:
        return rag_service.answer(query)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RAGServiceError as exc:
        logger.exception("RAG service failed")
        raise HTTPException(
            status_code=503, detail="The answer service is temporarily unavailable."
        ) from exc


@chat_router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question must not be empty.")
    session_id = request.session_id.strip()
    if not session_id:
        raise HTTPException(status_code=422, detail="Session ID must not be empty.")
    try:
        result = rag_service.answer(question, session_id)
        return ChatResponse(**result)
    except RAGServiceError as exc:
        logger.exception("RAG service failed")
        raise HTTPException(
            status_code=503, detail="The answer service is temporarily unavailable."
        ) from exc


@chat_router.delete("/chat/{session_id}", status_code=204)
def clear_chat_session(session_id: str) -> Response:
    rag_service.clear_session(session_id)
    return Response(status_code=204)




