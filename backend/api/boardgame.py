from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any
from backend.services.retrieval_service import get_memory_chain
from backend.services.vector_service import ingest_text, ingest_json, search_collection

router = APIRouter(
    prefix="/boardgame",
    tags=["boardgame"]
)

chain = get_memory_chain()


# Pydantic Model for ingesting JSON
class IngestData(BaseModel):
    id:str
    text:str
    metadata:Any = None # Lazy, didn't wanna make a whole new object



@router.post("/submit_json")
async def submit_json(items:list[IngestData]):


    ingested_items = ingest_json(
        collection_name="collection_text",
        items=[item.dict() for item in items]
    )

    return {"ingested_items": ingested_items}



@router.post("/submit_text")
async def submit_text(text:IngestData):


    ingested_items = ingest_text(
        collection_name="collection_text",
        items=[text.dict()]
    )

    return {"ingested_items": ingested_items}


@router.get("/rag_chat")
async def tools_rag(query:str):

    # First, get the search results from the collection
    results = search_collection(
        collection_name="collection_text",
        query=query
        # We COULD set the k value here, or just let default to 5
    )

    # Here's the RAG part -
    # Augmenting the Generated response with the data we Retrieved
    return chain.invoke({
        "input": f"""
            Respond to the user's query based on the search results.
            
            The User's Query: {query}
            
            The Search Results: {results}
            
        """
    })




