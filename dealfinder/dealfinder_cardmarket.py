"""
dealfinder_cardmarket.py
JensHQ – DealFinder Cardmarket
Pokémon, MTG, Yu-Gi-Oh – scrapet öffentliche Preise
"""

import requests
import re
import time
import random
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9",
}

MIN_PREIS  = 10.0
RABATT_MIN = 0.30

WATCHLIST = [
    # ── POKÉMON ──────────────────────────────
    {"name": "Glurak Base Set Holo",       "kategorie": "Pokemon",  "trend_ref": 350.0,
     "url": "https://www.cardmarket.com/de/Pokemon/Products/Singles/Base-Set/Glurak"},
    {"name": "Glurak ex Obsidian Flames",  "kategorie": "Pokemon",  "trend_ref": 80.0,
     "url": "https://www.cardmarket.com/de/Pokemon/Products/Singles/Karmesin-Purpur-Obsidianflammen/Glurak-ex-246"},
    {"name": "Umbreon VMAX Alt Art",       "kategorie": "Pokemon",  "trend_ref": 120.0,
     "url": "https://www.cardmarket.com/de/Pokemon/Products/Singles/Evolving-Skies/Umbreon-VMAX-215"},
    {"name": "Lugia V Alt Art",            "kategorie": "Pokemon",  "trend_ref": 90.0,
     "url": "https://www.cardmarket.com/de/Pokemon/Products/Singles/Silver-Tempest/Lugia-V-186"},
    {"name": "Mewtwo Base Set Holo",       "kategorie": "Pokemon",  "trend_ref": 80.0,
     "url": "https://www.cardmarket.com/de/Pokemon/Products/Singles/Base-Set/Mewtu"},
    {"name": "Rayquaza VMAX Alt Art",      "kategorie": "Pokemon",  "trend_ref": 75.0,
     "url": "https://www.cardmarket.com/de/Pokemon/Products/Singles/Evolving-Skies/Rayquaza-VMAX-218"},
    {"name": "Pikachu VMAX Rainbow",       "kategorie": "Pokemon",  "trend_ref": 45.0,
     "url": "https://www.cardmarket.com/de/Pokemon/Products/Singles/Vivid-Voltage/Pikachu-VMAX-188"},
    {"name": "Gengar ex Special Ill.",     "kategorie": "Pokemon",  "trend_ref": 55.0,
     "url": "https://www.cardmarket.com/de/Pokemon/Products/Singles/Karmesin-Purpur-Paradoxrift/Gengar-ex-245"},

    # ── MAGIC THE GATHERING ───────────────────
    {"name": "Black Lotus (Beta)",         "kategorie": "MTG",      "trend_ref": 8000.0,
     "url": "https://www.cardmarket.com/de/Magic/Products/Singles/Beta-Edition/Black-Lotus"},
    {"name": "Ragavan Nimble Pilferer",    "kategorie": "MTG",      "trend_ref": 55.0,
     "url": "https://www.cardmarket.com/de/Magic/Products/Singles/Modern-Horizons-2/Ragavan-Nimble-Pilferer"},
    {"name": "Wrenn and Six",              "kategorie": "MTG",      "trend_ref": 70.0,
     "url": "https://www.cardmarket.com/de/Magic/Products/Singles/Modern-Horizons/Wrenn-and-Six"},
    {"name": "Liliana of the Veil",        "kategorie": "MTG",      "trend_ref": 35.0,
     "url": "https://www.cardmarket.com/de/Magic/Products/Singles/Innistrad/Liliana-of-the-Veil"},
    {"name": "Force of Will (Alliances)",  "kategorie": "MTG",      "trend_ref": 80.0,
     "url": "https://www.cardmarket.com/de/Magic/Products/Singles/Alliances/Force-of-Will"},
    {"name": "Fetchlands (Scalding Tarn)", "kategorie": "MTG",      "trend_ref": 25.0,
     "url": "https://www.cardmarket.com/de/Magic/Products/Singles/Zendikar/Scalding-Tarn"},

    # ── YU-GI-OH ─────────────────────────────
    {"name": "Blue-Eyes White Dragon LOB", "kategorie": "YGO",      "trend_ref": 120.0,
     "url": "https://www.cardmarket.com/de/YuGiOh/Products/Singles/Legend-of-Blue-Eyes-White-Dragon/Blue-Eyes-White-Dragon-LOB-EN001"},
    {"name": "Dark Magician LOB",          "kategorie": "YGO",      "trend_ref": 80.0,
     "url": "https://www.cardmarket.com/de/YuGiOh/Products/Singles/Legend-of-Blue-Eyes-White-Dragon/Dark-Magician-LOB-EN005"},
    {"name": "Exodia the Forbidden One",   "kategorie": "YGO",      "trend_ref": 150.0,
     "url": "https://www.cardmarket.com/de/YuGiOh/Products/Singles/Legend-of-Blue-Eyes-White-Dragon/Exodia-the-Forbidden-One-LOB-EN124"},
    {"name": "Ash Blossom & Joyous Spring","kategorie": "YGO",      "trend_ref": 18.0,
     "url": "https://www.cardmarket.com/de/YuGiOh/Products/Singles/Maximum-Crisis/Ash-Blossom-Joyous-Spring"},
    {"name": "Nibiru the Primal Being",    "kategorie": "YGO",      "trend_ref": 12.0,
     "url": "https://www.cardmarket.com/de/YuGiOh/Products/Singles/Soul-Fusion/Nibiru-the-Primal-Being"},
    {"name": "Apollousa Bow of the Goddess","kategorie": "YGO",     "trend_ref": 15.0,
     "url": "https://www.cardmarket.com/de/YuGiOh/Products/Singles/Rising-Rampage/Apollousa-Bow-of-the-Goddess"},
]


