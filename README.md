# 🚦 Opole Traffic ETL & Dashboard

Projekt inżynierski realizujący proces ETL (Extract, Transform, Load) do monitorowania płynności ruchu drogowego w Opolu z korelacją danych pogodowych. Zawiera interaktywny dashboard mapowy pozwalający sprawdzić natężenie ruchu w dowolnym punkcie miasta.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-green?logo=sqlite&logoColor=white)
![Leaflet](https://img.shields.io/badge/Map-Leaflet.js-199900?logo=leaflet&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-22%20passed-success?logo=pytest)
![Status](https://img.shields.io/badge/Status-Active-success)

## 📌 O projekcie

System automatycznie pobiera dane z dwóch niezależnych źródeł, przetwarza je i składuje w bazie danych SQLite. Dane są dostępne przez interaktywny dashboard mapowy w przeglądarce.

1. **TomTom Traffic API** – dane o prędkości i natężeniu ruchu w czasie rzeczywistym (REST API).
2. **TimeAndDate Scraping** – historyczne dane meteorologiczne (Web Scraping z walidacją proxy).

## 🚀 Kluczowe Funkcjonalności

### 🗺️ Interaktywny Dashboard
* **Mapa Opola** – kliknij dowolne miejsce na mapie, aby sprawdzić aktualny `jam_factor`.
* **Panel boczny** – wyświetla prędkość, limit prędkości (FFS), pewność pomiaru i historię ostatnich pomiarów.
* **Kolor w czasie rzeczywistym** – zielony (swobodny) → żółty → pomarańczowy → czerwony (korek).

### ⚙️ Architektura ETL
* **Feature Engineering** – autorski algorytm `jam_factor` (0–10) obliczany z surowych danych TomTom.
* **Resilience** – walidacja proxy przed użyciem, automatyczny fallback do połączenia bezpośredniego.
* **Backup & Retention** – automatyczne kopie zapasowe bazy co N cykli, polityka przechowywania ostatnich 5.
* **Security** – klucze API wyłącznie przez zmienne środowiskowe (`.env`), nigdy w kodzie.

### 🐳 Infrastruktura
* **Dockerized** – pełna konteneryzacja, powtarzalne środowisko.
* **Auto-Recovery** – polityka `restart: always` w Docker Compose.
* **Volume Persistence** – baza danych trwała poza cyklem życia kontenera.

### ✅ Testy
* 22 unit testy (pytest) pokrywające logikę `jam_factor`, parsowanie danych pogodowych i rotację backupów.

## 🛠️ Technologie

| Warstwa | Technologia |
|---|---|
| Język | Python 3.10+ |
| Web framework | Flask 3.1 |
| Mapa | Leaflet.js + OpenStreetMap |
| Baza danych | SQLite3 |
| ETL / Scraping | Requests, BeautifulSoup4 |
| Testy | pytest |
| Konteneryzacja | Docker, Docker Compose |
| Konfiguracja | python-dotenv |

## ⚙️ Instalacja i Uruchomienie

### Wymagania wstępne
* Python 3.10+ **lub** Docker Desktop.
* Darmowy klucz API TomTom → [developer.tomtom.com](https://developer.tomtom.com/).

---

### Opcja A: Lokalnie (zalecane do testów i developmentu)

#### 1. Klonowanie repozytorium
```bash
git clone https://github.com/MarcinJarema/Opole-Traffic-ETL.git
cd Opole-Traffic-ETL
```

#### 2. Środowisko wirtualne
```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
```

#### 3. Instalacja zależności
```bash
pip install -r requirements.txt
```

#### 4. Konfiguracja klucza API
Utwórz plik `.env` w głównym katalogu projektu:
```bash
TOMTOM_API_KEY=twoj_klucz_api_tutaj
```

#### 5. Uruchomienie dashboardu (mapa)
```bash
python app.py
```
Otwórz `http://localhost:8080` w przeglądarce.

#### 6. Uruchomienie pętli ETL (zbieranie danych co 15 min)
```bash
python main_loop.py
```
> Oba procesy możesz uruchomić równolegle w osobnych terminalach — ETL zapisuje dane do bazy, dashboard je odczytuje.

#### 7. Uruchomienie testów
```bash
python -m pytest tests/ -v
```

---

### Opcja B: Docker (ETL loop)

#### 1. Klonowanie i konfiguracja
```bash
git clone https://github.com/MarcinJarema/Opole-Traffic-ETL.git
cd Opole-Traffic-ETL
```
Utwórz plik `.env`:
```
TOMTOM_API_KEY=twoj_klucz_api_tutaj
```

#### 2. Uruchomienie
```bash
docker compose up -d
```

#### 3. Podgląd logów
```bash
docker compose logs -f
```

#### 4. Zatrzymanie
```bash
docker compose down
```

---

## 📂 Struktura Projektu

```
├── app.py               # Flask dashboard (API + serwowanie mapy)
├── main_loop.py         # Główna pętla ETL (zbieranie danych)
├── traffic_api.py       # Klient TomTom API + obliczanie jam_factor
├── weather_scraper.py   # Scraper danych pogodowych
├── history_weather_2024.py  # Runner scrapingu historycznego (cały rok)
├── config.py            # Konfiguracja globalna (punkty pomiarowe, URL-e)
├── db_utils.py          # Inicjalizacja i obsługa bazy SQLite
├── backup_utils.py      # Backupy z polityką retencji
├── logger_config.py     # Konfiguracja logowania (plik + konsola)
├── robots_checker.py    # Weryfikacja robots.txt przed scrapingiem
├── templates/
│   └── index.html       # Dashboard (Leaflet.js + panel boczny)
├── tests/               # Unit testy (pytest, 22 przypadków)
├── db/                  # Baza danych SQLite (traffic.db)
├── logs/                # Logi aplikacji
├── backups/             # Automatyczne kopie zapasowe
├── compose.yaml         # Konfiguracja Docker Compose
├── Dockerfile           # Obraz Docker
└── requirements.txt     # Zależności Python
```

## 🚧 Plany Rozwoju

* [x] Konteneryzacja aplikacji (Docker).
* [x] Interaktywny dashboard mapowy (Flask + Leaflet.js).
* [x] Unit testy (pytest).
* [ ] Migracja bazy danych na PostgreSQL.
* [ ] Wykres historyczny jam_factor na dashboardzie.
* [ ] Korelacja ruchu z danymi pogodowymi w panelu analitycznym.

---

### Autor: Marcin Jarema
