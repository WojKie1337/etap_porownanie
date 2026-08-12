# from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# url połączenia z mongodb
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "notes_db"
COLLECTION_NAME = "notes"

# globalna zmienna dla klienta
# client: Optional[MongoClient] = None
client: Optional[AsyncIOMotorClient] = None

# zwraca instancję bazy danych
async def get_database():
    return client[DATABASE_NAME]

# zwraca kolekcję notes
async def get_collection():
    db = await get_database()
    return db[COLLECTION_NAME]

# inicjalizuje połączenie z mongodb przy starcie aplikacji
async def connect_to_mongo():
    global client
    print("Łączenie z MongoDB...")
    # client = MongoClient(MONGODB_URL)
    client = AsyncIOMotorClient(MONGODB_URL)

    # test połączenia
    try:
        await client.admin.command('ping')
        print("Połączono z MongoDB")
    except Exception as e:
        print("Błąd połączenia z MongoDB: ", e)
        raise

# zamknięcie połączenia z MongoDB
def close_mongo_connection():
    global client
    if client:
        print("Zamykanie połączenia z MongoDB...")
        client.close()
        print("Połączenie zamknięte")

# inicjalizacja bazy danych - tworzy indeksy
async def init_mongodb():
    db = client[DATABASE_NAME]
    # collection = get_collection()
    collection = db[COLLECTION_NAME]
    # opcjonalne utworzenie indeksów
    await collection.create_index("title")
    print("Indeksy utworzone w kolekcji ", COLLECTION_NAME)