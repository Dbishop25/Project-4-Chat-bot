import pytest
import json
from pathlib import Path


import backend.services.vector_service as vector_service

DOCS = [
    {"id": "azul_1", "text": "Each factory display holds 4 tiles.", "metadata": {"title": "Azul Rules", "page": 3}},
]

def test_injest_json_returns_count(isolated_store):
    assert isolated_store.ingest_json("t", DOCS) == 3


def test_search_finds_exact_text_with_metadata(isolated_store):
    isolated_store.ingest_json("t", DOCS)
    doc, _ = isolated_store.search_collection("t", DOCS[0]["text"], k=1)[0]
    assert doc.page_content == DOCS[0]["text"]
    assert doc.metadata == {"title": "Azul Rules", "page": 3}

def test_reingesting_does_not_duplicate(isolated_store):
    isolated_store.ingest_json("t", DOCS)
    isolated_store.ingest_json("t", DOCS)
    assert len(isolated_store.search_collection("t", "x", k=10)) == 3

@pytest.mark.xfail(strict=True, reason="BUG: metadata=None (what submit_json sends when it's "
                   "left out) crashes Document(). Fix: item.get('metadata') or {}")
def test_ingest_without_metadata(isolated_store):
    assert isolated_store.ingest_json("t", [{"id": "x", "text": "hi", "metadata": None}]) == 1

@pytest.mark.ollama
def test_hit_rate_on_real_index():
    """Real data/chroma + Ollama. The `expected` text should be in the top 5 chunks
    for at least 80% of answerable questions in test_questions.json."""
    questions = json.loads((Path(__file__).parent / "test_questions.json").read_text())
    answerable = [q for q in questions if q["type"] == "answerable" and q["game"] != "Example Game"]
    misses = [
        q["id"] for q in answerable
        if not any(q["expected"].lower() in doc.page_content.lower()
                   for doc, _ in vector_service.search_collection("collection_text", q["question"], k=5))
    ]
    print(f"\nmisses: {misses}")
    assert len(misses) <= 0.2 * len(answerable)
