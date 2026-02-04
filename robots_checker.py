# robots_checker.py

import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

def is_scraping_allowed(target_url: str, user_agent: str = "*") -> bool:
    """
    Weryfikuje zgodność scrapowania z protokołem Robots Exclusion Protocol (robots.txt).
    
    Parsuje plik robots.txt domeny docelowej i sprawdza, czy dany User-Agent
    ma prawo pobrać zasób pod wskazanym adresem URL.
    """
    try:
        parsed_url = urlparse(target_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"

        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        
        allowed = rp.can_fetch(user_agent, target_url)
        
        if not allowed:
            logging.warning(f"⛔ Blokada robots.txt dla URL: {target_url}")
            
        return allowed

    except Exception as e:
        # Strategia Fail-Open: W razie błędu (np. brak pliku robots.txt lub timeout),
        # zakładamy, że scraping jest dozwolony, ale logujemy problem.
        logging.warning(f"Nie udało się sprawdzić robots.txt ({e}). Zakładam zgodę.")
        return True 

if __name__ == "__main__":
    # Szybki test manualny
    test_url = "https://www.timeanddate.com/weather/poland/opole/historic"
    print(f"Czy mogę pobierać {test_url}? -> {is_scraping_allowed(test_url)}")