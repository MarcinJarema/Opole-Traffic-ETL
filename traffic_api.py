# traffic_api.py

import requests
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from db_utils import get_connection
from config import TRAFFIC_POINTS, TOMTOM_API_URL, LAT_OP, LON_OP, TOMTOM_API_KEY

def fetch_current_traffic() -> List[Dict[str, Any]]:
    """
    Pobiera aktualne dane o płynności ruchu z API TomTom.
    
    Wykonuje zapytanie HTTP GET do endpointu Flow Segment Data.
    Oblicza autorski wskaźnik 'jam_factor' na podstawie różnicy
    między prędkością aktualną a swobodną (Free Flow Speed).
    """
    
    # Parametry zapytania zgodne z dokumentacją TomTom API
    params = {
        "point": f"{LAT_OP},{LON_OP}",
        "unit": "KMPH",     # Jednostka: km/h
        "key": TOMTOM_API_KEY,
    }

    try:
        # Timeout 10s zapobiega zawieszeniu aplikacji przy problemach z siecią
        resp = requests.get(TOMTOM_API_URL, params=params, timeout=10)
        resp.raise_for_status() # Rzuci wyjątek dla błędów 4xx/5xx
        
        data = resp.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Błąd komunikacji z API TomTom: {e}")
        return []

    # Parsowanie odpowiedzi JSON
    flow = data.get("flowSegmentData", {})
    
    # Pobieranie danych z bezpiecznymi wartościami domyślnymi
    speed = flow.get("currentSpeed")
    free_flow_speed = flow.get("freeFlowSpeed")
    confidence = flow.get("confidence", 0.0)

    # --- Feature Engineering: Jam Factor Calculation ---
    # Wzór: Im wolniej jedziemy względem normy, tym wyższy współczynnik (0-10)
    if free_flow_speed and free_flow_speed > 0:
        ratio = (speed or 0.1) / free_flow_speed
        jam_factor = 10.0 * max(0.0, 1.0 - ratio)
    else:
        jam_factor = 0.0

    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    record = {
        "timestamp": now_iso,
        "lat": LAT_OP,
        "lon": LON_OP,
        "speed": speed,
        "speed_limit": free_flow_speed,
        "jam_factor": jam_factor,
        "confidence": confidence,
        "provider": "tomtom_flow",
    }

    return [record]


def save_traffic(records: List[Dict[str, Any]]) -> None:
    """
    Transakcyjny zapis rekordów ruchu do bazy SQLite.
    """
    if not records:
        return

    conn = get_connection()
    try:
        cur = conn.cursor()
        
        query = """
            INSERT INTO traffic (
                timestamp, lat, lon, speed, speed_limit,
                jam_factor, confidence, provider
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        for r in records:
            cur.execute(query, (
                r["timestamp"], r["lat"], r["lon"],
                r["speed"], r["speed_limit"],
                r["jam_factor"], r["confidence"], r["provider"],
            ))

        conn.commit()
    except Exception as e:
        logging.error(f"Błąd zapisu do bazy danych: {e}")
        conn.rollback() # Wycofanie zmian w razie błędu
    finally:
        conn.close()