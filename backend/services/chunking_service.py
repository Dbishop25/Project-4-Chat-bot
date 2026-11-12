
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from .vector_service import create_or_get_collection

CLEANED_DIR = Path(__file__).resolve().parents[2] / "data" / "cleaned"
HEADERS_TO_SPLIT_ON = [
     ("#", "h1"),
     ("##", "h2"),
     ("###", "h3"),
     ("####", "h4"),
     ("#####", "h5"),
     ("######", "h6"),
]


def ingest_md(collection_name:str):
     splitter = MarkdownHeaderTextSplitter(
          headers_to_split_on=HEADERS_TO_SPLIT_ON,
          strip_headers=False,
     )
     source_paths = sorted(CLEANED_DIR.rglob("*.md"))
     docs = []

     for path in source_paths:
          source = path.relative_to(CLEANED_DIR).as_posix()
          markdown = path.read_text(encoding="utf-8")
          for chunk in splitter.split_text(markdown):
               metadata = {
                    **chunk.metadata,
                    "source": source,
                    "game": chunk.metadata.get("h1", path.stem),
               }
               docs.append(
                    Document(page_content=chunk.page_content, metadata=metadata)
               )

     if not docs:
          return 0

     vectorstore = create_or_get_collection(collection_name)
     relative_sources = {
          path.relative_to(CLEANED_DIR).as_posix() for path in source_paths
     }
     stored = vectorstore.get(include=["metadatas"])
     existing_ids = [
          document_id
          for document_id, metadata in zip(
               stored.get("ids", []), stored.get("metadatas", [])
          )
          if isinstance(metadata, dict)
          and metadata.get("source") in relative_sources
     ]
     if existing_ids:
          vectorstore.delete(ids=existing_ids)

     vectorstore.add_documents(documents=docs)
     return len(docs)