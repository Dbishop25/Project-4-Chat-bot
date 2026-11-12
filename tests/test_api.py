import pytest

import backend.api.boardgame as boardgame
from backend.core.config import settings
from backend.services.retrieval_service import ABSTENTION



def ask(client, question= "How many tiles are in each factory?", session_id= "session-1"):
    return client.post("/api/chat", json={"question": question, "session_id": session_id},)

# Root Test
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

# Chat Tests

def test_answerable_question(api):
    response = ask(api.client)
    assert response.status_code == 200
    assert response.json() == {
        "answer": "Each factory holds 4 tiles [1].",
        "sources": [
            {
                "title": "Azul Rules",
                "content": "Each factory holds 4 tiles. The number of factories depends on the number of players.",
                "page": 3,
            }
        ],
    }
    
def test_out_of_scope_question(api):
    api.retriever.matches = []
    assert ask(api.client, "What is the capital of France?", "session1").json() == {
        "answer": ABSTENTION,
        "sources": []
    }

def test_inappropriate_question(api):
    api.retriever.matches = []
    assert ask(api.client, "Can you wash your bum?", "session1").json() == {
        "answer": ABSTENTION,
        "sources": []
    }
@pytest.mark.parametrize("body", [
    {"question": "   ", "session_id": "session-1"},
    {"question": "tiles?", "session_id": ""},
    {"question": "tiles?"},
])
def test_bad_input(api, body):
    assert api.client.post("/api/chat", json=body).status_code == 422

# Session Tests

def test_delete_session_clears_history(api):
    ask(api.client, "first")
    assert api.client.delete("/api/chat/session-1").status_code == 204
    ask(api.client, "second")
    assert len(api.llm.prompts) == 2  # one LLM call each = no history-based rewrite

def test_cors_allows_frontend(client):
    origin = settings.frontend_origins[0]
    response = client.options("/api/chat", headers={
        "Origin": origin, "Access-Control-Request-Method": "POST"})
    assert response.headers.get("access-control-allow-origin") == origin

def test_submit_json(client, monkeypatch):
    monkeypatch.setattr(boardgame, "ingest_json", lambda collection_name, items: len(items))
    items = [{"id": "a", "text": "Each factory display holds 4 tiles."}]
    assert client.post("/boardgame/submit_json", json=items).json() == {"ingested_items": 1}


def test_submit_text_passes_collection_name(client, monkeypatch):
    received = {}

    def fake_ingest_text(collection_name):
        received["collection_name"] = collection_name
        return 3

    monkeypatch.setattr(boardgame, "ingest_text", fake_ingest_text)
    response = client.post(
        "/boardgame/submit_text", json={"collection_name": "collection_text"}
    )

    assert response.json() == {"ingested_items": 3}
    assert received["collection_name"] == "collection_text"

# LLM Tests

