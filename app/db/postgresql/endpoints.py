# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException
from app.models import schemas, models_sqlite
from app.db.postgresql.database import get_db

router = APIRouter()

# endpointy
# pobierz wszystkie
# dodanie paginacji
@router.get("/", tags=["PostgreSQL"], response_model=list[schemas.NoteResponse])
async def get_all(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models_sqlite.Note).offset(skip).limit(limit)
    )
    # notes = db.query(models_sqlite.Note).offset(skip).limit(limit).all()
    # return notes
    return result.scalars().all()

# pobierz jeden
@router.get("/{id}", tags=["PostgreSQL"], response_model=schemas.NoteResponse)
async def get_one(id: int, db: AsyncSession = Depends(get_db)):
    # note = db.query(models_sqlite.Note).filter(models_sqlite.Note.id == id).first()
    result = await db.execute(
        select(models_sqlite.Note).where(models_sqlite.Note.id == id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail=f"Notatka {id} nie znaleziona")
    return note

# dodaj jeden
@router.post("/", status_code=201, tags=["PostgreSQL"], response_model=schemas.NoteResponse)
async def create_note(note: schemas.NoteBase, db: AsyncSession = Depends(get_db)):
    db_note = models_sqlite.Note(**note.model_dump()) # model pydantic a nie sqlalchemy
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note

# usuń jeden
@router.delete("/{id}", status_code=204, tags=["PostgreSQL"])
async def delete_note(id: int, db: AsyncSession = Depends(get_db)):
    # note  = db.get(models_sqlite.Note, id)
    result = await db.execute(
        select(models_sqlite.Note).where(models_sqlite.Note.id == id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Notatka nie znaleziona")
    await db.delete(note)
    await db.commit()


# modyfikacja notatki
@router.put("/{id}", response_model=schemas.NoteResponse)
async def update_note(id: int, note: schemas.NoteBase, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models_sqlite.Note).where(models_sqlite.Note.id == id)
    )
    # db_note = db.get(models_sqlite.Note, id)
    db_note = result.scalar_one_or_none()
    if not db_note:
        raise HTTPException(status_code=404, detail="Notatka nie została znaleziona")
    db_note.title = note.title
    db_note.body = note.body
    db_note.date = note.date

    await db.commit()
    await db.refresh(db_note)
    return db_note