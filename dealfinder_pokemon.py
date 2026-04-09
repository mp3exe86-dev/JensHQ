"""
dealfinder_pokemon.py
JensHQ – DealFinder Pokémon Sets
Sucht teuerste Karten aus bekannten Sets die unter Marktwert sind
Datenquelle: Pokemon TCG API (kostenlos, kein Key nötig)
"""

import requests
import sys
import time
from datetime import datetime

sys.path.insert(0, r"/home/jens/JobAgent")
from telegram_notifier import send_deal_message

# ──────────────────────────────────────────
#  KONFIGURATION
# ──────────────────────────────────────────
TCG_API       = "https://api.pokemontcg.io/v2"
MIN_MARKTWERT = 50.0   # Nur Karten mit Trendpreis >= 20€
RABATT_MIN    = 0.40   # 33% unter Marktwert

# ──────────────────────────────────────────
#  SET-WATCHLIST mit deutschen Namen + Tier
# ──────────────────────────────────────────
SETS_WATCHLIST = [
    # ── S-Tier ──
    {"id": "base1",   "de": "Basis Set",              "en": "Base Set",               "tier": "S"},
    {"id": "jungle",  "de": "Dschungel",              "en": "Jungle",                 "tier": "S"},
    {"id": "fossil",  "de": "Fossil",                 "en": "Fossil",                 "tier": "S"},
    {"id": "rocket1", "de": "Team Rocket",            "en": "Team Rocket",            "tier": "S"},
    {"id": "neo1",    "de": "Neo Genesis",            "en": "Neo Genesis",            "tier": "S"},
    {"id": "neo2",    "de": "Neo Entdeckung",         "en": "Neo Discovery",          "tier": "S"},
    {"id": "neo3",    "de": "Neo Schicksal",          "en": "Neo Revelation",         "tier": "S"},
    {"id": "neo4",    "de": "Neo Destiny",            "en": "Neo Destiny",            "tier": "S"},
    {"id": "si1",     "de": "Skyridge",               "en": "Skyridge",               "tier": "S"},
    {"id": "aq1",     "de": "Aquapolis",              "en": "Aquapolis",              "tier": "S"},
    {"id": "ex1",     "de": "EX Rubin & Saphir",      "en": "Expedition Base Set",    "tier": "S"},
    # ── A-Tier ──
    {"id": "ex13",    "de": "EX Drachensturm",        "en": "EX Dragon Frontiers",    "tier": "A"},
    {"id": "ex15",    "de": "EX Team Rocket Returns", "en": "EX Team Rocket Returns", "tier": "A"},
    {"id": "ex7",     "de": "EX Deoxys",              "en": "EX Deoxys",              "tier": "A"},
    {"id": "dp1",     "de": "Diamant & Perl",         "en": "Diamond & Pearl",        "tier": "A"},
    {"id": "pl1",     "de": "Platin",                 "en": "Platinum",               "tier": "A"},
    {"id": "hgss1",   "de": "HeartGold SoulSilver",   "en": "HeartGold SoulSilver",   "tier": "A"},
    # ── B-Tier Sun & Moon ──
    {"id": "sm35",    "de": "Verborgenes Schicksal",  "en": "Hidden Fates",           "tier": "B"},
    {"id": "sm9",     "de": "Gemeinsam stärker",      "en": "Team Up",                "tier": "B"},
    {"id": "sm10",    "de": "Ungebrochen Verbündet",  "en": "Unbroken Bonds",         "tier": "B"},
    {"id": "sm3",     "de": "Brennende Schatten",     "en": "Burning Shadows",        "tier": "B"},
    # ── B-Tier Sword & Shield ──
    {"id": "swsh7",   "de": "Entwickelnde Himmel",    "en": "Evolving Skies",         "tier": "B"},
    {"id": "swsh45",  "de": "Strahlende Schicksale",  "en": "Shining Fates",          "tier": "B"},
    {"id": "cel25",   "de": "Celebrations",           "en": "Celebrations",           "tier": "B"},
    {"id": "swsh9",   "de": "Leuchtende Sterne",      "en": "Brilliant Stars",        "tier": "B"},
    {"id": "swsh8",   "de": "Fusionsangriff",         "en": "Fusion Strike",          "tier": "B"},
    {"id": "swsh6",   "de": "Eiskalte Herrschaft",    "en": "Chilling Reign",         "tier": "B"},
    # ── C-Tier Scarlet & Violet ──
    {"id": "sv3pt5",  "de": "Pokémon 151",            "en": "Pokemon 151",            "tier": "C"},
    {"id": "sv4",     "de": "Paradoxrift",            "en": "Paradox Rift",           "tier": "C"},
    {"id": "sv3",     "de": "Schwarze Flammen",       "en": "Obsidian Flames",        "tier": "C"},
    # ── Spezialsets ──
    {"id": "swsh12pt5", "de": "Zenit der Könige",     "en": "Crown Zenith",           "tier": "S"},
]

TIER_EMOJI = {"S": "🥇", "A": "🥈", "B": "🥉", "C": "🟢"}

# ──────────────────────────────────────────
#  API FUNKTIONEN
# ──────────────────────────────────────────
def get_top_karten(set_id: str, limit: int = 10) -> list:
    """Holt die teuersten Karten eines Sets via Pokemon TCG API."""
    try:
        url = (
            f"{TCG_API}/cards"
            f"?q=set.id:{set_id}"
            f"&orderBy=-cardmarket.prices.trendPrice"
            f"&pageSize={limit}"
        )
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json().get("data", [])
        elif r.status_code == 429:
            print("  Rate Limit – warte 10s...")
            time.sleep(10)
            return get_top_karten(set_id, limit)
    except Exception as e:
        print(f"  Fehler bei Set {set_id}: {e}")
    return []


