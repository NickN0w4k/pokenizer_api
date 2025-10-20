# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# --- Basis-Modelle (für verschachtelte Objekte) ---

class Set(BaseModel):
    name: str
    symbol_url: Optional[str] = None
    release_date: Optional[date] = None
    class Config: from_attributes = True

class Rarity(BaseModel):
    name: str
    class Config: from_attributes = True

class Artist(BaseModel):
    name: str
    class Config: from_attributes = True
        
class Type(BaseModel):
    name: str
    class Config: from_attributes = True

class Subtype(BaseModel):
    name: str
    class Config: from_attributes = True

class Attack(BaseModel):
    name: Optional[str] = None
    cost: Optional[str] = None
    damage: Optional[str] = None
    text: Optional[str] = None
    class Config: from_attributes = True

class Ability(BaseModel):
    name: str
    text: Optional[str] = None
    type: Optional[str] = None
    class Config: from_attributes = True

class Rule(BaseModel):
    text: str
    class Config: from_attributes = True


# --- Haupt-Modell für Karten (API-Antworten) ---

class CardBase(BaseModel):
    tcg_id: str
    name: str
    image_url: Optional[str] = None

class CardListResponse(CardBase):
    """Eine vereinfachte Kartenansicht für Listen."""
    number_in_set: Optional[str] = None
    set: Optional[Set] = None
    rarity: Optional[Rarity] = None
    hp: Optional[int] = None
    class Config: from_attributes = True

class CardDetailResponse(CardBase):
    """Die vollständige Detailansicht einer Karte."""
    supertype: str
    hp: Optional[int] = None
    number_in_set: Optional[str] = None
    evolves_from: Optional[str] = None
    
    set: Optional[Set] = None
    rarity: Optional[Rarity] = None
    artist: Optional[Artist] = None
    
    types: List[Type] = []
    subtypes: List[Subtype] = []
    attacks: List[Attack] = []
    abilities: List[Ability] = []
    rules: List[Rule] = []

    class Config: from_attributes = True

class PaginatedCardResponse(BaseModel):
    """Das Modell für die paginierte Antwort bei der Kartensuche."""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    items: List[CardListResponse]


# --- Modelle für Benutzer & Authentifizierung (für die Zukunft) ---

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Modelle für einfache Listen (Hilfs-Endpunkte) ---

class SetNameResponse(BaseModel):
    name: str
    class Config: from_attributes = True

class RarityNameResponse(BaseModel):
    name: str
    class Config: from_attributes = True

class TypeNameResponse(BaseModel):
    name: str
    class Config: from_attributes = True

# --- ALLGEMEINE MODELLE ---
class Message(BaseModel):
    detail: str

# --- NEUES MODELL FÜR SAMMLUNGS-ANTWORTEN ---
class CollectionItemResponse(BaseModel):
    quantity: int
    card: CardListResponse

    