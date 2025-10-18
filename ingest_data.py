# ingest_data.py
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
from datetime import datetime

# Importiere die neuen, optimierten Pokémon-Modelle
from models import Base, Set, Rarity, Type, Subtype, Artist, Card, Attack, Ability, Rule

# --- KONFIGURATION ---
# Passen Sie diese Werte an Ihre Umgebung an.
DATA_ROOT_DIR = os.path.join(os.path.dirname(__file__), 'data', 'kartendaten')
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "lollol" # Ersetzen Sie dies mit Ihrem Passwort
POSTGRES_HOST = "192.168.2.173"
POSTGRES_PORT = "5432"
POSTGRES_DB = "pokemon_api" # Der Name Ihrer neuen, leeren Datenbank

POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# --- DATENBANK-SETUP ---
engine = create_engine(POSTGRES_URI)
Session = sessionmaker(bind=engine)
session = Session()

# --- HAUPT-LOGIK ---
def ingest_data():
    """Liest alle JSON-Dateien, verarbeitet die Daten und befüllt die Datenbank."""
    print("--- Starte Pokémon-Karten Ingestion ---")

    print("Setze Datenbank zurück und erstelle Tabellen...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Tabellen erfolgreich erstellt.")

    json_files = [os.path.join(root, file) for root, _, files in os.walk(DATA_ROOT_DIR) for file in files if file.endswith('.json')]

    print("\n[1/3] Lese alle JSON-Dateien, um einzigartige Werte zu sammeln...")
    all_sets, all_rarities, all_types, all_subtypes, all_artists = set(), set(), set(), set(), set()
    set_release_dates = {}

    for file_path in tqdm(json_files, desc="Sammle Werte"):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            set_data = data.get('set')
            if set_data and isinstance(set_data, dict):
                set_name = set_data.get('name')
                if set_name:
                    all_sets.add(set_name)
                    if set_name not in set_release_dates and set_data.get('releaseDate'):
                        set_release_dates[set_name] = set_data.get('releaseDate')
                
                all_rarities.add(set_data.get('rarity'))
            
            if data.get('types'): all_types.update(data['types'])
            if data.get('subtypes'): all_subtypes.update(data['subtypes'])
            if data.get('artist'): all_artists.add(data['artist'])

    print("\n[2/3] Befülle Lookup-Tabellen in der Datenbank...")
    set_map, rarity_map, type_map, subtype_map, artist_map = {}, {}, {}, {}, {}

    for name in tqdm(sorted(list(all_sets - {None})), desc="Sets"):
        release_date_str = set_release_dates.get(name)
        release_date_obj = None
        if release_date_str:
            try:
                release_date_obj = datetime.strptime(release_date_str, '%Y/%m/%d').date()
            except ValueError:
                print(f"Warnung: Ungültiges Datumsformat für Set '{name}': {release_date_str}")

        obj = Set(name=name, release_date=release_date_obj)
        session.add(obj)
        session.commit()
        set_map[name] = obj.id

    for model, names, name_map in [(Rarity, all_rarities, rarity_map), (Type, all_types, type_map), (Subtype, all_subtypes, subtype_map), (Artist, all_artists, artist_map)]:
        for name in tqdm(sorted(list(names - {None})), desc=model.__tablename__):
            obj = model(name=name)
            session.add(obj)
            session.commit()
            name_map[name] = obj.id

    print("\n[3/3] Befülle Haupttabelle 'cards' und verknüpfe Beziehungen...")
    for file_path in tqdm(json_files, desc="Importiere Karten"):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            tcg_id = data['id']
        
            # Finde den relativen Pfad der JSON-Datei zum DATA_ROOT_DIR
            # z.B. "bw1\bw1-1.json"
            relative_json_path = os.path.relpath(file_path, DATA_ROOT_DIR)
            
            # Ersetze die Dateiendung .json durch .png
            # z.B. "bw1\bw1-1.png"
            relative_image_path = os.path.splitext(relative_json_path)[0] + ".png"
            
            # Erstelle die URL: Ersetze OS-Trennzeichen (\) durch URL-Trennzeichen (/)
            # und stelle den Mount-Point '/images' voran.
            # z.B. "/images/bw1/bw1-1.png"
            local_image_url = f"/images/{relative_image_path.replace(os.sep, '/')}"

            set_data = data.get('set', {})
            set_id = set_map.get(set_data.get('name')) if isinstance(set_data, dict) else None
            rarity_id = rarity_map.get(set_data.get('rarity')) if isinstance(set_data, dict) else None
            
            new_card = Card(
                tcg_id=data['id'], 
                name=data['name'], 
                image_url=local_image_url,
                supertype=data['supertype'],
                hp=int(data['hp']) if data.get('hp') and str(data['hp']).isdigit() else None,
                number_in_set=set_data.get('number') if isinstance(set_data, dict) else None,
                evolves_from=data.get('evolvesFrom'), set_id=set_id, rarity_id=rarity_id,
                artist_id=artist_map.get(data.get('artist'))
            )
            
            session.add(new_card)

            if data.get('types'):
                types_to_add = session.query(Type).filter(Type.name.in_(data['types'])).all()
                new_card.types.extend(types_to_add)
            
            if data.get('subtypes'):
                subtypes_to_add = session.query(Subtype).filter(Subtype.name.in_(data['subtypes'])).all()
                new_card.subtypes.extend(subtypes_to_add)
                    
            session.flush()

            if data.get('attacks'):
                for attack_data in data['attacks']:
                    session.add(Attack(card_id=new_card.id, name=attack_data.get('name'),
                                       cost=", ".join(attack_data.get('cost', [])), damage=attack_data.get('damage'),
                                       text=attack_data.get('text')))
            
            if data.get('abilities'):
                for ability_data in data['abilities']:
                    session.add(Ability(card_id=new_card.id, name=ability_data['name'],
                                        text=ability_data.get('text'), type=ability_data.get('type')))
            
            if data.get('rules'):
                for rule_text in data['rules']:
                    if rule_text:
                        session.add(Rule(card_id=new_card.id, text=rule_text))
    
    print("Alle Objekte erstellt. Führe finalen Commit aus...")
    session.commit()
    session.close()
    print("\n--- Daten-Ingestion erfolgreich abgeschlossen! ---")

if __name__ == "__main__":
    ingest_data()