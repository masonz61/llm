from __future__ import annotations

import sqlite3
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas.action_items import (
    ActionItemResponse,
    ExtractActionItemsRequest,
    ExtractActionItemsResponse,
    MarkActionItemDoneRequest,
    MarkActionItemDoneResponse,
)
from ..services.extract import ActionItemExtractionError, extract_action_items


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract")
def extract(payload: ExtractActionItemsRequest) -> ExtractActionItemsResponse:
    text = str(payload.text).strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(text)

    try:
        items = extract_action_items(text)
        ids = db.insert_action_items(items, note_id=note_id)
    except ActionItemExtractionError as e:
        # This should not happen for the heuristic extractor, but keeps behavior clear
        # if extraction is swapped to an LLM-based implementation.
        raise HTTPException(status_code=502, detail="failed to extract action items") from e
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="database error") from e

    return ExtractActionItemsResponse(
        note_id=note_id,
        items=[{"id": i, "text": t} for i, t in zip(ids, items)],
    )


@router.get("")
def list_all(note_id: Optional[int] = None) -> List[ActionItemResponse]:
    try:
        rows = db.list_action_items(note_id=note_id)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="database error") from e

    return [
        ActionItemResponse(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done")
def mark_done(
    action_item_id: int, payload: MarkActionItemDoneRequest
) -> MarkActionItemDoneResponse:
    done = bool(payload.done)
    try:
        db.mark_action_item_done(action_item_id, done)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="database error") from e

    return MarkActionItemDoneResponse(id=action_item_id, done=done)


