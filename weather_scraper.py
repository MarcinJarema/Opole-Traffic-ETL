# weather_scraper.py

import logging
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import List, Dict, Optional, Any

from db_utils import get_connection
from config import CITY_NAME, COUNTRY_SLUG, LAT_OP, LON_OP
from robots_checker import is_scraping_allowed

BASE_URL = "https://www.timeanddate.com/weather"

# User-Agent identyfikujący naszego bota (dobra praktyka etyczna)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ProjektOpoleBot/1.0; +https://github.com/twoj-nick/projekt)"
}

# Lista serwerów proxy do rotacji IP (zapobieganie blokadom).
# W środowisku produkcyjnym ta lista powinna pochodzić z płatnego API lub zmiennych środowiskowych.
PROXY_LIST = [
    "http://20.210.113.32:8123",
    "http://186.121.235.66:8080",
]

def _is_proxy_alive(proxy_url: str) -> bool:
    """Sprawdza czy proxy odpowiada w ciągu 3 sekund."""
    try:
        proxies = {"http": proxy_url, "https": proxy_url}
        requests.head("https://www.timeanddate.com", proxies=proxies, timeout=3)
        return True
    except Exception:
        logging.debug(f"Proxy nieosiągalne: {proxy_url}")
        return False


def get_random_proxy() -> Dict[str, str]:
    """Losuje działający serwer proxy z puli. Zwraca pusty dict gdy żaden nie działa."""
    working = [p for p in PROXY_LIST if _is_proxy_alive(p)]
    if not working:
        logging.warning("Żadne proxy z listy nie odpowiada — użyję połączenia bezpośredniego.")
        return {}
    proxy_url = random.choice(working)
    return {"http": proxy_url, "https": proxy_url}


def build_day_url(d: date) -> str:
    """Generuje URL do historycznych danych pogodowych dla konkretnej daty."""
    return (
        f"{BASE_URL}/{COUNTRY_SLUG}/{CITY_NAME}"
        f"/historic?month={d.month}&year={d.year}&hd={d.year}{d.month:02d}{d.day:02d}"
    )


def fetch_day_html(d: date) -> Optional[str]:
    """
    Pobiera kod HTML strony z danymi historycznymi.
    
    Implementuje wzorzec 'Resilience':
    1. Sprawdza robots.txt.
    2. Próbuje połączenia przez losowe Proxy.
    3. W razie błędu (Fallback), próbuje połączenia bezpośredniego.
    """
    url = build_day_url(d)
    
    # Krok 1: Weryfikacja etyczna (Robots Exclusion Protocol)
    if not is_scraping_allowed(url, HEADERS["User-Agent"]):
        logging.warning(f"⛔ Scraping zablokowany przez robots.txt dla: {url}")
        return None

    # Krok 2: Próba połączenia przez Proxy (anonimizacja)
    try:
        proxy = get_random_proxy()
        # Timeout 5s dla proxy (szybka weryfikacja czy działa)
        resp = requests.get(url, headers=HEADERS, proxies=proxy, timeout=5)
        resp.raise_for_status()
        return resp.text
    except Exception:
        # Krok 3: Fallback - połączenie bezpośrednie (Direct Connection)
        # Używane, gdy proxy zawiedzie. Dłuższy timeout (20s).
        try:
            logging.info(f"Proxy failed for {url}. Switching to direct connection...")
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return resp.text
        except Exception as e2:
            logging.error(f"❌ Krytyczny błąd pobierania {url}: {e2}")
            return None


