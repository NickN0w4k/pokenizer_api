# models.py
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Date
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint

# Die Base-Klasse, von der alle unsere Modelle erben.
Base = declarative_base()

# --- Verbindungstabellen für Viele-zu-Viele-Beziehungen ---

card_types_table = Table('card_types', Base.metadata,
    Column('card_id', Integer, ForeignKey('cards.id'), primary_key=True),
    Column('type_id', Integer, ForeignKey('types.id'), primary_key=True)
)

card_subtypes_table = Table('card_subtypes', Base.metadata,
    Column('card_id', Integer, ForeignKey('cards.id'), primary_key=True),
    Column('subtype_id', Integer, ForeignKey('subtypes.id'), primary_key=True)
)

# --- Lookup-Tabellen (für einzigartige Werte) ---

class Set(Base):
    __tablename__ = 'sets'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    release_date = Column(Date, nullable=True) # Korrekter Datentyp
    cards = relationship('Card', back_populates='set')

class Rarity(Base):
    __tablename__ = 'rarities'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    cards = relationship('Card', back_populates='rarity')

class Type(Base):
    __tablename__ = 'types'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

class Subtype(Base):
    __tablename__ = 'subtypes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    cards = relationship('Card', back_populates='artist')
    
# --- Haupt-Tabelle: Card ---

class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True) # Neuer, einheitlicher Primärschlüssel
    tcg_id = Column(String, nullable=False, unique=True, index=True) # Die alte ID wie "me01-1"
    name = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=True)
    supertype = Column(String, nullable=False)
    hp = Column(Integer, nullable=True)
    number_in_set = Column(String, nullable=True)
    evolves_from = Column(String, nullable=True)

    # Fremdschlüssel zu den Lookup-Tabellen
    set_id = Column(Integer, ForeignKey('sets.id'))
    rarity_id = Column(Integer, ForeignKey('rarities.id'), nullable=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=True)

    # Beziehungen
    set = relationship('Set', back_populates='cards')
    rarity = relationship('Rarity', back_populates='cards')
    artist = relationship('Artist', back_populates='cards')
    
    types = relationship('Type', secondary=card_types_table, backref='cards')
    subtypes = relationship('Subtype', secondary=card_subtypes_table, backref='cards')
    
    attacks = relationship('Attack', back_populates='card', cascade="all, delete-orphan")
    abilities = relationship('Ability', back_populates='card', cascade="all, delete-orphan")
    rules = relationship('Rule', back_populates='card', cascade="all, delete-orphan")

# --- Detail-Tabellen ---

class Attack(Base):
    __tablename__ = 'attacks'
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'))
    name = Column(String, nullable=True) # Erlaubt leere Namen
    cost = Column(Text, nullable=True)
    damage = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    card = relationship('Card', back_populates='attacks')

class Ability(Base):
    __tablename__ = 'abilities'
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'))
    name = Column(String, nullable=False)
    text = Column(Text, nullable=True)
    type = Column(String, nullable=True)
    card = relationship('Card', back_populates='abilities')
    
class Rule(Base):
    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'))
    text = Column(Text, nullable=True) # Erlaubt leere Regeltexte
    card = relationship('Card', back_populates='rules')

    # --- BENUTZER-TABELLE HINZUFÜGEN ---

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

# --- VERBINDUNGSTABELLE FÜR SAMMLUNGEN HINZUFÜGEN ---

class UserCollection(Base):
    __tablename__ = 'user_collections'
    # Jede Zeile ist eine eindeutige Kombination aus Benutzer und Karte
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'), primary_key=True)
    quantity = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )

    # Beziehungen, damit SQLAlchemy weiß, wie alles zusammenhängt
    user = relationship('User', backref='collection_items')
    card = relationship('Card', backref='collection_items')