def build_cm_url(card_name: str) -> str:
    """Baut einen Cardmarket-Suchlink."""
    import urllib.parse
    return (
        "https://www.cardmarket.com/de/Pokemon/Products/Singles"
        "?searchString=" + urllib.parse.quote(card_name)
    )


# ──────────────────────────────────────────
#  DEAL-ERKENNUNG
# ──────────────────────────────────────────
def analysiere_deals(karten: list, set_info: dict) -> list:
    deals = []
    for card in karten:
        preise  = card.get("cardmarket", {}).get("prices", {})
        # avg30 = 30-Tage-Durchschnitt als Referenzwert
        # avg1  = gestrige Preise als aktueller Wert
        # trendPrice als Fallback
        referenz = preise.get("avg30") or preise.get("trendPrice") or preise.get("averageSellPrice", 0)
        aktuell  = preise.get("avg1") or preise.get("lowPrice", 0)

        if not referenz or referenz < MIN_MARKTWERT:
            continue
        if not aktuell or aktuell <= 0:
            continue
        # Aktuell muss günstiger sein als Referenz
        if aktuell >= referenz:
            continue

        rabatt = (referenz - aktuell) / referenz
        if rabatt < RABATT_MIN:
            continue

        name     = card.get("name", "?")
        nummer   = card.get("number", "?")
        gesamt   = card.get("set", {}).get("printedTotal", "?")
        card_id  = card.get("id", "")
        # Direkter Cardmarket-Link: prices.pokemontcg.io redirectet auf CM
        # Wir ersetzen /en/ durch /de/ für deutschen Markt
        if card_id:
            cm_url = f"https://prices.pokemontcg.io/cardmarket/{card_id}"
        else:
            cm_url = build_cm_url(name)

        deals.append({
            "name":      name,
            "set_de":    set_info["de"],
            "set_en":    set_info["en"],
            "tier":      set_info["tier"],
            "nummer":    f"{nummer}/{gesamt}",
            "referenz":  referenz,
            "aktuell":   aktuell,
            "rabatt":    round(rabatt * 100),
            "cm_url":    cm_url,
        })

    return sorted(deals, key=lambda d: d["rabatt"], reverse=True)


# ──────────────────────────────────────────
#  NACHRICHT BAUEN
# ──────────────────────────────────────────
def deal_emoji(rabatt: int) -> str:
    if rabatt >= 60: return "🔥🔥"
    if rabatt >= 50: return "🔥"
    if rabatt >= 40: return "💰"
    return "⭐"


def build_deal_message(alle_deals: list) -> str:
    heute  = datetime.now().strftime("%d.%m.%Y %H:%M")
    header = (
        f"🃏 <b>DealFinder – Pokémon Sets</b>\n"
        f"📅 {heute}\n"
        f"────────────────────\n"
    )

    if not alle_deals:
        return header + "ℹ️ Heute keine Deals ≥33% unter Trendpreis.\n\n🤖 JensHQ DealFinder"

    header += f"🎯 <b>{len(alle_deals)} Deal(s) gefunden!</b>\n\n"
    lines   = []

    for i, deal in enumerate(alle_deals, 1):
        tier_e  = TIER_EMOJI.get(deal["tier"], "")
        d_emoji = deal_emoji(deal["rabatt"])
        block   = f"{d_emoji} <b>{i}. {deal['name']}</b>\n"
        block  += f"   {tier_e} {deal['set_de']} | #{deal['nummer']}\n"
        block  += f"   📈 30-Tage-Schnitt: <b>{deal['referenz']:.2f}€</b>\n"
        block  += f"   🏷️ Aktuell (gestern): <b>{deal['aktuell']:.2f}€</b>\n"
        block  += f"   📉 <b>{deal['rabatt']}% unter Trendpreis</b>\n"
        block  += f"   🔗 <a href='{deal['cm_url']}'>Cardmarket suchen</a>\n"
        lines.append(block)

    body   = "\n".join(lines)
    if len(alle_deals) > 999:
        body += f"\n<i>... und {len(alle_deals) - 10} weitere Deals</i>\n"

    footer = "\n────────────────────\n🤖 JensHQ DealFinder"
    return header + body + footer


# ──────────────────────────────────────────
#  HAUPTFUNKTION
# ──────────────────────────────────────────
def run_dealfinder():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] DealFinder Pokémon Sets gestartet...")
    print(f"Sets: {len(SETS_WATCHLIST)} | Min. Marktwert: {MIN_MARKTWERT}€ | Rabatt: ≥{int(RABATT_MIN*100)}%\n")

    alle_deals = []
    gesehen    = set()

    for set_info in SETS_WATCHLIST:
        print(f"  [{set_info['tier']}] {set_info['de']} ({set_info['id']})...")
        karten = get_top_karten(set_info["id"], limit=10)
        deals  = analysiere_deals(karten, set_info)

        set_count = 0
        for deal in deals:
            if set_count >= 1:  # Max 1 pro Set
                break
            key = f"{deal['name']}_{deal['set_en']}"
            if key not in gesehen:
                gesehen.add(key)
                alle_deals.append(deal)
                set_count += 1
                print(f"    ✅ {deal['name']} – {deal['rabatt']}% Rabatt ({deal['aktuell']:.2f}€ statt {deal['referenz']:.2f}€)")

        time.sleep(0.3)

    print(f"\n{len(alle_deals)} Deal(s) gesamt gefunden.")

    msg     = build_deal_message(alle_deals)
    success = send_deal_message(msg)

    if success:
        print("✅ Deal-Bericht gesendet.")
    else:
        print("❌ Fehler beim Senden.")

    return alle_deals


if __name__ == "__main__":
    run_dealfinder()