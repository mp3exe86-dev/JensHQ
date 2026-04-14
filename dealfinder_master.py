"""
dealfinder_master.py
JensHQ - DealFinder Master
Ruft alle Module auf, sendet Bericht nach Kategorie getrennt per JensDealBot
"""

import sys
import time
import json
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, r"/home/jens/JobAgent")
from telegram_notifier import send_deal_message

# ══════════════════════════════════════════
#  GESEHENE DEALS (Duplikat-Filter, 3 Tage)
# ══════════════════════════════════════════
SEEN_DEALS_FILE = os.path.join(os.path.dirname(__file__), "daten", "seen_deals.json")
SEEN_DEALS_TTL  = 3  # Tage

def _deal_key(deal: dict) -> str:
    url = deal.get("url") or deal.get("link") or deal.get("cm_url") or ""
    if url:
        return url
    titel = str(deal.get("titel") or deal.get("name") or "").strip()[:60]
    preis = str(deal.get("preis") or deal.get("aktuell") or "")
    return f"{titel}_{preis}"

def load_seen_deals() -> dict:
    if os.path.exists(SEEN_DEALS_FILE):
        try:
            with open(SEEN_DEALS_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_seen_deals(seen: dict):
    os.makedirs(os.path.dirname(SEEN_DEALS_FILE), exist_ok=True)
    with open(SEEN_DEALS_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)

def filter_neue_deals(deals: list) -> tuple[list, dict]:
    """Gibt nur neue Deals zurück und das aktualisierte seen-Dict."""
    seen  = load_seen_deals()
    heute = date.today().isoformat()
    cutoff = (date.today() - timedelta(days=SEEN_DEALS_TTL)).isoformat()

    # Alte Einträge bereinigen
    seen = {k: v for k, v in seen.items() if v >= cutoff}

    neue = []
    for deal in deals:
        key = _deal_key(deal)
        if key and key not in seen:
            neue.append(deal)
            seen[key] = heute

    return neue, seen

try:
    from dealfinder_pokemon       import run_dealfinder         as scan_pokemon
    POKEMON_AKTIV = True
except ImportError:
    POKEMON_AKTIV = False

try:
    from dealfinder_kleinanzeigen import run_kleinanzeigen_scan as scan_kleinanzeigen
    KLEINANZEIGEN_AKTIV = True
except ImportError:
    KLEINANZEIGEN_AKTIV = False

try:
    from dealfinder_cardmarket    import run_cardmarket_scan    as scan_cardmarket
    CARDMARKET_AKTIV = True
except ImportError:
    CARDMARKET_AKTIV = False

# ══════════════════════════════════════════
#  KATEGORIEN
# ══════════════════════════════════════════
KATEGORIEN = [
    ("Pokemon",  "Pokémon"),
    ("MTG",      "Magic the Gathering"),
    ("YGO",      "Yu-Gi-Oh"),
    ("Konsolen", "Konsolen"),
    ("Retro",    "Retro Gaming"),
    ("Lego",     "Lego"),
]

def rabatt_emoji(rabatt) -> str:
    rabatt = int(rabatt or 0)
    if rabatt >= 60: return "🔥🔥"
    if rabatt >= 50: return "🔥"
    if rabatt >= 40: return "🟠"
    return "🟡"

# ══════════════════════════════════════════
#  ÜBERSICHTS-NACHRICHT
# ══════════════════════════════════════════
def build_uebersicht(alle_deals: list, quellen: list) -> str:
    heute = datetime.now().strftime("%d.%m.%Y %H:%M")

    nach_kat = {}
    for d in alle_deals:
        kat = d.get("kategorie", "Sonstiges")
        nach_kat[kat] = nach_kat.get(kat, 0) + 1

    msg  = f"<b>DealFinder Tagesbericht</b>\n"
    msg += f"Datum: {heute}\n"
    msg += f"Quellen: {', '.join(quellen)}\n"
    msg += f"────────────────────\n"

    if not alle_deals:
        msg += "Heute keine Deals gefunden.\n"
        msg += "────────────────────\n"
        msg += "JensHQ DealFinder"
        return msg

    msg += f"<b>{len(alle_deals)} Deal(s) gefunden:</b>\n\n"

    for kat_key, kat_label in KATEGORIEN:
        count = nach_kat.get(kat_key, 0)
        if count > 0:
            msg += f"{kat_label}: <b>{count} Deal(s)</b>\n"

    msg += f"────────────────────\n"
    msg += f"<i>Details folgen je Kategorie</i>\n"
    msg += f"JensHQ DealFinder"
    return msg

# ══════════════════════════════════════════
#  KATEGORIE-NACHRICHT
# ══════════════════════════════════════════
def build_kategorie_nachricht(kat_key: str, kat_label: str, deals: list) -> str:
    msg  = f"<b>{kat_label}</b>\n"
    msg += f"────────────────────\n"
    msg += f"<b>{len(deals)} Deal(s)</b>\n\n"

    for i, deal in enumerate(deals[:8], 1):
        # Felder normalisieren — verschiedene Scanner nutzen verschiedene Keys
        titel    = deal.get("titel") or deal.get("name") or deal.get("karte") or "Unbekannt"
        preis    = float(deal.get("preis") or deal.get("angebotspreis") or deal.get("aktuell") or 0)
        referenz = float(deal.get("referenz") or deal.get("trendpreis") or deal.get("marktwert") or 0)
        rabatt   = int(deal.get("rabatt_pct") or deal.get("rabatt") or 0)
        url      = deal.get("url") or deal.get("link") or deal.get("cm_url") or ""
        quelle   = deal.get("quelle") or deal.get("source") or ""
        vb_str   = " <i>[VB]</i>" if deal.get("vb") else ""

        emoji = rabatt_emoji(rabatt)

        msg += f"{emoji} <b>{i}. {str(titel)[:45]}</b>\n"
        msg += f"   {preis:.0f} EUR"
        if referenz:
            msg += f" | Ref: {referenz:.0f} EUR"
        msg += f" | <b>-{rabatt}%</b>{vb_str}\n"
        if url:
            msg += f"   <a href='{url}'>Zum Angebot</a>"
        if quelle:
            msg += f" <i>({quelle})</i>"
        msg += "\n\n"

    if len(deals) > 8:
        msg += f"<i>... und {len(deals) - 8} weitere Deals</i>\n"

    return msg

# ══════════════════════════════════════════
#  HAUPTFUNKTION
# ══════════════════════════════════════════
def run_master():
    print(f"\n{'='*50}")
    print(f"JensHQ DealFinder Master - {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"{'='*50}\n")

    alle_deals = []
    quellen    = []

    if POKEMON_AKTIV:
        print("-- Modul 1: Pokemon --")
        try:
            deals = scan_pokemon()
            for d in deals:
                d.setdefault("kategorie", "Pokemon")
            alle_deals.extend(deals)
            quellen.append("PokeTrace")
        except Exception as e:
            print(f"  Fehler: {e}")
        time.sleep(2)

    if KLEINANZEIGEN_AKTIV:
        print("\n-- Modul 2: Kleinanzeigen --")
        try:
            deals = scan_kleinanzeigen()
            alle_deals.extend(deals)
            quellen.append("Kleinanzeigen")
        except Exception as e:
            print(f"  Fehler: {e}")
        time.sleep(2)

    if CARDMARKET_AKTIV:
        print("\n-- Modul 3: Cardmarket --")
        try:
            deals = scan_cardmarket()
            alle_deals.extend(deals)
            quellen.append("Cardmarket")
        except Exception as e:
            print(f"  Fehler: {e}")

    # Nur neue Deals (Duplikat-Filter, 3 Tage)
    neue_deals, seen_updated = filter_neue_deals(alle_deals)
    print(f"  Filter: {len(alle_deals)} Deals gefunden, {len(neue_deals)} neu (nicht in den letzten {SEEN_DEALS_TTL} Tagen gesehen)")
    save_seen_deals(seen_updated)
    alle_deals = neue_deals

    # Sortieren nach Rabatt
    alle_deals.sort(key=lambda d: int(d.get("rabatt_pct") or d.get("rabatt") or 0), reverse=True)

    print(f"\n{'='*50}")
    print(f"GESAMT: {len(alle_deals)} neue Deals | Quellen: {', '.join(quellen)}")
    print(f"{'='*50}\n")

    # Deals nach Kategorie gruppieren
    nach_kat = {}
    for d in alle_deals:
        kat = d.get("kategorie", "Sonstiges")
        nach_kat.setdefault(kat, []).append(d)

    # 1. Übersichtsnachricht
    uebersicht = build_uebersicht(alle_deals, quellen)
    send_deal_message(uebersicht)
    time.sleep(1)

# 2. Je Kategorie eine Nachricht
    for kat_key, kat_label in KATEGORIEN:
        if kat_key == "Pokemon":
            continue  # Pokemon sendet eigenen Block
        deals = nach_kat.get(kat_key, [])
        if not deals:
            continue
        msg = build_kategorie_nachricht(kat_key, kat_label, deals)
        success = send_deal_message(msg)
        print(f"{'OK' if success else 'FEHLER'} {kat_label}: {len(deals)} Deals gesendet.")
        time.sleep(1.5)

    return alle_deals


if __name__ == "__main__":
    run_master()