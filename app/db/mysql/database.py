from fastapi import APIRouter
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models.base import Base
import time
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

router = APIRouter()

# URL = "mysql+pymysql://user:password@localhost:3306/notes_db"
URL = "mysql+aiomysql://user:password@localhost:3306/notes_db"

# engine = create_engine(URL)
engine = create_async_engine(
    URL, 
    pool_size=5, 
    max_overflow=10, 
    pool_pre_ping=True, 
    pool_recycle=1800
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
        await conn.run_sync(Base.metadata.create_all)