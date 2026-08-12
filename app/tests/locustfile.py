# testy obciążeniowe Locust dla SQLite i MongoDB
"""
Uruchomienie:
1. SQLite:  locust -f app/tests/locustfile.py --tags sqlite
2. MongoDB: locust -f app/tests/locustfile.py --tags mongodb
3. Oba:     locust -f app/tests/locustfile.py
4. Oba na porcie: locust -f app/tests/locustfile.py --host http://localhost:8000
# 5000 użytkowników, czas narastania 50/s, czas testu 100 sekund
5. PostgreSQL: locust -f app/tests/locustfile.py --host http://localhost:8000 --tags postgresql --headless -u 5000 -r 50 --run-time 100s --csv=results_postgresql
6. MySQL: locust -f app/tests/locustfile.py --host http://localhost:8000 --tags mysql --headless -u 5000 -r 50 --run-time 100s --csv=results_mysql
7. SQLite: locust -f app/tests/locustfile.py --host http://localhost:8000 --tags sqlite --headless -u 5000 -r 50 --run-time 100s --csv=results_sqlite
8. DuckDB: locust -f app/tests/locustfile.py --host http://localhost:8000 --tags duckdb --headless -u 5000 -r 50 --run-time 100s --csv=results_duckdb
9. MongoDB: locust -f app/tests/locustfile.py --host http://localhost:8000 --tags mongodb --headless -u 5000 -r 50 --run-time 100s --csv=results_mongodb
"""
from locust import HttpUser, task, between, tag
from tests_data import generate_random_note, generate_updated_note
import random

# --- SQLITE ---

