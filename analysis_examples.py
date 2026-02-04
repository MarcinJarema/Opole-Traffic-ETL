# analysis_examples.py

import sqlite3
from db_utils import get_connection

def avg_jam_factor_by_temp_bucket() -> None:
    """
    Analizuje zależność między temperaturą a natężeniem ruchu (Jam Factor).
    
    Wykonuje agregację danych z tabel 'traffic' i 'weather', grupując wyniki
    w przedziały temperaturowe (kubełki) w celu znalezienia korelacji.
    """
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT
            -- Kategoryzacja temperatury (Bucketing) dla celów analitycznych
            CASE
                WHEN w.temperature_c IS NULL THEN 'brak danych'
                WHEN w.temperature_c < 0 THEN '< 0°C'
                WHEN w.temperature_c BETWEEN 0 AND 10 THEN '0–10°C'
                WHEN w.temperature_c BETWEEN 10 AND 20 THEN '10–20°C'
                ELSE '> 20°C'
            END AS temp_bucket,
            AVG(t.jam_factor) AS avg_jam,
            COUNT(t.id) as count_records
        FROM traffic t
        LEFT JOIN weather w
          -- Łączenie rekordów po wspólnej godzinie (format ISO: YYYY-MM-DDTHH)
          ON substr(t.timestamp, 1, 13) = substr(w.timestamp, 1, 13)
        WHERE w.temperature_c IS NOT NULL
        GROUP BY temp_bucket
        ORDER BY avg_jam DESC;
    """

    try:
        cur.execute(query)
        rows = cur.fetchall()
        
        # Wyświetlanie wyników w formie tabelarycznej
        print(f"{'Kategoria Temp':<15} | {'Średni Korek':<20} | {'Liczba próbek'}")
        print("-" * 55)
        for temp_bucket, avg_jam, count in rows:
            print(f"{temp_bucket:<15} | {avg_jam:<20.4f} | {count}")
            
    except sqlite3.Error as e:
        print(f"Błąd wykonywania zapytania analitycznego: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    avg_jam_factor_by_temp_bucket()