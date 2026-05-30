# main_loop.py

import time
import logging
from typing import List, Dict
from dotenv import load_dotenv

# Wczytanie zmiennych środowiskowych (bezpieczeństwo)
load_dotenv()

# Importy modułów wewnętrznych
from db_utils import init_db
from traffic_api import fetch_current_traffic, save_traffic
from logger_config import setup_logging
from backup_utils import perform_backup 

# --- KONFIGURACJA ---
# Częstotliwość pętli w sekundach (np. 900s = 15 min).
# Ustawione na 1s dla celów demonstracyjnych/testowych.
CHECK_INTERVAL_SECONDS = 900

# Próg natężenia ruchu (0-10), powyżej którego logujemy ostrzeżenie
JAM_ALERT_THRESHOLD = 8.0

# Co ile cykli wykonywać backup (np. co 4 cykle = co 1h przy interwale 15min)
BACKUP_EVERY_N_CYCLES = 4


def check_for_alerts(traffic_data: List[Dict]) -> None:
    """
    Analizuje pobrane dane pod kątem anomalii (silne korki).
    
    Jeśli 'jam_factor' przekroczy zdefiniowany próg, funkcja generuje
    log poziomu WARNING oraz wyświetla komunikat operatorowi.
    """
    for record in traffic_data:
        jam = record.get("jam_factor", 0.0)
        loc = f"({record['lat']}, {record['lon']})"
        
        if jam >= JAM_ALERT_THRESHOLD:
            msg = f"⚠️ ALERT: Wykryto duży zator {loc}! Poziom: {jam:.2f}"
            logging.warning(msg)
            print(msg) 
        else:
            logging.info(f"Ruch w normie {loc}. Jam Factor: {jam:.2f}")


def main() -> None:
    """
    Główna funkcja orkiestrująca proces ETL.
    Uruchamia pętlę nieskończoną, która cyklicznie pobiera dane,
    zapisuje je do bazy i zarządza backupami.
    """
    # 1. Konfiguracja logowania
    setup_logging()
    
    # 2. Inicjalizacja struktury bazy danych
    init_db()
    
    logging.info(f"Uruchomiono serwis monitoringu. Interwał: {CHECK_INTERVAL_SECONDS}s")
    print("🚀 System wystartował. Logi w katalogu /logs. Naciśnij Ctrl+C, aby zatrzymać.")
    
    cycle_count = 0 

    try:
        while True:
            logging.info("--- START CYKLU ETL ---")
            
            # KROK 1: Extract & Load (Pobranie i zapis)
            traffic_recs = fetch_current_traffic()
            
            if traffic_recs:
                save_traffic(traffic_recs)
                logging.info(f"Zapisano {len(traffic_recs)} nowych rekordów ruchu.")
                
                # KROK 2: Analiza w czasie rzeczywistym
                check_for_alerts(traffic_recs)
            else:
                logging.warning("Brak danych z API w bieżącym cyklu.")

            # KROK 3: Maintenance (Backupy)
            cycle_count += 1
            if cycle_count >= BACKUP_EVERY_N_CYCLES:
                logging.info("Uruchamianie zaplanowanego backupu bazy danych...")
                perform_backup()
                cycle_count = 0 

            # Oczekiwanie na kolejny cykl
            logging.info(f"Uśpienie procesu na {CHECK_INTERVAL_SECONDS}s...")
            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        # Graceful Shutdown - bezpieczne zamknięcie
        print("\n")
        logging.info("Otrzymano sygnał zatrzymania (SIGINT).")
        
        logging.info("Tworzenie backupu bezpieczeństwa przed zamknięciem...")
        perform_backup()
        
        logging.info("Program zakończył pracę poprawnie.")
        print("👋 Do widzenia!")

if __name__ == "__main__":
    main()