# Pokenizer API

Eine FastAPI-basierte API zum Durchsuchen und Verwalten von Pokémon-Sammelkarten.

## Funktionen

-   Durchsuchen von Pokémon-Karten, -Sets und -Künstlern.
-   Verwalten der persönlichen Kartensammlung.
-   Erstellen und Verwalten von benutzerdefinierten Listen.
-   Benutzerverwaltung und Authentifizierung (falls implementiert).
-   Automatische API-Dokumentation über Swagger UI und ReDoc.

## Technologie-Stack

-   **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
-   **Datenbank:** [PostgreSQL](https://www.postgresql.org/)
-   **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
-   **Datenvalidierung:** [Pydantic](https://pydantic-docs.helpmanual.io/)
-   **Server:** [Uvicorn](https://www.uvicorn.org/)
-   **Abhängigkeiten:** psycopg2, tqdm

## Setup und Installation

Folgen Sie diesen Schritten, um das Projekt lokal auszuführen.

### 1. Klonen des Repositories

```bash
git clone <repository-url>
cd pokenizer_api
```

### 2. Python Virtual Environment

Erstellen und aktivieren Sie eine virtuelle Umgebung.

```bash
# Für Windows
python -m venv venv
.\venv\Scripts\activate

# Für macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Abhängigkeiten installieren

Installieren Sie alle erforderlichen Pakete mit pip.

```bash
pip install -r requirements.txt
```

### 4. Datenbank-Setup

Dieses Projekt verwendet eine PostgreSQL-Datenbank.

1.  Stellen Sie sicher, dass Sie einen laufenden PostgreSQL-Server haben.
2.  Erstellen Sie eine neue, leere Datenbank (z. B. mit dem Namen `pokemon_api`).
3.  Öffnen Sie die Datei `ingest_data.py` und passen Sie die folgenden Konfigurationswerte an Ihre Datenbankumgebung an:

    ```python
    # ingest_data.py

    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "ultrasicherespasswort" # Ersetzen Sie dies mit Ihrem Passwort
    POSTGRES_HOST = "192.168.2.173"
    POSTGRES_PORT = "5432"
    POSTGRES_DB = "pokemon_api" # Der Name Ihrer Datenbank
    ```

### 5. Daten importieren

Führen Sie das Skript `ingest_data.py` aus, um die Datenbank mit den Pokémon-Kartendaten aus dem `/data`-Verzeichnis zu befüllen. Dieser Vorgang kann einige Minuten dauern.

**Wichtiger Hinweis:** Das Skript löscht zu Beginn alle vorhandenen Tabellen in der konfigurierten Datenbank (`Base.metadata.drop_all(engine)`).

```bash
python ingest_data.py
```

## Starten der Anwendung

Sobald das Setup abgeschlossen ist, können Sie die API mit Uvicorn starten.

```bash
uvicorn main:app --reload
```

Die API ist jetzt unter `http://127.0.0.1:8000` verfügbar.

## API-Dokumentation

FastAPI generiert automatisch eine interaktive API-Dokumentation.

-   **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
-   **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
