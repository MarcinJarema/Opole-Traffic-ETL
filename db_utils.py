# db_utils.py

import sqlite3
from pathlib import Path
from config import DB_PATH

def get_connection() -> sqlite3.Connection:
    """
    Ustanawia połączenie z bazą danych SQLite.
    
    Tworzy strukturę katalogów dla pliku bazy danych, jeśli ta jeszcze nie istnieje.
    """
    db_dir = DB_PATH.parent
    db_dir.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """
    Inicjalizuje schemat bazy danych (DDL).
    
    Tworzy tabele 'traffic' oraz 'weather' wraz z indeksami optymalizującymi
    wydajność zapytań (np. joinów po czasie), jeśli jeszcze nie istnieją.
    """
    conn = get_connection()
    cur = conn.cursor()

    # --- Tabela Traffic (Ruch drogowy) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,   -- Format: ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ)
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            speed REAL,
            speed_limit REAL,
            jam_factor REAL,           -- Obliczony współczynnik korka (0-10)
            confidence REAL,
            provider TEXT
        );
    """)

    # --- Tabela Weather (Dane pogodowe) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,   -- Format: ISO 8601 UTC
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            temperature_c REAL,
            weather_desc TEXT,
            wind_speed REAL,
            wind_dir TEXT,
            humidity REAL,
            pressure REAL,
            visibility REAL,
            source TEXT
        );
    """)

    # --- Indeksy (Performance Tuning) ---
    # Kluczowe dla szybkiego łączenia tabel (JOIN) po osi czasu
    cur.execute("CREATE INDEX IF NOT EXISTS idx_traffic_time ON traffic(timestamp);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_weather_time ON weather(timestamp);")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"✅ Baza danych zainicjalizowana poprawnie: {DB_PATH}")