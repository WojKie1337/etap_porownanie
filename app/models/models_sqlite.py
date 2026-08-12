from .base import Base
from sqlalchemy import Column, Integer, String, Text

class Note(Base):
    __tablename__ = "notes"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    date = Column(String(50), nullable=False)