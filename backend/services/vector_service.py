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
def search_collection(collection_name:str, query:str, k:int=5):

    collection = create_or_get_collection(collection_name)

    results = collection.similarity_search_with_score(query, k)

    return results





# To ingest documents (txt.) into chunks and store it into a collection.
def ingest_text(collection_name:str, text:str, source_id:str):

    text = text.strip()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, # every 300 characters, make a new chunk
        chunk_overlap=100, # chunks will overlap with each other by 100 chars (keeps context)
        separators=["\n\n", "\n", ".", " "]
    )

    chunks = splitter.split_text(text)

    print(chunks)
    print("CHUNK LENGTH--------")
    print(len(chunks))

    docs = []

    for i, chunk in enumerate(chunks):

        chunk_id = f"{source_id}_chunk_{i}"

        docs.append({"id":chunk_id, "text":chunk})

    return ingest_json(collection_name, docs)




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




