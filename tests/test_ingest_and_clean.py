import scripts.ingest_and_clean as pipeline

def test_clean_removes_html_citations_and_links():
    raw = "<b>Azul</b> is a game.[1] See https://example.com now.[citation needed]"
    assert pipeline.clean_text_noise(raw) == "Azul is a game. See now."

def test_clean_converts_headers_and_drops_references():
    raw = "Intro\n== Gameplay ==\nTake tiles.\n=== Scoring ===\nScore points.\n== References ==\nJunk"
    cleaned = pipeline.clean_text_noise(raw)
    assert "## Gameplay" in cleaned and "### Scoring" in cleaned
    assert "References" not in cleaned and "Junk" not in cleaned

def test_bgg_lookup_falls_back_when_request_fails(monkeypatch):
    def offline(*args, **kwargs):
        raise ConnectionError("no internet")

    monkeypatch.setattr(pipeline.requests, "get", offline)
    assert pipeline.auto_lookup_bgg_metadata("Azul (board game)") == {"bgg_id": "N/A", "title": "Azul"}

def test_ingest_game_writes_raw_and_cleaned_files(monkeypatch, tmp_path):
    raw_text = "Azul is a tile game.\n== Gameplay ==\nTake tiles."
    monkeypatch.setattr(pipeline, "RAW_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "CLEANED_DIR", tmp_path)
    monkeypatch.setattr(pipeline, "search_wiki_article", lambda query: ("Azul (board game)", raw_text))
    monkeypatch.setattr(pipeline, "auto_lookup_bgg_metadata",
                        lambda name: {"bgg_id": "230802", "title": "Azul", "min_players": 2, "max_players": 4})

    pipeline.ingest_game_by_name("Azul")

    assert (tmp_path / "azul_raw.txt").read_text() == raw_text
    cleaned = (tmp_path / "azul.md").read_text()
    assert cleaned.startswith("# Azul\n")
    assert "- **Player Count:** 2 to 4 players" in cleaned
    assert "## Gameplay\nTake tiles." in cleaned