def parse_float(text: str) -> Optional[float]:
    """
    Normalizuje dane tekstowe do formatu liczbowego (float).
    Usuwa jednostki, znaki specjalne i zamienia przecinki na kropki.
    Przykład: '14,5 °C' -> 14.5
    """
    text = text.strip()
    if not text:
        return None
    
    cleaned = ""
    for ch in text:
        if ch.isdigit() or ch in ",.-":
            cleaned += ch
        elif cleaned and ch == " ":
            # Przerywamy po napotkaniu spacji po liczbie (np. "14 C")
            break
            
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_weather_table(html: str, d: date) -> List[Dict[str, Any]]:
    """
    Parsuje tabelę HTML (id='wt-his') i ekstrahuje dane pogodowe.
    
    Mapowanie kolumn (wg struktury timeanddate.com):
    [1] Temp, [2] Opis, [3] Wiatr, [4] Wilgotność, [5] Ciśnienie, [6] Widoczność.
    """
    if not html:
        return []
        
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="wt-his")
    
    # Fallback: szukanie po nagłówkach, jeśli ID tabeli się zmieniło
    if table is None:
        for t in soup.find_all("table"):
            header = t.find("tr")
            if header and "Temp" in header.get_text():
                table = t
                break

    if table is None:
        logging.warning("Nie znaleziono tabeli z danymi pogodowymi.")
        return []

    records: List[Dict[str, Any]] = []
    rows = table.find_all("tr")

    # Pomijamy pierwszy wiersz (nagłówek)
    for row in rows[1:]:
        cols = row.find_all("td")
        time_col = row.find("th")
        
        # Walidacja struktury wiersza (wymagane min. 7 kolumn danych)
        if not time_col or len(cols) < 7:
            continue

        # Ekstrakcja danych (indeksy przesunięte o 1 przez ikonę w kolumnie 0)
        try:
            temp_txt = cols[1].get_text(" ", strip=True)
            weather_desc = cols[2].get_text(" ", strip=True)
            wind_txt = cols[3].get_text(" ", strip=True)
            hum_txt = cols[4].get_text(" ", strip=True)
            press_txt = cols[5].get_text(" ", strip=True)
            vis_txt = cols[6].get_text(" ", strip=True)

            # Parsowanie czasu
            time_txt = time_col.get_text(" ", strip=True)
            time_part = time_txt.split()[0] # np. "00:00"
            
            dt_local = datetime.strptime(f"{d.isoformat()} {time_part}", "%Y-%m-%d %H:%M")
            timestamp_iso = dt_local.isoformat(timespec="minutes") + "Z"

            record = {
                "timestamp": timestamp_iso,
                "lat": LAT_OP,
                "lon": LON_OP,
                "temperature_c": parse_float(temp_txt),
                "weather_desc": weather_desc,
                "wind_speed": parse_float(wind_txt),
                "humidity": parse_float(hum_txt),
                "pressure": parse_float(press_txt),
                "visibility": parse_float(vis_txt),
                "source": "timeanddate_html",
                "wind_dir": "" # Brak danych o kierunku w tej tabeli (wymagałoby analizy ikony)
            }
            records.append(record)
        except Exception as e:
            logging.warning(f"Błąd parsowania wiersza: {e}")
            continue

    return records


def save_weather_records(records: List[Dict[str, Any]]) -> None:
    """
    Idempotentny zapis rekordów pogodowych do bazy danych.
    Sprawdza istnienie rekordu przed wstawieniem (unikaty po timestamp).
    """
    if not records:
        return

    conn = get_connection()
    try:
        cur = conn.cursor()

        for r in records:
            # Sprawdzenie duplikatów
            cur.execute("SELECT 1 FROM weather WHERE timestamp = ? LIMIT 1", (r["timestamp"],))
            if cur.fetchone():
                continue

            cur.execute("""
                INSERT INTO weather (
                    timestamp, lat, lon, temperature_c, weather_desc, 
                    wind_speed, humidity, pressure, visibility, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r["timestamp"], r["lat"], r["lon"], r["temperature_c"], r["weather_desc"],
                r["wind_speed"], r["humidity"], r["pressure"], r["visibility"], r["source"]
            ))

        conn.commit()
    except Exception as e:
        logging.error(f"Błąd zapisu danych pogodowych: {e}")
    finally:
        conn.close()


def scrape_day(d: date) -> None:
    """
    Główna funkcja procesu ETL dla danych pogodowych (Extract -> Transform -> Load).
    """
    html = fetch_day_html(d)
    if html:
        records = parse_weather_table(html, d)
        save_weather_records(records)
        logging.info(f"📅 {d}: Pomyślnie przetworzono {len(records)} rekordów pogodowych.")
    else:
        logging.warning(f"📅 {d}: Brak danych HTML do przetworzenia.")


if __name__ == "__main__":
    # Test manualny modułu
    from db_utils import init_db  
    
    logging.basicConfig(level=logging.INFO)
    init_db() 
    
    # Test dla konkretnej daty
    test_d = date(2024, 5, 2)
    print(f"Rozpoczynanie testu scrapingu dla: {test_d}")
    scrape_day(test_d)