from __future__ import annotations

import sqlite3
from typing import List

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas.notes import CreateNoteRequest, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("")
def create_note(payload: CreateNoteRequest) -> NoteResponse:
    content = str(payload.content).strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")

    try:
        note_id = db.insert_note(content)
        note = db.get_note(note_id)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="database error") from e

    # `note` should not be None right after insert, but keep defensive checks.
    if note is None:
        raise HTTPException(status_code=500, detail="failed to load created note")

    return NoteResponse(id=note["id"], content=note["content"], created_at=note["created_at"])


@router.get("")
def list_all_notes() -> List[NoteResponse]:
    try:
        rows = db.list_notes()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="database error") from e

    return [
        NoteResponse(id=r["id"], content=r["content"], created_at=r["created_at"])
        for r in rows
    ]


@router.get("/{note_id}")
def get_single_note(note_id: int) -> NoteResponse:
    try:
        row = db.get_note(note_id)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="database error") from e

    if row is None:
        raise HTTPException(status_code=404, detail="note not found")

    return NoteResponse(id=row["id"], content=row["content"], created_at=row["created_at"])


