# Week 2 - Action Item Extractor

This Week 2 project is a FastAPI + SQLite notes app that extracts action items from free-form notes using:
- a heuristic extractor (`/action-items/extract`)
- an Ollama LLM extractor (`/action-items/extract-llm`)

## Prerequisites

- Python `>=3.10`
- `uv` (https://docs.astral.sh/uv/)
- For LLM endpoint: local Ollama daemon and at least one pulled model

## Setup and Run

From repository root:

```bash
uv sync --group dev
uv run uvicorn week2.app.main:app --reload
```

Open:

- App UI: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## Ollama Configuration

The app resolves LLM model in this order:

1. `OLLAMA_MODEL` environment variable
2. fallback default: `llama3.1:8b`

Example:

```bash
export OLLAMA_MODEL=llama3.1:8b
ollama serve
```

If Ollama is unavailable or returns invalid output, `POST /action-items/extract-llm` responds with `503`.

## API Endpoints

### `POST /action-items/extract`
Extract action items using heuristic rules.

Request body:

```json
{
  "text": "- [ ] Set up database\nTODO: write tests",
  "save_note": true
}
```

Response body:

```json
{
  "note_id": 1,
  "items": [
    { "id": 1, "text": "Set up database" },
    { "id": 2, "text": "TODO: write tests" }
  ]
}
```

### `POST /action-items/extract-llm`
Extract action items with Ollama structured output. Same request/response shape as the heuristic endpoint.

### `GET /action-items`
List stored action items. Optional query: `note_id`.

### `POST /action-items/{action_item_id}/done`
Mark an action item done/undone.

Request body:

```json
{ "done": true }
```

### `POST /notes`
Create a note.

Request body:

```json
{ "content": "Meeting notes..." }
```

### `GET /notes`
List all notes (newest first).

### `GET /notes/{note_id}`
Get one note by id.

## Frontend Buttons

The home page (`week2/frontend/index.html`) exposes:

- `Extract`: calls heuristic endpoint
- `Extract LLM`: calls Ollama endpoint
- `List Notes`: fetches and displays notes from `GET /notes`

## Run Tests

From repository root:

```bash
uv run pytest week2/tests -q
```
