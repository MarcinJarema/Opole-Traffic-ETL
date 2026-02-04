# config.py

import os
from pathlib import Path
from dotenv import load_dotenv

"""
Moduł konfiguracyjny aplikacji.
Centralne miejsce zarządzania stałymi, ścieżkami oraz zmiennymi środowiskowymi.
"""

# 1. Ładowanie zmiennych środowiskowych (z pliku .env)
load_dotenv()

# --- KONFIGURACJA BAZY DANYCH ---
DB_DIR = Path("db")
DB_NAME = "traffic.db"
DB_PATH = DB_DIR / DB_NAME

# --- KONFIGURACJA LOKALIZACJI ---
CITY_NAME = "opole"
COUNTRY_SLUG = "poland"

# Punkty pomiarowe ruchu (szerokość, długość geograficzna)
TRAFFIC_POINTS = {
    "niemodlinska_most": (50.6691, 17.9073),        # ul. Niemodlińska – most na Odrze
    "ozimska_reymonta": (50.6685, 17.9375),         # ul. Ozimska / Reymonta – skrzyżowanie
    "wezel_opole_poludnie": (50.5323, 17.9180),     # węzeł Opole Południe – A4/DK45
}

# Wybór aktywnego punktu do monitorowania
ACTIVE_POINT_KEY = "ozimska_reymonta"
LAT_OP, LON_OP = TRAFFIC_POINTS[ACTIVE_POINT_KEY]

# --- KONFIGURACJA API (TOMTOM) ---
TOMTOM_API_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

# Pobranie klucza z bezpiecznego magazynu (.env)
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

# Walidacja krytyczna: Program nie może działać bez klucza
if not TOMTOM_API_KEY:
    raise ValueError(
        "CRITICAL ERROR: Brak klucza API TomTom! "
        "Upewnij się, że utworzyłeś plik .env i zdefiniowałeś w nim TOMTOM_API_KEY."
    )

# --- KONFIGURACJA SCRAPINGU POGODY ---
HISTORY_YEAR = 2024
WEATHER_BASE_URL = "https://www.timeanddate.com/weather"
WEATHER_HISTORY_URL = f"{WEATHER_BASE_URL}/{COUNTRY_SLUG}/{CITY_NAME}/historic"