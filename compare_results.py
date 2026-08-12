import pandas as pd
import re
import matplotlib.pyplot as plt

bazy = {
    "PostgreSQL": "results_postgresql_stats.csv",
    "MySQL": "results_mysql_stats.csv",
    "SQLite": "results_sqlite_stats.csv",
    "DuckDB": "results_duckdb_stats.csv",
    "MongoDB": "results_mongodb_stats.csv",
}

# wczytanie wszystkich plików
frames = []
for nazwa, plik in bazy.items():
    try:
        df = pd.read_csv(plik)
        df["Baza"] = nazwa
        frames.append(df)
    except FileNotFoundError:
        print(f"Plik {plik} nie istnieje, pomijam")

if not frames:
    print("Brak plików do porównania")
    exit()

df = pd.concat(frames)

# wyodrębnienie typu operacji z nazwy endpointu
def extract_operation(name):
    # szuka ostatniego wystąpienia nawiasów kwadratowych z typem
    match = re.search(r'\[([A-Z\s]+)\]', name)
    if not match:
        return "OTHER"
    op = match.group(1).strip()
    if 'GET' in op:
        return 'GET'
    elif 'CREATE' in op:
        return 'CREATE'
    elif 'UPDATE' in op:
        return 'UPDATE'
    elif 'DELETE' in op:
        return 'DELETE'
    return 'OTHER'

df['Operation'] = df['Name'].apply(extract_operation)

# przygotowanie danych - średni czas odpowiedzi per operacja i baza
avg_times = pd.pivot_table(
    df, 
    values='Average Response Time', 
    index='Operation', 
    columns='Baza', 
    aggfunc='mean'
)

# błędy
failures = pd.pivot_table(
    df, 
    values="Failure Count", 
    index="Operation", 
    columns="Baza", 
    aggfunc="sum"
)

# lista operacji do narysowania (tylko te które występują)
operacje = ['GET', 'CREATE', 'UPDATE', 'DELETE']
kolory = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# --- Wykres 1: Średni czas odpowiedzi ---
fig1, ax1 = plt.subplots()        # poprawione: tylko jeden wykres
x = range(len(operacje))
width = 0.15

for i, baza in enumerate(avg_times.columns):
    heights = []
    for op in operacje:
        if op in avg_times.index and baza in avg_times.columns:
            heights.append(avg_times.loc[op, baza])
        else:
            heights.append(0)
    ax1.bar([xi + i*width for xi in x], heights, width, label=baza, color=kolory[i % len(kolory)])

ax1.set_xlabel('Typ operacji')
ax1.set_ylabel('Średni czas odpowiedzi (ms)')
ax1.set_title('Średni czas odpowiedzi – porównanie baz')
ax1.set_xticks([xi + width*2 for xi in x])
ax1.set_xticklabels(operacje)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.7)
fig1.tight_layout()
fig1.savefig('czasy_odpowiedzi.png', dpi=150)
plt.close(fig1)

# --- Wykres 2: Liczba błędów ---
fig2, ax2 = plt.subplots()        # poprawione
for i, baza in enumerate(failures.columns):
    heights = []
    for op in operacje:
        if op in failures.index and baza in failures.columns:
            heights.append(failures.loc[op, baza])
        else:
            heights.append(0)
    ax2.bar([xi + i*width for xi in x], heights, width, label=baza, color=kolory[i % len(kolory)])

ax2.set_xlabel('Typ operacji')
ax2.set_ylabel('Liczba błędów')
ax2.set_title('Liczba błędów – porównanie baz')
ax2.set_xticks([xi + width*2 for xi in x])
ax2.set_xticklabels(operacje)
ax2.legend()
ax2.grid(axis='y', linestyle='--', alpha=0.7)
fig2.tight_layout()
fig2.savefig('liczba_bledow.png', dpi=150)
plt.close(fig2)

print("Wykresy zapisano: czasy_odpowiedzi.png, liczba_bledow.png")