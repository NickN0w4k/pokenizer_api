# routers/collection.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas, database
from .auth_utils import get_current_active_user

router = APIRouter(
    prefix="/collection",
    tags=["Collection"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/cards", response_model=List[schemas.CollectionItemResponse])
def get_user_collection(
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Gibt die Sammlung des Benutzers zurück, inklusive der Anzahl jeder Karte.
    """
    collection_items = db.query(models.UserCollection).filter(
        models.UserCollection.user_id == current_user.id
    ).all()
    
    response = []
    for item in collection_items:
        response.append({
            "quantity": item.quantity,
            "card": item.card
        })
    return response

@router.post("/cards/{tcg_id}", response_model=schemas.Message)
def add_or_increment_card_in_collection(
    tcg_id: str, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Fügt eine Karte zur Sammlung hinzu oder erhöht die Anzahl, falls sie bereits vorhanden ist.
    """
    card_to_add = db.query(models.Card).filter(models.Card.tcg_id == tcg_id).first()
    if not card_to_add:
        raise HTTPException(status_code=404, detail="Karte nicht gefunden")

    existing_entry = db.query(models.UserCollection).filter(
        models.UserCollection.user_id == current_user.id,
        models.UserCollection.card_id == card_to_add.id
    ).first()

    # --- FIX for Error 2 ---
    if existing_entry is not None:
        # --- FIX for Error 1 ---
        existing_entry.quantity = existing_entry.quantity + 1
        db.commit()
        return {"detail": f"Anzahl für '{card_to_add.name}' auf {existing_entry.quantity} erhöht."}
    else:
        new_entry = models.UserCollection(user_id=current_user.id, card_id=card_to_add.id, quantity=1)
        db.add(new_entry)
        db.commit()
        return {"detail": f"Karte '{card_to_add.name}' zur Sammlung hinzugefügt."}

@router.delete("/cards/{tcg_id}", response_model=schemas.Message)
def remove_or_decrement_card_in_collection(
    tcg_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Verringert die Anzahl einer Karte in der Sammlung oder entfernt sie,
    wenn die Anzahl 1 beträgt.
    """
    card_to_remove = db.query(models.Card).filter(models.Card.tcg_id == tcg_id).first()
    if not card_to_remove:
        raise HTTPException(status_code=404, detail="Karte nicht gefunden")

    entry = db.query(models.UserCollection).filter(
        models.UserCollection.user_id == current_user.id,
        models.UserCollection.card_id == card_to_remove.id
    ).first()

    # Use 'is not None' for existence check here too for consistency
    if entry is None:
        raise HTTPException(status_code=404, detail="Karte nicht in der Sammlung gefunden")

    if entry.quantity > 1:
        # --- FIX for Error 3 ---
        entry.quantity = entry.quantity - 1
        db.commit()
        return {"detail": f"Anzahl für '{card_to_remove.name}' auf {entry.quantity} reduziert."}
    else:
        db.delete(entry)
        db.commit()
        return {"detail": f"Karte '{card_to_remove.name}' aus der Sammlung entfernt."}