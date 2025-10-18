# routers/cards.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
# 'aliased' wird benötigt, um Mehrdeutigkeiten bei Joins zu vermeiden
from sqlalchemy.orm import aliased
from typing import List, Optional
import math

import models, schemas, database

# Erstelle einen "Router", um alle kartenbezogenen Endpunkte zu bündeln
router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)


@router.get("/", response_model=schemas.PaginatedCardResponse)
def search_cards(
    # --- NEUER FILTERPARAMETER HINZUGEFÜGT ---
    attack_name: Optional[str] = Query(None, description="Filtert Karten, die eine Attacke mit diesem Namen haben (Groß-/Kleinschreibung irrelevant)."),

    # Bestehende Filterparameter
    number_in_set: Optional[str] = Query(None, description="Filtert Karten nach der exakten Nummer im Set (z.B. '1/132')."),
    name: Optional[str] = Query(None, description="Filtert Karten, deren Name den Text enthält (Groß-/Kleinschreibung irrelevant)."),
    supertype: Optional[str] = Query(None, description="Filtert nach exaktem Supertype ('Pokémon', 'Trainer', 'Energy')."),
    type: Optional[str] = Query(None, description="Filtert Pokémon nach einem exakten Typ (z.B. 'Feuer')."),
    subtype: Optional[str] = Query(None, description="Filtert Karten nach einem exakten Subtyp (z.B. 'Basis', 'Phase-1')."),
    rarity: Optional[str] = Query(None, description="Filtert Karten nach exaktem Seltenheits-Namen."),
    set_name: Optional[str] = Query(None, description="Filtert Karten nach exaktem Set-Namen."),
    hp_gte: Optional[int] = Query(None, description="Filtert Pokémon, deren HP größer oder gleich diesem Wert sind."),
    hp_lt: Optional[int] = Query(None, description="Filtert Pokémon, deren HP kleiner als dieser Wert sind."),

    # Paginierungsparameter
    page: int = Query(1, ge=1, description="Die Seitenzahl."),
    page_size: int = Query(20, ge=1, le=100, description="Anzahl der Ergebnisse pro Seite."),

    db: Session = Depends(database.get_db)
):
    """
    Sucht und listet Karten mit erweiterten Filtern und Paginierung auf.
    Alle Filter können kombiniert werden.
    """
    query = db.query(models.Card)

    # --- NEUE FILTERLOGIK IMPLEMENTIERT ---
    if attack_name:
        # Führe einen Join zur Attack-Tabelle durch
        # Verwende .any(), um zu prüfen, ob *mindestens eine* Attacke den Kriterien entspricht
        query = query.join(models.Attack).filter(
            models.Attack.name.ilike(f"%{attack_name}%"))

    # Bestehende Filterlogik
    if number_in_set:
        query = query.filter(models.Card.number_in_set == number_in_set)

    if name:
        query = query.filter(models.Card.name.ilike(f"%{name}%"))

    if supertype:
        query = query.filter(models.Card.supertype == supertype)

    if type:
        # Erstelle einen Alias für die Type-Tabelle, um Konflikte zu vermeiden, falls später mehr Joins hinzukommen
        type_alias = aliased(models.Type)
        query = query.join(models.Card.types.of_type(type_alias)).filter(
            type_alias.name == type)

    if subtype:
        subtype_alias = aliased(models.Subtype)
        query = query.join(models.Card.subtypes.of_type(subtype_alias)).filter(
            subtype_alias.name == subtype)

    if rarity:
        query = query.join(models.Rarity).filter(models.Rarity.name == rarity)

    if set_name:
        query = query.join(models.Set).filter(models.Set.name == set_name)

    if hp_gte is not None:
        query = query.filter(models.Card.hp >= hp_gte)

    if hp_lt is not None:
        query = query.filter(models.Card.hp < hp_lt)

    # --- Paginierungslogik ---
    # Zähle die *eindeutigen* Karten, um Duplikate durch Joins zu vermeiden
    total_items = query.distinct().count()
    total_pages = math.ceil(total_items / page_size)

    cards = query.options(
        selectinload(models.Card.set),
        selectinload(models.Card.rarity)
    ).distinct().offset((page - 1) * page_size).limit(page_size).all()

    return {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "items": cards
    }


@router.get("/{tcg_id}", response_model=schemas.CardDetailResponse)
def get_card_by_id(tcg_id: str, db: Session = Depends(database.get_db)):
    """
    Ruft alle Details für eine einzelne Karte anhand ihrer TCG-ID (z.B. "me01-1") ab.
    """
    # Lade alle Beziehungen direkt mit, da wir hier die Detailansicht wollen
    card = db.query(models.Card).options(
        selectinload(models.Card.set),
        selectinload(models.Card.rarity),
        selectinload(models.Card.artist),
        selectinload(models.Card.types),
        selectinload(models.Card.subtypes),
        selectinload(models.Card.attacks),
        selectinload(models.Card.abilities),
        selectinload(models.Card.rules)
    ).filter(models.Card.tcg_id == tcg_id).first()

    if card is None:
        raise HTTPException(status_code=404, detail="Karte nicht gefunden")

    return card