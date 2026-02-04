# backup_utils.py

import shutil
import logging
import os
from datetime import datetime
from pathlib import Path
from config import DB_PATH

BACKUP_DIR = Path("backups")
BACKUP_RETENTION_LIMIT = 5  # Liczba przechowywanych ostatnich kopii

def perform_backup() -> None:
    """
    Tworzy kopie zapasową bazy danych z unikalnym znacznikiem czasu.
    
    Implementuje politykę retencji (Retention Policy): przechowuje tylko
    określoną liczbę ostatnich kopii (zdefiniowaną w BACKUP_RETENTION_LIMIT),
    automatycznie usuwając najstarsze pliki, aby oszczędzać miejsce na dysku.
    """
    try:
        if not DB_PATH.exists():
            logging.warning("Backup anulowany: Brak pliku bazy danych.")
            return

        BACKUP_DIR.mkdir(exist_ok=True)
        
        # Generowanie nazwy pliku: traffic_backup_YYYY-MM-DD_HH-MM.db
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        backup_filename = f"traffic_backup_{timestamp}.db"
        destination = BACKUP_DIR / backup_filename
        
        # Kopiowanie z zachowaniem metadanych (copy2)
        shutil.copy2(DB_PATH, destination)
        logging.info(f"✅ Utworzono backup: {destination}")
        
        # --- Rotacja backupów (Retention Policy) ---
        # Pobierz listę plików .db i posortuj od najstarszego do najnowszego
        backups = sorted(BACKUP_DIR.glob("*.db"), key=os.path.getmtime)
        
        while len(backups) > BACKUP_RETENTION_LIMIT:
            oldest = backups.pop(0)
            try:
                oldest.unlink()
                logging.info(f"♻️  Rotacja: usunięto stary backup {oldest.name}")
            except OSError as e:
                logging.error(f"Nie udało się usunąć starego backupu {oldest.name}: {e}")

    except Exception as e:
        logging.error(f"Krytyczny błąd procesu backupu: {e}")