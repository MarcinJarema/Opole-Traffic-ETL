# 🚦 Opole Traffic ETL & Weather Analysis

Projekt inżynierski realizujący proces ETL (Extract, Transform, Load) do monitorowania płynności ruchu drogowego w Opolu i korelacji korków z warunkami pogodowymi. Aplikacja jest w pełni skonteneryzowana i gotowa do wdrożenia.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-green?logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success)

## 📌 O projekcie

System automatycznie pobiera dane z dwóch niezależnych źródeł, przetwarza je i składuje w bazie danych w celu późniejszej analizy analitycznej.
1.  **TomTom Traffic API** – pobieranie danych o prędkości i czasie przejazdu (REST API).
2.  **TimeAndDate Scraping** – pozyskiwanie danych meteorologicznych (Web Scraping z rotacją proxy).

## 🚀 Kluczowe Funkcjonalności

### 🐳 Infrastruktura i Deployment
* **Dockerized:** Aplikacja działa w izolowanym kontenerze, co gwarantuje powtarzalność środowiska (Infrastructure as Code).
* **Auto-Recovery:** Kontener skonfigurowany jest z polityką `restart: always` – automatycznie wstaje po awarii lub restarcie serwera.
* **Volume Persistence:** Dane (baza SQL) są mapowane na wolumen hosta, co zapewnia ich trwałość nawet po usunięciu kontenera.

### ⚙️ Architektura ETL
* **Resilience:** System posiada mechanizmy *Retry Policy* oraz *Proxy Rotation* dla scrapera, aby unikać blokad IP.
* **Security:** Wrażliwe dane (klucze API) są wstrzykiwane przez zmienne środowiskowe (`.env`).
* **Feature Engineering:** Autorski algorytm obliczania `jam_factor` (0-10) na podstawie surowych danych o przepływie ruchu.

## 🛠️ Technologie

* **Core:** Python 3.10+
* **Containerization:** Docker, Docker Compose
* **Database:** SQLite3
* **Libraries:** Requests, BeautifulSoup4, python-dotenv
* **Tools:** Git, VS Code

## ⚙️ Instalacja i Uruchomienie

### Wymagania wstępne
* Zainstalowany [Docker Desktop](https://www.docker.com/products/docker-desktop/) LUB Python 3.10+.
* Klucz API do serwisu TomTom (darmowy).

### 1. Klonowanie repozytorium
```bash
git clone [https://github.com/MarcinJarema/Opole-Traffic-ETL.git](https://github.com/MarcinJarema/Opole-Traffic-ETL.git)
cd Opole-Traffic-ETL
```
# Opcja A: Uruchomienie przez Docker (Zalecane)
Najprostsza metoda. Nie musisz instalować Pythona ani bibliotek u siebie.

### 1. Konfiguracja: Utwórz plik .env i wklej klucz API:
```bash
TOMTOM_API_KEY=twoj_klucz_api_wpisz_tutaj
```
### 2. Uruchomienie w tle:
```bash
docker compose up -d
```
### 3. Podgląd logów (opcjonalnie):
```bash
docker compose logs -f
```
### 4. Zatrzymanie:
```bash
docker compose down
```
# Opcja B: Uruchomienie lokalne (Python)
Dla celów deweloperskich (bez Dockera).

### 1. Konfiguracja środowiska wirtualnego
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
```

### 2. Instalacja zależności
```bash
pip install -r requirements.txt
```

### 3. Konfiguracja zmiennych środowiskowych
Utwórz plik .env w głównym katalogu (skopiuj z .env.example) i wprowadź swój klucz:
```bash
TOMTOM_API_KEY=twoj_klucz_api_tutaj
```

### 4. Uruchomienie
```bash
python main_loop.py
```
### 📂 Struktura Projektu
```
├── backups/             # Automatyczne kopie zapasowe DB
├── db/                  # Wolumen bazy danych (traffic.db)
├── logs/                # Logi aplikacji
├── compose.yaml         # Konfiguracja Docker Compose
├── Dockerfile           # Przepis na obraz Docker
├── .dockerignore        # Pliki ignorowane przez Dockera
├── main_loop.py         # Główny proces orkiestrujący
├── traffic_api.py       # Klient API TomTom
├── weather_scraper.py   # Moduł scrapujący
├── config.py            # Konfiguracja globalna
├── db_utils.py          # Obsługa bazy danych
└── requirements.txt     # Zależności Python
```

## 🚧 Plany Rozwoju (To-Do)
* [x] Konteneryzacja aplikacji (Docker).
* [ ] Dodanie wizualizacji danych (Dashboard w PowerBI / Streamlit).
* [ ] Migracja bazy danych na PostgreSQL.
* [ ] Dodanie testów jednostkowych (pytest).

### Autor: Marcin Jarema
