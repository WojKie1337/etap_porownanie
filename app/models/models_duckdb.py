from sqlalchemy import Column, Integer, String, Text, Sequence
from sqlalchemy.orm import declarative_base

# Osobny Base tylko dla DuckDB
Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer,Sequence('note_id_seq', start=1), primary_key=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    date = Column(String(50), nullable=False)