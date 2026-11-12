import pytest

from backend.services.retrieval_service import ABSTENTION, RAGService, RAGServiceError
from claude_tests.conftest import AZUL, FakeLLM


# RAGService Tests

def test_blank_question(make_service):
    service, _, _ = make_service()
    with pytest.raises(ValueError):
        service.answer("  ")

def test_weak_matches_are_ignored(make_service):
    service, _, llm = make_service(matches=[(AZUL, 0.4)])  # threshold is 0.5
    assert service.answer("tiles?") == {"answer": ABSTENTION, "sources": []}
    assert llm.prompts == []  # the LLM is never asked

def test_answer_includes_cited_source(make_service):
    service, _, _ = make_service()
    result = service.answer("tiles?")
    assert result["answer"] == "Each factory holds 4 tiles [1]."
    assert result["sources"] == [{"title": "Azul Rules", "content": AZUL.page_content, "page": 3}]

def test_ungrounded_reply_is_refused(make_service, reply):
    service, _, _ = make_service(replies=(reply,))
    assert service.answer("tiles?") == {"answer": ABSTENTION, "sources": []}

def test_follow_up_question_uses_history(make_service):
    service, retriever, llm = make_service(replies=(
        "Each factory holds 4 tiles [S1].",  # answer to question 1
        "azul tiles two players",            # question 2 rewritten as a search
        "Still 4 tiles [S1].",               # answer to question 2
    ))
    service.answer("How many tiles per factory?", session_id="s1")
    service.answer("And for 2 players?", session_id="s1")
    assert "How many tiles per factory?" in llm.prompts[1]
    assert retriever.calls[1]["query"] == "azul tiles two players"

# Session Tests

def test_sessions_are_kept_separate(make_service):
    service, _, llm = make_service()
    service.answer("Azul question", session_id="alice")
    service.answer("Dominion question", session_id="bob")
    assert "Azul question" not in llm.prompts[1]

def test_failure_raises_rag_service_error(make_service):
    service, retriever, _ = make_service()
    retriever.error = RuntimeError("chroma is down")
    with pytest.raises(RAGServiceError):
        service.answer("tiles?")

# LLM Tests

RULE = [{
    "id": "azul_1",
    "text": "Each factory holds 4 tiles.",
    "metadata": {"title": "Azul Rules", "page": 3} 
}]



        import pytest

from backend.services.retrieval_service import ABSTENTION, RAGService, RAGServiceError
from tests.conftest import AZUL, FakeLLM


# RAGService Tests

def test_blank_question(make_service):
    service, _, _ = make_service()
    with pytest.raises(ValueError):
        service.answer("  ")

def test_weak_matches_are_ignored(make_service):
    service, _, llm = make_service(matches=[(AZUL, 0.4)])  # threshold is 0.5
    assert service.answer("tiles?") == {"answer": ABSTENTION, "sources": []}
    assert llm.prompts == []  # the LLM is never asked

def test_answer_includes_cited_source(make_service):
    service, _, _ = make_service()
    result = service.answer("tiles?")
    assert result["answer"] == "Each factory holds 4 tiles [1]."
    assert result["sources"] == [{"title": "Azul Rules", "content": AZUL.page_content, "page": 3}]

@pytest.mark.parametrize("reply", [
    "Each factory holds 4 tiles.",
    "I will not answer that question.",
])
def test_ungrounded_reply_is_refused(make_service, reply):
    service, _, _ = make_service(replies=(reply,))
    assert service.answer("tiles?") == {"answer": ABSTENTION, "sources": []}

def test_follow_up_question_uses_history(make_service):
    service, retriever, llm = make_service(replies=(
        "Each factory holds 4 tiles [S1].",  # answer to question 1
        "azul tiles two players",            # question 2 rewritten as a search
        "Still 4 tiles [S1].",               # answer to question 2
    ))
    service.answer("How many tiles per factory?", session_id="s1")
    service.answer("And for 2 players?", session_id="s1")
    assert "How many tiles per factory?" in llm.prompts[1]
    assert retriever.calls[1]["query"] == "azul tiles two players"

# Session Tests

def test_sessions_are_kept_separate(make_service):
    service, _, llm = make_service()
    service.answer("Azul question", session_id="alice")
    service.answer("Dominion question", session_id="bob")
    assert "Azul question" not in llm.prompts[1]

def test_failure_raises_rag_service_error(make_service):
    service, retriever, _ = make_service()
    retriever.error = RuntimeError("chroma is down")
    with pytest.raises(RAGServiceError):
        service.answer("tiles?")

# LLM Tests

RULE = [{
    "id": "azul_1",
    "text": "Each factory holds 4 tiles.",
    "metadata": {"title": "Azul Rules", "page": 3} 
}]



        