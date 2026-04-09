"""
dealfinder_referenz.py
JensHQ – Referenzpreis-Modul
Holt aktuelle Marktpreise von Idealo (Neuware) und Pricecharting (Retro/Konsolen)
"""

import requests
import re
import time
import json
import os
from datetime import date

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9",
}

CACHE_FILE = r"C:\JobAgent\shared\daten\referenz_cache.json"
CACHE_TTL  = 1  # Tag


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache: dict):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def cache_gueltig(cache: dict, key: str) -> bool:
    entry = cache.get(key, {})
    if not entry:
        return False
    try:
        return (date.today() - date.fromisoformat(entry.get("datum", "2000-01-01"))).days < CACHE_TTL
    except Exception:
        return False


def get_idealo_preis(suchbegriff: str) -> float:
    """Holt günstigsten Neupreis von Idealo."""
    cache = load_cache()
    key   = f"idealo_{suchbegriff}"
    if cache_gueltig(cache, key):
        return cache[key]["preis"]

    try:
        url = f"https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q={suchbegriff.replace(' ', '+')}"
        r   = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return 0.0

        html    = r.text
        matches = re.findall(r'(\d+),(\d{2})\s*€', html)
        preise  = []
        for m in matches:
            try:
                preise.append(float(f"{m[0]}.{m[1]}"))
            except Exception:
                pass

        preis = min(preise) if preise else 0.0

        cache[key] = {"preis": preis, "datum": str(date.today())}
        save_cache(cache)
        time.sleep(1.5)
        return preis

    except Exception as e:
        print(f"  Idealo Fehler ({suchbegriff}): {e}")
        return 0.0


def get_pricecharting_preis(suchbegriff: str) -> float:
    """Holt Marktpreis von Pricecharting (gut für Retro-Konsolen)."""
    cache = load_cache()
    key   = f"pricecharting_{suchbegriff}"
    if cache_gueltig(cache, key):
        return cache[key]["preis"]

    try:
        url = f"https://www.pricecharting.com/search-products?q={suchbegriff.replace(' ', '+')}&type=prices"
        r   = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return 0.0

        html    = r.text
        # Preis aus erstem Suchergebnis
        matches = re.findall(r'\$\s*(\d+)\.(\d{2})', html)
        if not matches:
            return 0.0

        # USD → EUR (grob ~0.92)
        usd   = float(f"{matches[0][0]}.{matches[0][1]}")
        preis = round(usd * 0.92, 2)

        cache[key] = {"preis": preis, "datum": str(date.today())}
        save_cache(cache)
        time.sleep(1.5)
        return preis

    except Exception as e:
        print(f"  Pricecharting Fehler ({suchbegriff}): {e}")
        return 0.0


def get_referenzpreis(suchbegriff: str, kategorie: str, fallback: float) -> float:
    """
    Kombiniert beide Quellen – Idealo primär, Pricecharting sekundär.
    Fallback = hardcoded Wert wenn beide scheitern.
    """
    preis = 0.0

    if kategorie == "Retro":
        # Retro: Pricecharting zuerst, dann Idealo
        preis = get_pricecharting_preis(suchbegriff)
        if preis <= 0:
            preis = get_idealo_preis(suchbegriff)
    else:
        # Konsolen & Lego: Idealo zuerst
        preis = get_idealo_preis(suchbegriff)
        if preis <= 0:
            preis = get_pricecharting_preis(suchbegriff)

    return preis if preis > 0 else fallback


if __name__ == "__main__":
    print("Teste Referenzpreise...")
    print(f"PS5 (Idealo):      {get_idealo_preis('PlayStation 5')}€")
    print(f"SNES (Pricecharting): {get_pricecharting_preis('Super Nintendo SNES')}€")