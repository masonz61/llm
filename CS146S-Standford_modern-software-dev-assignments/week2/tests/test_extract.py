import pytest

import json

from ..app.services.extract import ActionItemExtractionError, extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_bullet_list(monkeypatch):
    from ..app.services import extract as extract_module

    monkeypatch.setattr(extract_module, "_list_ollama_models", lambda: ["llama3:8b"])
    monkeypatch.setattr(
        extract_module,
        "_ollama_generate_text",
        lambda _model, _prompt: json.dumps(["Set up database", "Write tests", "write tests"]),
    )

    text = """
    Notes from meeting:
    - Set up database
    - Write tests
    """.strip()

    items = extract_action_items_llm(text)
    assert items == ["Set up database", "Write tests"]


def test_extract_action_items_llm_keyword_prefixed_lines(monkeypatch):
    from ..app.services import extract as extract_module

    monkeypatch.setattr(extract_module, "_list_ollama_models", lambda: ["llama3:8b"])
    monkeypatch.setattr(
        extract_module,
        "_ollama_generate_text",
        lambda _model, _prompt: json.dumps(
            ["Set up database", "Implement API extract endpoint", "Write tests"]
        ),
    )

    text = """
    todo: Set up database
    action: Implement API extract endpoint
    next: Write tests
    """.strip()

    items = extract_action_items_llm(text)
    assert items == ["Set up database", "Implement API extract endpoint", "Write tests"]


def test_extract_action_items_llm_empty_input_returns_empty_list():
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   ") == []


def test_extract_action_items_llm_malformed_llm_json_raises(monkeypatch):
    from ..app.services import extract as extract_module

    monkeypatch.setattr(extract_module, "_list_ollama_models", lambda: ["llama3:8b"])
    monkeypatch.setattr(extract_module, "_ollama_generate_text", lambda _model, _prompt: "not json")

    with pytest.raises(ActionItemExtractionError):
        extract_action_items_llm("Some note")
