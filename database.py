# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ihre PostgreSQL-Verbindungsdaten
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "lollol" # IHR PASSWORT HIER
POSTGRES_HOST = "192.168.2.173"
POSTGRES_PORT = "5432"
POSTGRES_DB = "pokemon_api"

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Eine Hilfsfunktion, die wir in unseren API-Endpunkten verwenden werden,
# um eine Datenbank-Session zu bekommen.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()