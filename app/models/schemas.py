from pydantic import BaseModel, Field, ConfigDict


class NoteBase(BaseModel):
    title: str
    body: str
    date: str # zobaczyć czy nie date

class NoteResponse(NoteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class NoteMongoResponse(NoteBase):
    id: str = Field(alias="_id", serialization_alias="id")

    model_config = ConfigDict(
        populate_by_name=True, 
        from_attributes=True
    )