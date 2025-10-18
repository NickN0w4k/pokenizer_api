# routers/sets.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from typing import List

import models, schemas, database

router = APIRouter(
    prefix="/sets", # Alle Routen hier beginnen mit /sets
    tags=["Sets"]
)

@router.get("/{set_name}/cards", response_model=List[schemas.CardListResponse])
def get_cards_by_set_name(set_name: str, db: Session = Depends(database.get_db)):
    """
    Ruft alle Karten eines spezifischen Sets anhand des exakten Set-Namens ab.
    """
    # Finde zuerst das Set, um sicherzustellen, dass es existiert.
    target_set = db.query(models.Set).filter(models.Set.name == set_name).first()
    if not target_set:
        raise HTTPException(status_code=404, detail=f"Set mit dem Namen '{set_name}' nicht gefunden.")

    # Hole alle Karten, die zu diesem Set gehören.
    cards = db.query(models.Card).filter(models.Card.set_id == target_set.id).options(
        selectinload(models.Card.set),
        selectinload(models.Card.rarity)
    ).order_by(models.Card.id).all() # Sortierung nach ID für konsistente Ergebnisse

    return cards