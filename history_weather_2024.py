# history_weather_2024.py

import time
import random
import logging
from datetime import date, timedelta

from db_utils import init_db
from config import HISTORY_YEAR
from weather_scraper import scrape_day
from logger_config import setup_logging

def is_leap_year(year: int) -> bool:
    """Sprawdza, czy rok jest przestępny."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def scrape_year(year: int) -> None:
    """
    Pobiera dane historyczne dzień po dniu dla całego podanego roku.
    
    Proces uwzględnia losowe opóźnienia (Rate Limiting), aby uniknąć
    blokady ze strony serwera docelowego (Politeness Policy).
    """
    # Upewniamy się, że tabela istnieje przed startem
    init_db()

    start_date = date(year, 1, 1)
    days_in_year = 366 if is_leap_year(year) else 365
    
    logging.info(f"Rozpoczynanie scrapingu historycznego dla roku {year}. Liczba dni: {days_in_year}")

    for i in range(days_in_year):
        current_date = start_date + timedelta(days=i)
        
        # Zabezpieczenie przed wyjściem poza rok (np. przy błędnej kalkulacji)
        if current_date.year != year:
            break

        progress_msg = f"Przetwarzanie dnia {i + 1}/{days_in_year}: {current_date}"
        print(f"--- {progress_msg} ---")  # Print dla natychmiastowego podglądu w konsoli

        try:
            scrape_day(current_date)
        except Exception as e:
            # Logujemy błąd, ale nie przerywamy pętli (kontynuujemy następny dzień)
            logging.error(f"Nieudane pobieranie dla daty {current_date}: {e}")

        # --- Rate Limiting / Politeness Policy ---
        # Losowe opóźnienie (1-3s) symulujące zachowanie człowieka
        sleep_time = random.uniform(1, 3)
        time.sleep(sleep_time)

    logging.info(f"Zakończono pobieranie danych historycznych dla roku {year}.")

if __name__ == "__main__":
    # Konfiguracja loggera przed uruchomieniem procesu
    setup_logging()
    scrape_year(HISTORY_YEAR)