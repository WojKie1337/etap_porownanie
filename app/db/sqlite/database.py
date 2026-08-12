from fastapi import APIRouter
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from app.models.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# router
router = APIRouter()

# url string z linkiem do bazy
# URL = "sqlite:///./notes.db" # synchronicznie
URL = "sqlite+aiosqlite:///./notes.db" # asynchronicznie

# engine = create_engine(URL)
engine = create_async_engine(
    URL, 
    connect_args={
        "check_same_thread": False, 
        "timeout": 10,
    }
    )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session



# def ini_base():
#     Base.metadata.create_all(bind=engine) # tworzenie bazy

async def ini_base():
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.run_sync(Base.metadata.create_all)