def scrape_cardmarket_preis(url: str) -> dict:
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return {}
        html = r.text

        trend_match = re.search(r'Trend[^<]*</dt>\s*<dd[^>]*>\s*([\d,\.]+)\s*€', html, re.IGNORECASE)
        if not trend_match:
            trend_match = re.search(r'"trend"\s*:\s*"?([\d,\.]+)"?', html, re.IGNORECASE)

        min_match = re.search(r'ab\s*([\d,\.]+)\s*€', html, re.IGNORECASE)
        if not min_match:
            min_match = re.search(r'Von\s*([\d,\.]+)\s*€', html, re.IGNORECASE)

        trend = float(trend_match.group(1).replace(',', '.')) if trend_match else 0.0
        minp  = float(min_match.group(1).replace(',', '.'))   if min_match  else 0.0
        return {"trend": trend, "min_preis": minp}

    except Exception as e:
        print(f"  Fehler: {e}")
        return {}


def run_cardmarket_scan() -> list[dict]:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Cardmarket Scan gestartet...")
    alle_deals = []

    for karte in WATCHLIST:
        print(f"  Prüfe [{karte['kategorie']}]: {karte['name']}...")
        data  = scrape_cardmarket_preis(karte["url"])
        trend = data.get("trend", 0.0) or karte["trend_ref"]
        minp  = data.get("min_preis", 0.0)

        if trend < MIN_PREIS or minp <= 0:
            time.sleep(random.uniform(1.5, 2.5))
            continue

        rabatt = (trend - minp) / trend
        if rabatt >= RABATT_MIN:
            alle_deals.append({
                "titel":      karte["name"],
                "kategorie":  karte["kategorie"],
                "preis":      minp,
                "referenz":   trend,
                "rabatt_pct": round(rabatt * 100),
                "url":        karte["url"],
                "quelle":     "Cardmarket",
                "vb":         False,
            })
            print(f"    ✅ DEAL: {karte['name']} – {minp}€ (Trend: {trend}€, -{round(rabatt*100)}%)")

        time.sleep(random.uniform(2.0, 3.5))

    print(f"\nCardmarket: {len(alle_deals)} Deal(s) gefunden.")
    return alle_deals


if __name__ == "__main__":
    deals = run_cardmarket_scan()
    for d in deals:
        print(f"  [{d['kategorie']}] {d['titel']} | {d['preis']}€ | -{d['rabatt_pct']}%")