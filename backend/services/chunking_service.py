
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from .vector_service import create_or_get_collection, EMBEDDING_MODEL
from langchain_chroma import Chroma

loader = DirectoryLoader(path="data/cleaned",
                         glob="**/*.md",
                        loader_cls=UnstructuredMarkdownLoader
                         )
docs =loader.load()


def ingest_md(collection_name:str):

   vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=EMBEDDING_MODEL,
        persist_directory="data/chroma",
        collection_name=collection_name
    )
   return len(docs)