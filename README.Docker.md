# 🐳 Docker — Opole Traffic ETL

Instrukcja uruchamiania projektu przez Docker i Docker Compose.

## Wymagania

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (zawiera Docker Compose)
* Klucz API TomTom → [developer.tomtom.com](https://developer.tomtom.com/)

---

## Szybki start

### 1. Konfiguracja klucza API

Utwórz plik `.env` w głównym katalogu projektu:

```
TOMTOM_API_KEY=twoj_klucz_api_tutaj
```

### 2. Budowanie i uruchomienie

```bash
docker compose up --build -d
```

Kontener startuje pętlę ETL (`main_loop.py`), która co 15 minut pobiera dane o ruchu z TomTom API i zapisuje je do bazy SQLite.

### 3. Podgląd logów

```bash
docker compose logs -f
```

### 4. Zatrzymanie

```bash
docker compose down
```

---

## Trwałość danych

Baza danych (`db/traffic.db`) oraz logi (`logs/`) są montowane jako wolumeny hosta:

```yaml
volumes:
  - ./db:/app/db
```

Dane przetrwają restart i usunięcie kontenera. Backupy tworzone są automatycznie co 4 cykle ETL do katalogu `backups/`.

---

## Auto-restart

Kontener skonfigurowany z polityką `restart: always` — automatycznie wstaje po awarii lub restarcie systemu.

---

## Budowanie obrazu dla innej architektury (np. serwer amd64 na Mac M1/M2)

```bash
docker build --platform=linux/amd64 -t opole-traffic-etl .
```

## Publikacja obrazu do rejestru

```bash
docker build -t twoj-rejestr/opole-traffic-etl .
docker push twoj-rejestr/opole-traffic-etl
```

---

## Uwaga — dashboard mapowy

Aktualnie Docker uruchamia wyłącznie pętlę ETL. Dashboard mapowy (`app.py`, dostępny na `http://localhost:8080`) uruchamiany jest lokalnie:

```bash
source .venv/bin/activate
python app.py
```

Dashboard odczytuje dane z tej samej bazy co kontener Docker — oba mogą działać równolegle.
