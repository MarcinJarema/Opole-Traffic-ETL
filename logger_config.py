# logger_config.py

import logging
from pathlib import Path

def setup_logging() -> None:
    """
    Konfiguruje globalny system logowania aplikacji.
    
    Logi są kierowane dwutorowo (Dual Logging):
    1. Do pliku (logs/app.log) - w celu archiwizacji i późniejszej analizy.
    2. Na konsolę (stdout) - dla bieżącego podglądu działania aplikacji.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",  # Czysty format daty bez milisekund
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )