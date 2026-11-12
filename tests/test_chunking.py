import backend.services.vector_service as vector_service

LONG_TEXT = " ".join(f"word{i}" for i in range(300))

def make_chunks(monkeypatch, text):
    """Run ingest_text but capture the chunks instead of saving them."""
    saved = []
    monkeypatch.setattr(vector_service, "ingest_json", lambda name, items: saved.extend(items) or len(items))
    vector_service.ingest_text("t", text, "azul")
    return saved

def test_long_text_is_split_into_small_chunks(monkeypatch):
    chunks = make_chunks(monkeypatch, LONG_TEXT)
    assert len(chunks) > 1
    assert all(len(chunk["text"]) <= 300 for chunk in chunks)

def test_chunk_ids_are_numbered(monkeypatch):
    chunks = make_chunks(monkeypatch, LONG_TEXT)
    assert [chunk["id"] for chunk in chunks] == [f"azul_chunk_{i}" for i in range(len(chunks))]

def test_no_text_is_lost(monkeypatch):
    chunks = make_chunks(monkeypatch, LONG_TEXT)
    assert set(" ".join(chunk["text"] for chunk in chunks).split()) == set(LONG_TEXT.split())