class SQLiteUser(HttpUser):
    # testy dla SQLite API
    wait_time = between(1, 3) # czekaj 1-3 sekundy między requestami
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.timeout = 30
    # lista utworzonych ID (dos testów GET/PUT/DELETE)
    def on_start(self):
        self.created_ids = []

    @task(10) # waga 10 - najczęstsza operacja
    @tag("sqlite", "read")
    def get_all_notes_sqlite(self):
        # GET /sqlite/notes/ - pobierz wszystkie notatki
        with self.client.get(
            "/sqlite/notes/", 
            params={"skip": 0, "limit": 100}, 
            catch_response=True, 
            name="/sqlite/notes/ [GET ALL]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(5) # waga 5
    @tag("sqlite", "read")
    def get_one_note_sqlite(self):
        # GET /sqlite/notes/{id} - pobierz jedną notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.get(
            f"/sqlite/notes/{note_id}", 
            catch_response=True, 
            name="/sqlite/notes/{id} [GET ONE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # notatka została usunięta - usuń z listy
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(8) # waga 8
    @tag("sqlite", "write")
    def create_note_sqlite(self):
        # POST /sqlite/notes/ - utwórz notatkę
        note = generate_random_note()
        with self.client.post(
            "/sqlite/notes/", 
            json=note, 
            catch_response=True, 
            name="/sqlite/notes/ [CREATE]"
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_ids.append(data["id"])
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(3) # waga 3
    @tag("sqlite", "write")
    def update_note_sqlite(self):
        # PUT /sqlite/notes/{id} - zaktualizuj notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        updated_note = generate_updated_note()

        with self.client.put(
            f"/sqlite/notes/{note_id}", 
            json=updated_note, 
            catch_response=True, 
            name="/sqlite/notes/{id} [UPDATE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(2) # waga 2 - najmniej częsta operacja
    @tag("sqlite", "write")
    def delete_note_sqlite(self):
        # DELETE /sqlite/notes/{id} - usuń notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.delete(
            f"/sqlite/notes/{note_id}", 
            catch_response=True, 
            name="/sqlite/notes/{id} [DELETE]"
        ) as response:
            if response.status_code == 204:
                self.created_ids.remove(note_id)
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

# --- MONGODB ---

class MongoDBUser(HttpUser):
    # testy dla MongoDB API
    wait_time = between(1, 3)
    # lista utworzonych id (MongoDB używa ObjectId string)
    def on_start(self):
        self.created_ids = []

    @task(10)
    @tag("mongodb", "read")
    def get_all_notes_mongodb(self):
        # GET /mongodb/notes/ - pobierz wszystkie notatki
        with self.client.get(
            "/mongodb/notes/", 
            params={"skip": 0, "limit": 100}, 
            catch_response=True, 
            name="/mongodb/notes/ [GET ALL]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(5)
    @tag("mongodb", "read")
    def get_one_note_mongodb(self):
        # GET /mongodb/notes/{id} - pobierz jedną notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.get(
            f"/mongodb/notes/{note_id}", 
            catch_response=True, 
            name="/mongodb/notes/{id} [GET ONE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(8)
    @tag("mongodb", "write")
    def create_note_mongodb(self):
        # POST /mongodb/notes/ - utwórz notatkę
        note = generate_random_note()
        with self.client.post(
            "/mongodb/notes/", 
            json=note, 
            catch_response=True, 
            name="/mongodb/notes/ [CREATE]"
        ) as response:
            if response.status_code == 201: # COŚ TU JEST NIE TAK
                data = response.json()
                note_id = data.get("id")
                if note_id is None:
                    note_id = data.get("_id")
                if note_id is None or note_id == "":
                    response.failure("Brak id/_id w odpowiedzi CREATE")
                else:
                    self.created_ids.append(note_id)
                    response.success()
            else:
                response.failure(f"Błąd {response.status_code}")


    @task(3)
    @tag("mongodb", "write")
    def update_note_mongodb(self):
        # PUT /mongodb/notes/{id} - zaktualizuj notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        updated_note = generate_updated_note()

        with self.client.put(
            f"/mongodb/notes/{note_id}", 
            json=updated_note, 
            catch_response=True, 
            name="/mongodb/notes/{id} [UPDATE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")


    @task(2)
    @tag("mongodb", "write")
    def delete_note_mongodb(self):
        # DELETE /mongodb/notes/{id} - usuń notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.delete(
            f"/mongodb/notes/{note_id}", 
            catch_response=True, 
            name="/mongodb/notes/{id} [DELETE]"
        )as response:
            if response.status_code == 204:
                self.created_ids.remove(note_id)
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")


# --- POSTGRESQL ---

class PostgreSQLUser(HttpUser):
    # testy dla postgresql API
    wait_time = between(1, 3) # czekaj 1-3 sekundy między requestami
    # lista utworzonych ID (dos testów GET/PUT/DELETE)
    def on_start(self):
        self.created_ids = []

    @task(10) # waga 10 - najczęstsza operacja
    @tag("postgresql", "read")
    def get_all_notes_postgresql(self):
        # GET /postgresql/notes/ - pobierz wszystkie notatki
        with self.client.get(
            "/postgresql/notes/", 
            params={"skip": 0, "limit": 100}, 
            catch_response=True, 
            name="/postgresql/notes/ [GET ALL]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(5) # waga 5
    @tag("postgresql", "read")
    def get_one_note_postgresql(self):
        # GET /postgresql/notes/{id} - pobierz jedną notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.get(
            f"/postgresql/notes/{note_id}", 
            catch_response=True, 
            name="/postgresql/notes/{id} [GET ONE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # notatka została usunięta - usuń z listy
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(8) # waga 8
    @tag("postgresql", "write")
    def create_note_postgresql(self):
        # POST /postgresql/notes/ - utwórz notatkę
        note = generate_random_note()
        with self.client.post(
            "/postgresql/notes/", 
            json=note, 
            catch_response=True, 
            name="/postgresql/notes/ [CREATE]"
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_ids.append(data["id"])
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(3) # waga 3
    @tag("postgresql", "write")
    def update_note_postgresql(self):
        # PUT /postgresql/notes/{id} - zaktualizuj notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        updated_note = generate_updated_note()

        with self.client.put(
            f"/postgresql/notes/{note_id}", 
            json=updated_note, 
            catch_response=True, 
            name="/postgresql/notes/{id} [UPDATE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(2) # waga 2 - najmniej częsta operacja
    @tag("postgresql", "write")
    def delete_note_postgresql(self):
        # DELETE /postgresql/notes/{id} - usuń notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.delete(
            f"/postgresql/notes/{note_id}", 
            catch_response=True, 
            name="/postgresql/notes/{id} [DELETE]"
        ) as response:
            if response.status_code == 204:
                self.created_ids.remove(note_id)
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")


# --- MYSQL ---

class MySQLUser(HttpUser):
    # testy dla mysql API
    wait_time = between(1, 3) # czekaj 1-3 sekundy między requestami
    # lista utworzonych ID (dos testów GET/PUT/DELETE)
    def on_start(self):
        self.created_ids = []

    @task(10) # waga 10 - najczęstsza operacja
    @tag("mysql", "read")
    def get_all_notes_mysql(self):
        # GET /mysql/notes/ - pobierz wszystkie notatki
        with self.client.get(
            "/mysql/notes/", 
            params={"skip": 0, "limit": 100}, 
            catch_response=True, 
            name="/mysql/notes/ [GET ALL]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(5) # waga 5
    @tag("mysql", "read")
    def get_one_note_mysql(self):
        # GET /mysql/notes/{id} - pobierz jedną notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.get(
            f"/mysql/notes/{note_id}", 
            catch_response=True, 
            name="/mysql/notes/{id} [GET ONE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # notatka została usunięta - usuń z listy
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(8) # waga 8
    @tag("mysql", "write")
    def create_note_mysql(self):
        # POST /mysql/notes/ - utwórz notatkę
        note = generate_random_note()
        with self.client.post(
            "/mysql/notes/", 
            json=note, 
            catch_response=True, 
            name="/mysql/notes/ [CREATE]"
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_ids.append(data["id"])
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(3) # waga 3
    @tag("mysql", "write")
    def update_note_mysql(self):
        # PUT /mysql/notes/{id} - zaktualizuj notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        updated_note = generate_updated_note()

        with self.client.put(
            f"/mysql/notes/{note_id}", 
            json=updated_note, 
            catch_response=True, 
            name="/mysql/notes/{id} [UPDATE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(2) # waga 2 - najmniej częsta operacja
    @tag("mysql", "write")
    def delete_note_mysql(self):
        # DELETE /mysql/notes/{id} - usuń notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.delete(
            f"/mysql/notes/{note_id}", 
            catch_response=True, 
            name="/mysql/notes/{id} [DELETE]"
        ) as response:
            if response.status_code == 204:
                self.created_ids.remove(note_id)
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")


# --- DUCKDB ---

class DuckDBUser(HttpUser):
    # testy dla duckdb API
    wait_time = between(1, 3) # czekaj 1-3 sekundy między requestami
    # lista utworzonych ID (dos testów GET/PUT/DELETE)
    def on_start(self):
        self.created_ids = []

    @task(10) # waga 10 - najczęstsza operacja
    @tag("duckdb", "read")
    def get_all_notes_duckdb(self):
        # GET /duckdb/notes/ - pobierz wszystkie notatki
        with self.client.get(
            "/duckdb/notes/", 
            params={"skip": 0, "limit": 100}, 
            catch_response=True, 
            name="/duckdb/notes/ [GET ALL]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(5) # waga 5
    @tag("duckdb", "read")
    def get_one_note_duckdb(self):
        # GET /duckdb/notes/{id} - pobierz jedną notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.get(
            f"/duckdb/notes/{note_id}", 
            catch_response=True, 
            name="/duckdb/notes/{id} [GET ONE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # notatka została usunięta - usuń z listy
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(8) # waga 8
    @tag("duckdb", "write")
    def create_note_duckdb(self):
        # POST /duckdb/notes/ - utwórz notatkę
        note = generate_random_note()
        with self.client.post(
            "/duckdb/notes/", 
            json=note, 
            catch_response=True, 
            name="/duckdb/notes/ [CREATE]"
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_ids.append(data["id"])
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(3) # waga 3
    @tag("duckdb", "write")
    def update_note_duckdb(self):
        # PUT /duckdb/notes/{id} - zaktualizuj notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        updated_note = generate_updated_note()

        with self.client.put(
            f"/duckdb/notes/{note_id}", 
            json=updated_note, 
            catch_response=True, 
            name="/duckdb/notes/{id} [UPDATE]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")

    @task(2) # waga 2 - najmniej częsta operacja
    @tag("duckdb", "write")
    def delete_note_duckdb(self):
        # DELETE /duckdb/notes/{id} - usuń notatkę
        if not self.created_ids:
            return

        note_id = random.choice(self.created_ids)
        with self.client.delete(
            f"/duckdb/notes/{note_id}", 
            catch_response=True, 
            name="/duckdb/notes/{id} [DELETE]"
        ) as response:
            if response.status_code == 204:
                self.created_ids.remove(note_id)
                response.success()
            elif response.status_code == 404:
                self.created_ids.remove(note_id)
                response.success()
            else:
                response.failure(f"Błąd {response.status_code}")
