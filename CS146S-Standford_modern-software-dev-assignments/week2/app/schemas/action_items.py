from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class ExtractActionItemsRequest(BaseModel):
    """
    Request payload for `POST /action-items/extract`.

    Uses `Any` for fields to preserve prior truthiness/coercion behavior as much as possible.
    """

    model_config = ConfigDict(extra="allow")

    text: Any = ""
    save_note: Any = None


class ExtractActionItemsItem(BaseModel):
    id: int
    text: str


class ExtractActionItemsResponse(BaseModel):
    note_id: Optional[int]
    items: List[ExtractActionItemsItem]


class ActionItemResponse(BaseModel):
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str


class MarkActionItemDoneRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    # Preserve prior behavior where missing `done` defaults to `True`,
    # and non-boolean values are coerced using Python truthiness.
    done: Any = True


class MarkActionItemDoneResponse(BaseModel):
    id: int
    done: bool

