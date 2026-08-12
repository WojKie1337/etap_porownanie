from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.models import schemas, models_duckdb
from app.db.duckdb.database import get_db, write_lock

router = APIRouter()

# --- Helper: funkcja synchroniczna do pobierania wszystkich notatek ---
def _get_all(db: Session, skip: int, limit: int):
    return db.query(models_duckdb.Note).offset(skip).limit(limit).all()

# endpointy
# pobierz wszystkie
# dodanie paginacji
@router.get("/", tags=["DuckDB"], response_model=list[schemas.NoteResponse])
async def get_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # notes = db.query(models_duckdb.Note).offset(skip).limit(limit).all()
    # return notes
    return await run_in_threadpool(_get_all, db, skip, limit)

# pobierz jeden
def _get_one(db: Session, id: int):
    note = db.query(models_duckdb.Note).filter(models_duckdb.Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail=f"Notatka {id} nie znaleziona")
    return note

@router.get("/{id}", tags=["DuckDB"], response_model=schemas.NoteResponse)
async def get_one(id: int, db: Session = Depends(get_db)):
    return await run_in_threadpool(_get_one, db, id)

# dodaj jeden
def _create_note(db: Session, note: schemas.NoteBase):
    db_note = models_duckdb.Note(**note.model_dump()) # model pydantic a nie sqlalchemy
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.post("/", status_code=201, tags=["DuckDB"], response_model=schemas.NoteResponse)
async def create_note(note: schemas.NoteBase, db: Session = Depends(get_db)):
    async with write_lock:
        return await run_in_threadpool(_create_note, db, note)

# usuń jeden
def _delete_note(db: Session, id: int):
    note  = db.get(models_duckdb.Note, id)
    if not note:
        raise HTTPException(status_code=404, detail="Notatka nie znaleziona")
    db.delete(note)
    db.commit()

@router.delete("/{id}", status_code=204, tags=["DuckDB"])
async def delete_note(id: int, db: Session = Depends(get_db)):
    async with write_lock:
        await run_in_threadpool(_delete_note, db, id)
    from fastapi.responses import Response
    return Response(status_code=204)


# modyfikacja notatki
def _update_note(db: Session, note_id: int, note: schemas.NoteBase):
    db_note = db.get(models_duckdb.Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Notatka nie została znaleziona")
    db_note.title = note.title
    db_note.body = note.body
    db_note.date = note.date

    db.commit()
    db.refresh(db_note)
    return db_note

@router.put("/{id}", response_model=schemas.NoteResponse)
async def update_note(id: int, note: schemas.NoteBase, db: Session = Depends(get_db)):
    async with write_lock:
        return await run_in_threadpool(_update_note, db, id, note)