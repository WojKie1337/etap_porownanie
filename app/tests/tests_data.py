# dane testowe dla testów obciążeniowych Locust
import random
from datetime import datetime, timedelta

# przykładowe tytuły notatek
TITLES = [
    "Zakupy spożywcze",
    "Lista zadań",
    "Spotkanie z klientem",
    "Pomysły na projekt",
    "Notatki ze szkolenia",
    "Plan wycieczki",
    "Przepis na obiad",
    "Budżet domowy",
    "Cele na miesiąc",
    "Kontakty ważne"
]

# przykładowe treści
BODIES = [
    "mleko, chleb, masło, jajka, ser",
    "Zadzwonić do klienta, napisać raport, zaktualizować dokumentację",
    "Omówić wymagania projektu, ustalić terminy",
    "Implementacja nowej funkcji, poprawa wydajności, refaktoring kodu",
    "MongoDB jest 10x szybsze od PostgreSQL w zapisach",
    "Kraków - Wawel, Rynek, Kazimierz - 3 dni",
    "Kurczak pieczony z ziemniakami i surówką",
    "Rachunki: 500 zł, zakupy: 800 zł, oszczędności: 200 zł",
    "Sport 3x w tygodniu, czytanie 30 min dziennie",
    "Jan Kowalski - 123-456-789, Anna Nowak - 987-654-321"
]

# generuje losową notatkę testową
def generate_random_note():
    return {
        "title": random.choice(TITLES), 
        "body": random.choice(BODIES), 
        "date": datetime.now().strftime("%d.%m.%y.")
    }

# generuje zaktualizowaną notatkę
def generate_updated_note():
    return {
        "title": f"[UPDATED] {random.choice(TITLES)}",
        "body": f"ZAKTUALIZOWANO: {random.choice(BODIES)}",
        "date": (datetime.now() + timedelta(days=1)).strftime("%d.%m.%y.")
    }