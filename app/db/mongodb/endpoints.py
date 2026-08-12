from fastapi import APIRouter, HTTPException, status, Depends, Response
from app.models import schemas
from app.db.mongodb.database import get_collection, COLLECTION_NAME
from bson import ObjectId
from typing import List

router = APIRouter()

# HELPER FUNCTION - konwertuje dokument mongodb na dict
def note_helper(note) -> dict:
    return {
        "_id": str(note["_id"]), 
        "title": note["title"], 
        "body": note["body"], 
        "date": note["date"],
    }

# pobierz wszystkie notatki
@router.get("/", tags=["MongoDB"], response_model=List[schemas.NoteMongoResponse])
async def get_all(skip: int = 0, limit: int = 100, collection = Depends(get_collection)):
    cursor = collection.find().skip(skip).limit(limit)
    notes = []

    async for note in cursor:
        notes.append(note_helper(note))
    return notes

# pobierz jedną notatkę
@router.get("/{id}", tags=["MongoDB"], response_model=schemas.NoteMongoResponse)
async def get_one(id: str, collection = Depends(get_collection)):
    # sprawdzenie czy id jest prawidłowym ObjectId
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nieprawidłowy format ID")

    note = await collection.find_one({"_id": ObjectId(id)})

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Notatka {id} nie została znaleziona")

    return note_helper(note)

# dodaj nową notatkę
@router.post("/", status_code=status.HTTP_201_CREATED, tags=["MongoDB"], response_model=schemas.NoteMongoResponse)
async def create_note(note: schemas.NoteBase, collection=Depends(get_collection)):
    # collection = get_collection()
    # konwersja pycantic model na dict
    note_dict = note.model_dump()
    # wstawienie do mongodb
    result = await collection.insert_one(note_dict)
    # pobranie utworzonej notatki
    new_note = await collection.find_one({"_id": result.inserted_id})
    return note_helper(new_note)

# aktualizowanie notatki
@router.put("/{id}", tags=["MongoDB"], response_model=schemas.NoteMongoResponse)
async def update_note(id: str, note: schemas.NoteBase, collection=Depends(get_collection)):
    # sprawdzenie czy id jest prawidłowym ObjectId
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nieprawidłowy format id")

    # collection = get_collection()

    # sprawdzenie czy notatka istnieje
    existing_note = await collection.find_one({"_id": ObjectId(id)})
    if not existing_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Notatka {id} nie została znaleiona")

    # aktualizuj
    note_dict = note.model_dump()
    await collection.update_one({"_id": ObjectId(id)}, {"$set": note_dict})
    # pobierz zaktualizowaną notatkę
    updated_note = await collection.find_one({"_id": ObjectId(id)})

    return note_helper(updated_note)

# usuwanie notatki
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["MongoDB"])
async def delete_note(id: str, collection=Depends(get_collection)):
    # sprawdzenie czy id jest prawidłowym ObjectId
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nieprawidłowy format id")

    # collection = get_collection()
    # sprawdzenie czy notatka istnieje
    existing_note = await collection.find_one({"_id": ObjectId(id)})
    if not existing_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Notatka o id {id} nie została znaleziona")

    # usunięcie
    await collection.delete_one({"_id": ObjectId(id)})
    return Response(status_code=status.HTTP_204_NO_CONTENT)