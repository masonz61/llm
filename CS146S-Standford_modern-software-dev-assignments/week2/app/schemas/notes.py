from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class CreateNoteRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    # Preserve prior behavior: missing `content` becomes "" (400), while null becomes "None".
    content: Any = ""


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str

