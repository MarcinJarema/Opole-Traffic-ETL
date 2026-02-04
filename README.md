# 🚦 Opole Traffic ETL & Weather Analysis

Projekt inżynierski stworzony w celu nauki procesów ETL. Aplikacja monitoruje korki w Opolu.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

## 📌 O projekcie

System służy do budowania historycznej bazy danych o ruchu drogowym, aby wykrywać anomalie i badać wpływ pogody na korki. Aplikacja integruje dane z dwóch niezależnych źródeł:
1.  **TomTom Traffic API** – pobieranie danych o prędkości i czasie przejazdu (REST API).
2.  **TimeAndDate Scraping** – pozyskiwanie danych meteorologicznych (Web Scraping z rotacją proxy).

Dane są normalizowane, walidowane i składowane w relacyjnej bazie danych **SQLite**, co umożliwia późniejszą analizę analityczną (np. SQL/Pandas).

## 🚀 Kluczowe Funkcjonalności

### 🛡️ Bezpieczeństwo i Konfiguracja
* **Environment Variables:** Wrażliwe dane (klucze API) są izolowane w pliku `.env` i nie trafiają do repozytorium.
* **Config Management:** Centralny moduł `config.py` waliduje obecność kluczy przy starcie aplikacji (Fail-Fast).

### ⚙️ Architektura ETL
* **Extract:** Hybrydowe podejście – oficjalne API dla ruchu drogowego oraz Scraping dla pogody.
* **Transform:**
    * **Feature Engineering:** Autorski algorytm obliczania `jam_factor` (współczynnik korka 0-10) na podstawie `freeFlowSpeed`.
    * **Data Normalization:** Konwersja jednostek i czyszczenie danych tekstowych ze scrapingu.
* **Load:** Transakcyjny zapis do bazy SQLite z obsługą duplikatów (Idempotency).

### 🔧 Resilience & Reliability (Niezawodność)
* **Proxy Rotation:** System losowania serwerów proxy dla scrapera pogodowego w celu uniknięcia blokad IP.
* **Politeness Policy:** Przestrzeganie zasad `robots.txt` oraz losowe opóźnienia między zapytaniami.
* **Error Handling:** Strategie *Retry* i *Fallback* (przełączanie na połączenie bezpośrednie w razie awarii proxy).
* **Logging:** Szczegółowe logowanie zdarzeń do pliku `logs/app.log` oraz na konsolę.

### 💾 Backup & Retention
* Automatyczne tworzenie kopii zapasowych bazy danych.
* **Retention Policy:** Mechanizm rotacji utrzymujący tylko 5 ostatnich kopii (oszczędność miejsca).

## 🛠️ Technologie

* **Python 3.10+**
* **SQLite3** (Baza danych)
* **Requests** (Komunikacja HTTP)
* **BeautifulSoup4** (Parsing HTML)
* **Python-Dotenv** (Zarządzanie sekretem)

## ⚙️ Instalacja i Uruchomienie

### 1. Klonowanie repozytorium
```bash
git clone [https://github.com/MarcinJarema/Opole-Traffic-ETL.git](https://github.com/MarcinJarema/Opole-Traffic-ETL.git)
cd Opole-Traffic-ETL
```

### 2. Konfiguracja środowiska wirtualnego
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
```

### 3. Instalacja zależności
```bash
pip install -r requirements.txt
```

### 4. Konfiguracja zmiennych środowiskowych
Utwórz plik .env w głównym katalogu (skopiuj z .env.example) i wprowadź swój klucz:
```bash
TOMTOM_API_KEY=twoj_klucz_api_tutaj
```

### 5. Uruchomienie
```bash
python main_loop.py
```
### 📂 Struktura Projektu
```
├── backups/             # Automatyczne kopie zapasowe DB
├── db/                  # Plik bazy danych (traffic.db)
├── logs/                # Logi operacyjne
├── main_loop.py         # Główny proces orkiestrujący ETL
├── traffic_api.py       # Klient API TomTom
├── weather_scraper.py   # Moduł scrapujący z obsługą Proxy
├── config.py            # Konfiguracja globalna
├── db_utils.py          # Inicjalizacja schematu bazy (DDL)
├── analysis_examples.py # Przykładowe analizy SQL
└── robots_checker.py    # Walidator zgodności z robots.txt
```

## 🚧 Plany Rozwoju (To-Do)
* [ ] Dodanie wizualizacji danych (wykresy w bibliotece Matplotlib/Seaborn).
* [ ] Przeniesienie bazy danych z SQLite na PostgreSQL (dla lepszej wydajności).
* [ ] Konteneryzacja aplikacji (Docker).
