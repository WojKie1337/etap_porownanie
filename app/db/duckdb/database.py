import asyncio
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from app.models.models_duckdb import Base

write_lock = asyncio.Lock()

# url string z linkiem do bazy
URL = "duckdb:///./notes_duck.db"

engine = create_engine(URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ini_base():
    Base.metadata.create_all(bind=engine)
    print("DuckDB tabela utworzona")


async def init_db():
    await asyncio.to_thread(ini_base)