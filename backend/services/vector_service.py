from typing import Any
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


PERSISTY_DIRECTORY = "data/chroma"
EMBEDDING_MODEL = OllamaEmbeddings(model="nomic-embed-text")
vector_store: dict[str, Chroma] = {}




def create_or_get_collection(collection_name:str):

    if collection_name not in vector_store:
        vector_store[collection_name] = Chroma(
            persist_directory=PERSISTY_DIRECTORY,
            collection_name=collection_name,
            embedding_function=EMBEDDING_MODEL
        )


    return vector_store[collection_name]





# Similarity Search for Retrival
def search_collection(collection_name:str, query:str, k:int=5, relevance_threshold:float | None = None):

    collection = create_or_get_collection(collection_name)

    results = collection.similarity_search_with_relevance_scores(query, k =k, score_threshold=relevance_threshold)

    return results





# To ingest documents (txt.) into chunks and store it into a collection.
def ingest_text(collection_name: str):
    from .chunking_service import ingest_md
    return ingest_md(collection_name)




def ingest_json(collection_name:str, items:list[dict[str, Any]]):

    collection = create_or_get_collection(collection_name)

    docs = [
        Document(page_content=item["text"], metadata=item.get("metadata", {}))
        for item in items
    ]

    print(items)

    # Attach IDs to each Document (easy since the JSON has an "id" field)
    ids = [item["id"] for item in items]

    # Finally add the Documents to the Collection!!
    embedded_docs = collection.add_documents(documents=docs, ids=ids)

    # Just wanna see
    print(embedded_docs)

    # Return the amount of ingested items just for visibility
    return len(embedded_docs)




