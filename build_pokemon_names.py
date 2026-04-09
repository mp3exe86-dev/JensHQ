"""
build_pokemon_names.py
Einmalig ausfuehren - laedt alle deutschen Pokemon-Namen von PokeAPI
"""

import requests
import json
import time
from pathlib import Path

POKE_API = "https://pokeapi.co/api/v2"
OUTPUT   = "/home/jens/JobAgent/daten/pokemon_names_de.json"
TOTAL    = 1025

def get_de_name(pokemon_id):
    try:
        r = requests.get(f"{POKE_API}/pokemon-species/{pokemon_id}", timeout=10)
        if r.status_code != 200:
            return {"id": pokemon_id, "de": f"Pokemon{pokemon_id}", "en": f"Pokemon{pokemon_id}"}
        data = r.json()
        name_de = ""
        name_en = data.get("name", "").capitalize()
        for n in data.get("names", []):
            if n["language"]["name"] == "de":
                name_de = n["name"]
                break
        return {"id": pokemon_id, "de": name_de or name_en, "en": name_en}
    except Exception as e:
        print(f"  Fehler bei #{pokemon_id}: {e}")
        return {"id": pokemon_id, "de": f"Pokemon{pokemon_id}", "en": f"Pokemon{pokemon_id}"}

def main():
    print(f"Lade deutsche Namen fuer {TOTAL} Pokemon...")
    print("Dauert ca. 15-20 Minuten.\n")
    namen = {}
    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)

    for i in range(1, TOTAL + 1):
        result = get_de_name(i)
        namen[str(i)] = result
        print(f"  #{i:04d} {result['en']:20s} -> {result['de']}")

        if i % 50 == 0:
            with open(OUTPUT, "w", encoding="utf-8") as f:
                json.dump(namen, f, ensure_ascii=False, indent=2)
            print(f"\nZwischenspeicherung: {i}/{TOTAL}\n")

        time.sleep(0.3)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(namen, f, ensure_ascii=False, indent=2)
    print(f"\nFertig! {len(namen)} Namen gespeichert.")

if __name__ == "__main__":
    main()