from fastapi import FastAPI
from contextlib import asynccontextmanager

# importy dla SQLite
from app.db.sqlite import database as sqlite_db
from app.db.sqlite import endpoints as sqlite_endpoints
from app.models import models_sqlite

# importy dla MongoDB
from app.db.mongodb import database as mongo_db
from app.db.mongodb import endpoints as mongo_endpoints

# importy dla PostgreSQL
from app.db.postgresql import database as postgres_db
from app.db.postgresql import endpoints as postgres_endpoints

# importy dla MySQL
from app.db.mysql import database as mysql_db
from app.db.mysql import endpoints as mysql_endpoints

# importy dla DuckDB
from app.db.duckdb import database as duckdb_db
from app.db.duckdb import endpoints as duckdb_endpoints

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("Inicjalizacja aplikacji...")
    # SQLite
    print("Inicjalizacja SQLite...")
    await sqlite_db.ini_base()
    print("SQLite gotowe")

    # PostgreSQL
    print("Inicjalizacja PostgreSQL...")
    await postgres_db.ini_base()
    print("PostgreSQL gotowe")

    # MySQL
    print("Inicjalizacja MySQL...")
    await mysql_db.ini_base()
    print("MySQL gotowe")

    # DuckDB
    print("Inicjalizacja DuckDB...")
    duckdb_db.ini_base()
    print("DuckDB gotowe")

    # MongoDB
    print("Inicjalizacja MongoDB...")
    await mongo_db.connect_to_mongo()
    await mongo_db.init_mongodb()
    print("MongoDB gotowe")
    yield
    # shutdown
    print("Zamykanie aplikacji...")
    mongo_db.close_mongo_connection()
    print("Aplikacja zamknięta")

'''
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup – otwórz połączenie z MongoDB
    print("Łączenie z MongoDB...")
    await mongo_db.connect_to_mongo()
    # indeksy zostały już utworzone przez init_db.py, więc init_mongodb() nie jest potrzebne
    print("MongoDB gotowe")
    
    yield
    
    # shutdown – zamknij połączenie
    print("Zamykanie połączenia z MongoDB...")
    mongo_db.close_mongo_connection()
'''
app = FastAPI(lifespan=lifespan)


app.include_router(sqlite_endpoints.router, prefix="/sqlite/notes", tags=["SQLite"])
app.include_router(mongo_endpoints.router, prefix="/mongodb/notes", tags=["MongoDB"])
app.include_router(postgres_endpoints.router, prefix="/postgresql/notes", tags=["PostgreSQL"])
app.include_router(mysql_endpoints.router, prefix="/mysql/notes", tags=["MySQL"])
app.include_router(duckdb_endpoints.router, prefix="/duckdb/notes", tags=["DuckDB"])

# Health check - sprawdza status aplikacji i połączeń z bazami danych
@app.get("/health", tags=["System"])
def health_check():
    return{
        "status": "ok", 
        "databases": {
            "sqlite": "active", 
            "mongodb": "active"
        }
    }

# strona główna API z listą dostępnych endpointów
@app.get("/", tags=["System"])
def root():
    return {
        "message": "Notes API - Zarządzanie notatkami",
        "version": "1.0.0",
        "endpoints": {
            "sqlite": {
                "base": "/sqlite/notes",
                "description": "SQLite - relacyjna baza danych"
            },
            "mongodb": {
                "base": "/mongodb/notes",
                "description": "MongoDB - dokumentowa baza danych"
            },
            "docs": {
                "swagger": "/docs",
                "redoc": "/redoc"
            }
        }
    }