# main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import cards, users, lists, sets, collection # Importiere unsere neuen Router

app = FastAPI(
    title="Pokenizer API",
    description="Eine API zum Durchsuchen und Verwalten von Pokémon-Sammelkarten.",
    version="1.0.0"
)

# Definiere den Pfad zum Verzeichnis, in dem die Bilder liegen
# ('data/kartendaten' relativ zur 'main.py')
IMAGE_DIR_PATH = os.path.join(os.path.dirname(__file__), 'data', 'kartendaten')

# Stelle dieses Verzeichnis unter dem URL-Pfad '/images' bereit
app.mount("/images", StaticFiles(directory=IMAGE_DIR_PATH), name="images")

# Binde die Router in die Haupt-App ein
app.include_router(cards.router)
app.include_router(users.router)
app.include_router(sets.router)
app.include_router(lists.router)
app.include_router(collection.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Ein einfacher Willkommens-Endpunkt.
    """
    return {"message": "Willkommen bei der Pokenizer API! Gehen Sie zu /docs für die Dokumentation."}