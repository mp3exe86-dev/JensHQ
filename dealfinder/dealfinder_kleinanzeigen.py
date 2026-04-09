"""
dealfinder_kleinanzeigen.py
JensHQ – DealFinder Quoka.de
"""

import requests
import re
import time
import random
import html as html_lib
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9",
}

MIN_PREIS  = 30
MAX_PREIS  = 2000
RABATT_MIN = 0.25

SUCHEN = [
    {"begriff": "PS5 Konsole", "kategorie": "Konsolen", "referenz": 430,
     "muss_enthalten": ["ps5 konsole", "playstation 5 konsole", "ps5 slim", "ps5 pro", "ps5 digital", "ps5 disc"]},
    {"begriff": "Xbox Series X",        "kategorie": "Konsolen", "referenz": 400,
     "muss_enthalten": ["xbox series x"]},
   {"begriff": "Nintendo Switch OLED", "kategorie": "Konsolen", "referenz": 290,
 "muss_enthalten": ["switch oled", "oled"]},
    {"begriff": "SNES Super Nintendo",  "kategorie": "Retro",    "referenz": 80,
     "muss_enthalten": ["snes", "super nintendo"]},
    {"begriff": "Nintendo 64 N64",      "kategorie": "Retro",    "referenz": 70,
     "muss_enthalten": ["n64", "nintendo 64"]},
    {"begriff": "Game Boy Color",       "kategorie": "Retro",    "referenz": 60,
     "muss_enthalten": ["game boy", "gameboy"]},
    {"begriff": "Game Boy Advance",     "kategorie": "Retro",    "referenz": 55,
     "muss_enthalten": ["game boy advance", "gba", "gameboy advance"]},
    {"begriff": "GameBoy original",     "kategorie": "Retro",    "referenz": 45,
     "muss_enthalten": ["gameboy", "game boy"]},
    {"begriff": "Lego Star Wars 75192", "kategorie": "Lego",     "referenz": 700,
     "muss_enthalten": ["lego", "75192"]},
    {"begriff": "Lego Star Wars 75313", "kategorie": "Lego",     "referenz": 650,
     "muss_enthalten": ["lego", "75313"]},
    {"begriff": "Lego Technic 42083",   "kategorie": "Lego",     "referenz": 350,
     "muss_enthalten": ["lego", "42083"]},
    {"begriff": "Lego Technic 42143",   "kategorie": "Lego",     "referenz": 280,
     "muss_enthalten": ["lego", "42143"]},
    {"begriff": "Lego Icons 10294",     "kategorie": "Lego",     "referenz": 230,
     "muss_enthalten": ["lego", "10294"]},
    {"begriff": "Lego Icons 10306",     "kategorie": "Lego",     "referenz": 250,
     "muss_enthalten": ["lego", "10306"]},
    {"begriff": "Lego Creator 10280",   "kategorie": "Lego",     "referenz": 180,
     "muss_enthalten": ["lego", "10280"]},
]

SKIP_KEYWORDS = [
    "defekt", "bastler", "ersatzteile", "kaputt", "broken",
    "ohne controller", "kein netzteil", "gesucht", "suche", "tausch",
    "massage", "katze", "hund", "welpen", "whatsapp", "lenkrad",
    "kühlschrank", " spiel", "controller allein", "ps4", "ps 4",
    "game ", "games" , "fatal frame", "resident evil", "re51", "remake", "pokemon smaragd",
"international superstar", "zelda für", "f-zero", "moorhuhn", "grand theft",
"n64 controller", "controller original"
]

VB_KEYWORDS = ["vb", "vhb", "verhandlungsbasis"]


def parse_preis(preis_str: str) -> float:
    cleaned = re.sub(r'[^\d,.]', '', str(preis_str)).replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def ist_vb(titel: str) -> bool:
    return any(kw in titel.lower() for kw in VB_KEYWORDS)

def hat_skip_keyword(titel: str) -> bool:
    return any(kw in titel.lower() for kw in SKIP_KEYWORDS)

def enthaelt_pflichtbegriff(titel: str, muss_enthalten: list) -> bool:
    """Prüft ob mindestens ein Pflichtbegriff im Titel vorkommt."""
    titel_lower = titel.lower()
    return any(kw in titel_lower for kw in muss_enthalten)

def decode_html(text: str) -> str:
    """Dekodiert HTML-Entities wie &#246; → ö"""
    return html_lib.unescape(text)


def suche_quoka(begriff: str) -> list[dict]:
    angebote = []
    url = f"https://www.quoka.de/anzeigen/?q={begriff.replace(' ', '+')}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []

        html = r.text

        # JSON-LD Blöcke extrahieren – nur echte Produktdaten
        # Suche nach vollständigen Produkt-Objekten
        produkte = re.findall(
            r'"name"\s*:\s*"([^"]+)".*?"url"\s*:\s*"([^"]+)".*?"price"\s*:\s*"([\d\.]+)"',
            html, re.DOTALL
        )

        # onclick URLs für bessere Link-Qualität
        onclick_urls = re.findall(
            r"window\.location\.href='(https://www\.quoka\.de/anzeigen/[^']+)'",
            html
        )

        for i, (name, rel_url, preis_str) in enumerate(produkte):
            name = decode_html(name).strip()

            # Absolute URL
            if rel_url.startswith("http"):
                full_url = rel_url
            elif i < len(onclick_urls):
                full_url = onclick_urls[i]
            else:
                full_url = f"https://www.quoka.de/{rel_url.lstrip('/')}"

            angebote.append({
                "titel": name,
                "preis": parse_preis(preis_str),
                "url":   full_url,
            })

    except Exception as e:
        print(f"  Fehler: {e}")

    return angebote


def analysiere_deals(angebote: list[dict], referenz: float, kategorie: str, muss_enthalten: list) -> list[dict]:
    deals = []
    for a in angebote:
        preis = a["preis"]
        titel = a["titel"]

        if preis <= 0 or preis < MIN_PREIS or preis > MAX_PREIS:
            continue
        if hat_skip_keyword(titel):
            continue
        if not enthaelt_pflichtbegriff(titel, muss_enthalten):
            continue

        rabatt = (referenz - preis) / referenz
        if rabatt >= RABATT_MIN:
            deals.append({
                "titel":      titel,
                "kategorie":  kategorie,
                "preis":      preis,
                "referenz":   referenz,
                "rabatt_pct": round(rabatt * 100),
                "vb":         ist_vb(titel),
                "url":        a["url"],
                "quelle":     "Quoka.de",
            })

    return sorted(deals, key=lambda d: d["rabatt_pct"], reverse=True)


def run_kleinanzeigen_scan() -> list[dict]:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Quoka.de Scan gestartet...")
    alle_deals = []
    gesehen    = set()

    for such in SUCHEN:
        print(f"  [{such['kategorie']}] '{such['begriff']}' – Referenz: {such['referenz']}€")
        angebote = suche_quoka(such["begriff"])
        deals    = analysiere_deals(
            angebote, such["referenz"],
            such["kategorie"], such["muss_enthalten"]
        )

        for deal in deals:
            if deal["url"] not in gesehen:
                gesehen.add(deal["url"])
                alle_deals.append(deal)
                print(f"    ✅ {deal['titel'][:50]} – {deal['preis']}€ (-{deal['rabatt_pct']}%)")

        time.sleep(random.uniform(1.0, 2.0))

    print(f"\nQuoka.de: {len(alle_deals)} Deal(s) gefunden.")
    return alle_deals


if __name__ == "__main__":
    run_kleinanzeigen_scan()