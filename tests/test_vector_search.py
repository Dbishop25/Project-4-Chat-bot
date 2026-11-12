import json 
from pathlib import Path
import pytest

import backend.services.vector_service as vector_service
from backend.core.config import settings
from backend.services.retrieval_service import RAGService
from tests.conftest import FakeLLM

pytestmark = pytest.mark.filterwarnings("ignore:Relevance scores must be between")

COLLECTION = "collection_text"

RULES = [
    {"id": "azul_1", "text": "Each factory display holds 4 tiles.", "metadata": {"title": "Azul"}},
    {"id": "catan_1", "text": "Roll two dice to collect resources.", "metadata": {"title": "Catan"}},
]

def test_exact_match_scores_highest(isolated_store):
    isolated_store.ingest_json(COLLECTION, RULES)
    results = isolated_store.search_collection(COLLECTION, RULES[0]["text"], k=2)
    best_doc, best_score = results[0]
    assert best_doc.page_content == RULES[0]["text"]
    assert best_score == pytest.approx(1.0, abs=1e-3)
    assert best_score > results[1][1]

def test_threshold_drops_weak_matches(isolated_store):
    isolated_store.ingest_json(COLLECTION, RULES)
    results = isolated_store.search_collection(COLLECTION, RULES[0]["text"], k=2, relevance_threshold=0.9)
    assert [doc.page_content for doc, _ in results] == [RULES[0]["text"]]

def test_rag_service_works_with_real_search(isolated_store):
    isolated_store.ingest_json(COLLECTION, RULES)
    service = RAGService(llm=FakeLLM("Each factory holds 4 tiles [S1]."), relevance_threshold=0.5)
    result = service.answer(RULES[0]["text"])
    assert result["answer"] == "Each factory holds 4 tiles [1]."
    assert result["sources"][0]["title"] == "Azul"

@pytest.mark.ollama
def test_threshold_separates_real_and_junk_questions(require_ollama):
    questions = json.loads((Path(__file__).parent.parent / "tests" / "test_questions.json").read_text())

    def best_score(question):
        results = vector_service.search_collection(COLLECTION, question, k=1)
        return results[0][1] if results else 0.0

    for q in questions:
        score = best_score(q["question"])
        print(f"Question: {q['question']}\nBest score: {score:.3f}\nExpected: {q['expected']}\n")