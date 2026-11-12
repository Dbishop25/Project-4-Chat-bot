from pathlib import Path

from langchain_core.documents import Document

import backend.services.chunking_service as chunking_service


def test_ingest_md_splits_by_headers_and_replaces_source_docs(monkeypatch, tmp_path):
    markdown_path = tmp_path / "azul.md"
    markdown_path.write_text(
        "# Azul\n\n## Gameplay\nDraft tiles.\n\n## Scoring\nScore adjacent tiles.",
        encoding="utf-8",
    )

    class FakeVectorStore:
        def __init__(self):
            self.records = {"old-azul": {"source": "azul.md"}}
            self.added = []
            self.deleted = []

        def get(self, *, include):
            return {
                "ids": list(self.records),
                "metadatas": list(self.records.values()),
            }

        def delete(self, *, ids):
            self.deleted.extend(ids)
            for document_id in ids:
                self.records.pop(document_id, None)

        def add_documents(self, *, documents):
            self.added.extend(documents)

    store = FakeVectorStore()
    monkeypatch.setattr(chunking_service, "CLEANED_DIR", tmp_path)
    monkeypatch.setattr(
        chunking_service, "create_or_get_collection", lambda name: store
    )

    assert chunking_service.ingest_md("collection_text") == 2
    assert store.deleted == ["old-azul"]
    assert [document.metadata["h2"] for document in store.added] == [
        "Gameplay",
        "Scoring",
    ]
    assert all(document.metadata["game"] == "Azul" for document in store.added)
    assert all(document.metadata["source"] == "azul.md" for document in store.added)
    assert all(
        not Path(document.metadata["source"]).is_absolute()
        for document in store.added
    )
    assert all(isinstance(document, Document) for document in store.added)