from __future__ import annotations

import os
import re
import json
import subprocess
from typing import Any, List
from dotenv import load_dotenv
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


class ActionItemExtractionError(RuntimeError):
    """Service-layer error for LLM-based action item extraction failures."""


_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_OLLAMA_FALLBACK_MODEL = os.getenv("OLLAMA_FALLBACK_MODEL", "llama3:8b")

# Ordered by preference; the first available model from `ollama list` wins.
_OLLAMA_PREFERRED_MODELS: list[str] = [
    "llama3.1:8b",
    "llama3:8b",
    "qwen2.5:7b",
    "mistral:7b",
    "llama2:7b",
]


def _list_ollama_models() -> list[str]:
    """List available Ollama models via `ollama list`. """
    try:
        proc = subprocess.run(
            ["ollama", "list"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as e:
        # `ollama` binary missing or not on PATH.
        raise ActionItemExtractionError(
            "Ollama is not available. Ensure the `ollama` CLI is installed and on PATH."
        ) from e

    if proc.returncode != 0:
        raise ActionItemExtractionError(
            f"`ollama list` failed with exit code {proc.returncode}: {proc.stderr.strip()}"
        )

    models: list[str] = []
    for line in proc.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Expected output table header includes `NAME ...`.
        if stripped.lower().startswith("name "):
            continue
        token = stripped.split()[0] if stripped else ""
        if token and token.lower() != "name":
            models.append(token)

    # Preserve order but dedupe.
    seen: set[str] = set()
    unique: list[str] = []
    for m in models:
        key = m.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(m)

    return unique


def _select_ollama_model(available_models: list[str]) -> str:
    """Select a model name using preferred models and a local fallback."""
    available_lower = {m.lower(): m for m in available_models}

    for preferred in _OLLAMA_PREFERRED_MODELS:
        if preferred.lower() in available_lower:
            return available_lower[preferred.lower()]

    if _OLLAMA_FALLBACK_MODEL.lower() in available_lower:
        return available_lower[_OLLAMA_FALLBACK_MODEL.lower()]

    if available_models:
        return available_models[0]

    # Last resort: still use the local fallback model name.
    return _OLLAMA_FALLBACK_MODEL


def _ollama_generate_text(model: str, prompt: str, *, timeout_s: int = 60) -> str:
    """Generate raw text from Ollama's local HTTP API."""
    url = _OLLAMA_BASE_URL.rstrip("/") + "/api/generate"
    body: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        # Keep output deterministic-ish for validation.
        "options": {"temperature": 0},
    }

    req = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=timeout_s) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        raise ActionItemExtractionError(
            f"Ollama generate failed (HTTP {e.code}): {e.read().decode('utf-8', errors='ignore')}"
        ) from e
    except URLError as e:
        raise ActionItemExtractionError(f"Ollama generate failed: {e}") from e

    response_text = str(payload.get("response", "")).strip()
    if not response_text:
        raise ActionItemExtractionError("Ollama returned an empty response.")

    return response_text


def _extract_json_array_candidate(raw_response: str) -> str:
    """Extract a JSON array substring from the raw model response."""
    text = raw_response.strip()
    if text.startswith("[") and text.endswith("]"):
        return text

    match = re.search(r"\[[\s\S]*?\]", text)
    if not match:
        raise ActionItemExtractionError("Ollama output did not contain a JSON array.")
    return match.group(0)


def _parse_json_array_of_strings(json_array: str) -> list[str]:
    """Parse and validate a JSON array of strings."""
    try:
        parsed = json.loads(json_array)
    except json.JSONDecodeError as e:
        raise ActionItemExtractionError(
            f"Ollama output contained malformed JSON: {e}"
        ) from e

    if not isinstance(parsed, list):
        raise ActionItemExtractionError("Ollama JSON was not an array.")

    items: list[str] = []
    for idx, item in enumerate(parsed):
        if not isinstance(item, str):
            raise ActionItemExtractionError(
                f"Ollama JSON array element {idx} was not a string."
            )
        items.append(item)

    return items


def _normalize_action_items(items: list[str]) -> list[str]:
    """Normalize candidate strings into clean action item text."""
    normalized: list[str] = []
    for item in items:
        cleaned = item.strip()
        # Strip common list markers accidentally returned inside strings.
        cleaned = BULLET_PREFIX_PATTERN.sub("", cleaned).strip()
        cleaned = cleaned.removeprefix("[ ]").strip()
        cleaned = cleaned.removeprefix("[todo]").strip()
        if cleaned:
            normalized.append(cleaned)
    return normalized


def _dedupe_action_items(items: list[str]) -> list[str]:
    """Deduplicate action items while preserving order (case-insensitive)."""
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items from `text` using a local Ollama model.

    Returns a clean, deduplicated list of action items (case-insensitive),
    or raises `ActionItemExtractionError` on Ollama failure/malformed output.
    """
    if not text or not str(text).strip():
        return []

    model = _select_ollama_model(_list_ollama_models())

    prompt = f"""
You extract actionable tasks from notes.
Return ONLY a valid JSON array of strings. No markdown, no commentary.
Rules:
- Each string is one short action item (imperative phrase).
- If there are no action items, return [] exactly.

User text:
{text}
""".strip()

    raw_response = _ollama_generate_text(model, prompt)
    json_candidate = _extract_json_array_candidate(raw_response)
    parsed_items = _parse_json_array_of_strings(json_candidate)
    normalized = _normalize_action_items(parsed_items)
    return _dedupe_action_items(normalized)
