# main.py
from fastapi import FastAPI
from routers import cards, users, lists, sets, collection # Importiere unsere neuen Router

app = FastAPI(
    title="Pokenizer API",
    description="Eine API zum Durchsuchen und Verwalten von Pokémon-Sammelkarten.",
    version="1.0.0"
)

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