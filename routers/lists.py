# routers/lists.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

import models, schemas, database

# Erstelle einen neuen Router für diese Endpunkt-Gruppe
router = APIRouter(
    tags=["Helper Lists"] # Gruppiert diese Endpunkte in der Doku
)

@router.get("/sets/", response_model=List[schemas.SetNameResponse])
def get_all_sets(db: Session = Depends(database.get_db)):
    """
    Gibt eine Liste aller existierenden Set-Namen zurück, sortiert nach Name.
    Nützlich für Filter-Dropdowns.
    """
    sets = db.query(models.Set).order_by(models.Set.name).all()
    return sets

@router.get("/rarities/", response_model=List[schemas.RarityNameResponse])
def get_all_rarities(db: Session = Depends(database.get_db)):
    """
    Gibt eine Liste aller einzigartigen Seltenheiten zurück, sortiert nach Name.
    """
    rarities = db.query(models.Rarity).order_by(models.Rarity.name).all()
    return rarities

@router.get("/types/", response_model=List[schemas.TypeNameResponse])
def get_all_types(db: Session = Depends(database.get_db)):
    """
    Gibt eine Liste aller Pokémon-Typen zurück, sortiert nach Name.
    """
    types = db.query(models.Type).order_by(models.Type.name).all()
    return types