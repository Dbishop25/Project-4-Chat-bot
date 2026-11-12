import importlib
from pathlib import Path    

import dotenv
import pytest

import backend.core.config as config
from claude_tests.conftest import TEST_ENV

@pytest.fixture
def reload_config(monkeypatch):
    """Reload config.py with your real .env switched off."""
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    yield lambda: importlib.reload(config).settings
    monkeypatch.undo()
    importlib.reload(config)

def test_settings_are_read_correctly(reload_config):
    settings = reload_config()
    assert settings.rag_top_k == 5
    assert settings.rag_relevance_threshold == 0.5
    assert settings.frontend_origins == ["http://localhost:5173"]

def test_missing_setting_raises_clear_error(reload_config, monkeypatch):
    monkeypatch.delenv("RAG_TOP_K")
    with pytest.raises(ValueError, match="RAG_TOP_K"):
        reload_config()

def test_env_example_has_every_setting():
    lines = (Path(__file__).parent.parent / ".env.example").read_text().splitlines()
    keys = {line.split("=")[0] for line in lines if "=" in line and not line.startswith("#")}
    assert keys == set(TEST_ENV)