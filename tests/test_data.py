import json
from pathlib import Path
import pytest

ROOT = Path(__file__).parent.parent
CLEANED = sorted((ROOT / "data" / "cleaned").glob("*.md"))
QUESTIONS = json.loads((ROOT / "tests" / "test_questions.json").read_text())

def test_every_cleaned_file_has_title_and_sections():
    assert CLEANED, "data/cleaned is empty"
    for path in CLEANED:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("# "), path.name
        assert "\n## " in text, path.name