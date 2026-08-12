import asyncio
from app.db.postgresql.database import ini_base as init_pg, engine as pg_engine
from app.db.mysql.database import ini_base as init_mysql, engine as mysql_engine
from app.db.sqlite.database import ini_base as init_sqlite, engine as sqlite_engine  # jeśli jest async
from app.db.duckdb.database import init_db as init_duckdb  # silnik synchroniczny – nie trzeba dispose
from app.db.mongodb.database import init_mongodb, connect_to_mongo, close_mongo_connection

async def main():
    print("Inicjalizacja baz danych...")
    await init_pg()
    await pg_engine.dispose()

    await init_mysql()
    await mysql_engine.dispose()

    # SQLite – jeśli używa async silnika
    await init_sqlite()
    await sqlite_engine.dispose()

    await init_duckdb()  # DuckDB jest synchroniczny – pomijamy dispose

    await connect_to_mongo()
    await init_mongodb()
    close_mongo_connection()

    print("Wszystkie bazy gotowe.")

if __name__ == "__main__":
    asyncio.run(main())