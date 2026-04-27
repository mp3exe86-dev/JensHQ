#!/usr/bin/env python3
# habits_check.py — Täglicher Habit Check mit Gamification & Habit-Gate

import json
import os
import random
import requests
import sys
import time
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv('/home/jens/JobAgent/.env')

BOT_TOKEN  = os.getenv("JAMES_TOKEN", "")
CHAT_ID    = os.getenv("CHAT_ID", "8656887627")
API_URL    = f"https://api.telegram.org/bot{BOT_TOKEN}"

HABITS_DATEI   = "/home/jens/JobAgent/daten/habits.json"
TRACKER_DATEI  = "/home/jens/JobAgent/daten/habits_tracker.json"
DEHN_DATEI     = "/home/jens/JobAgent/daten/dehn_tipps.json"
GATE_DATEI     = "/home/jens/JobAgent/daten/habit_gate.json"

# ═══════════════════════════════════════
# HABITS DEFINITION
# ═══════════════════════════════════════

HABITS = [
    {"id": "sport",       "emoji": "💪", "name": "Sport / Krafttraining",    "ziel_woche": 3},
    {"id": "liegestuetze","emoji": "🤸", "name": "100 Liegestütze",          "ziel_woche": 5},
    {"id": "dehnen",      "emoji": "🧘", "name": "Dehnen / Mobilität",        "ziel_woche": 3},
    {"id": "az900",       "emoji": "📚", "name": "AZ-900 gelernt",            "ziel_woche": 4},
    {"id": "jenshq",      "emoji": "🤖", "name": "An JensHQ gearbeitet",      "ziel_woche": 4},
    {"id": "lesen",       "emoji": "📖", "name": "Gelesen (mind. 10 Min)",    "ziel_woche": 4},
    {"id": "bett",        "emoji": "😴", "name": "Vor 23 Uhr ins Bett",       "ziel_woche": 6},
]

# Habit-Gate: welche Features brauchen welche Habits
HABIT_GATES = {
    "SEi8 + Proxmox":         {"min_score": 80, "wochen": 2},
    "Hermes Integration":      {"min_score": 80, "wochen": 2},
    "Dev Mode vollständig":    {"min_score": 80, "wochen": 3},
    "Pokemon Chroniken":       {"habit": "az900", "min_tage": 4},
    "YouTube/GitHub Launch":   {"min_score": 80, "wochen": 4},
}

# ═══════════════════════════════════════
# HILFSFUNKTIONEN
# ═══════════════════════════════════════

def send(text: str, keyboard=None):
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if keyboard:
        payload["reply_markup"] = keyboard
    try:
        requests.post(f"{API_URL}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        print(f"[Send Fehler] {e}")

def lade_json(pfad, default):
    try:
        with open(pfad, "r") as f:
            return json.load(f)
    except:
        return default

def speichere_json(pfad, daten):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "w") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)

def lade_tracker() -> dict:
    return lade_json(TRACKER_DATEI, {"wochen": {}, "gesamt": {}})

def lade_gate() -> dict:
    return lade_json(GATE_DATEI, {"freigeschaltet": [], "wochen_scores": []})

def kw_key() -> str:
    heute = date.today()
    kw = heute.isocalendar()[1]
    return f"{heute.year}_KW{kw}"

def berechne_wochen_score(tracker: dict) -> dict:
    kw = kw_key()
    woche = tracker.get("wochen", {}).get(kw, {})
    scores = {}
    for habit in HABITS:
        hid = habit["id"]
        tage = woche.get(hid, [])
        erreicht = len(tage)
        ziel = habit["ziel_woche"]
        prozent = int((erreicht / ziel) * 100) if ziel > 0 else 0
        scores[hid] = {"erreicht": erreicht, "ziel": ziel, "prozent": min(prozent, 100)}
    gesamt = int(sum(s["prozent"] for s in scores.values()) / len(scores)) if scores else 0
    return {"habits": scores, "gesamt": gesamt}

def heute_erledigt(tracker: dict, habit_id: str) -> bool:
    kw = kw_key()
    heute = str(date.today())
    tage = tracker.get("wochen", {}).get(kw, {}).get(habit_id, [])
    return heute in tage

def markiere_habit(tracker: dict, habit_id: str, erledigt: bool):
    kw = kw_key()
    heute = str(date.today())
    if "wochen" not in tracker:
        tracker["wochen"] = {}
    if kw not in tracker["wochen"]:
        tracker["wochen"][kw] = {}
    if habit_id not in tracker["wochen"][kw]:
        tracker["wochen"][kw][habit_id] = []

    tage = tracker["wochen"][kw][habit_id]
    if erledigt and heute not in tage:
        tage.append(heute)
    elif not erledigt and heute in tage:
        tage.remove(heute)

# ═══════════════════════════════════════
# DEHN TIPP
# ═══════════════════════════════════════

def hole_dehn_tipp() -> str:
    tipps = lade_json(DEHN_DATEI, [])
    if not tipps:
        return ""
    tipp = random.choice(tipps)
    return (
        f"\n🧘 <b>Dehn-Tipp heute — {tipp['bereich']}:</b>\n"
        f"<b>{tipp['name']}</b> ({tipp['dauer']})\n\n"
        f"{tipp['anleitung']}\n\n"
        f"🎯 Ziel: {tipp['ziel']}"
    )

# ═══════════════════════════════════════
# HABIT GATE CHECK
# ═══════════════════════════════════════

def pruefe_gates(tracker: dict, gate: dict):
    score_daten = berechne_wochen_score(tracker)
    gesamt = score_daten["gesamt"]

    # Wochen-Scores speichern
    wochen_scores = gate.get("wochen_scores", [])
    kw = kw_key()
    if not wochen_scores or wochen_scores[-1]["kw"] != kw:
        wochen_scores.append({"kw": kw, "score": gesamt})
        gate["wochen_scores"] = wochen_scores[-8:]  # max 8 Wochen

    # Gates prüfen
    neue_freischaltungen = []
    for feature, bedingung in HABIT_GATES.items():
        if feature in gate.get("freigeschaltet", []):
            continue

        if "wochen" in bedingung:
            noetige_wochen = bedingung["wochen"]
            min_score = bedingung["min_score"]
            gute_wochen = sum(1 for w in wochen_scores if w["score"] >= min_score)
            if gute_wochen >= noetige_wochen:
                gate["freigeschaltet"].append(feature)
                neue_freischaltungen.append(feature)
        elif "habit" in bedingung:
            hid = bedingung["habit"]
            min_tage = bedingung["min_tage"]
            erreicht = score_daten["habits"].get(hid, {}).get("erreicht", 0)
            if erreicht >= min_tage:
                gate["freigeschaltet"].append(feature)
                neue_freischaltungen.append(feature)

    speichere_json(GATE_DATEI, gate)
    return neue_freischaltungen

# ═══════════════════════════════════════
# ABEND CHECK SENDEN
# ═══════════════════════════════════════

def sende_abend_check():
    tracker = lade_tracker()
    wochentag = ["Mo","Di","Mi","Do","Fr","Sa","So"][date.today().weekday()]
    datum = date.today().strftime("%d.%m.%Y")

    msg = f"🌙 <b>Habit Check — {wochentag} {datum}</b>\n\nWas hast du heute geschafft?\n"

    keyboard = {"inline_keyboard": []}
    for habit in HABITS:
        hid = habit["id"]
        erledigt = heute_erledigt(tracker, hid)
        check = "✅" if erledigt else "⬜"
        keyboard["inline_keyboard"].append([
            {"text": f"{check} {habit['emoji']} {habit['name']}", 
             "callback_data": f"habit_toggle_{hid}"}
        ])

    keyboard["inline_keyboard"].append([
        {"text": "💾 Speichern & Auswerten", "callback_data": "habit_save"}
    ])

    send(msg, keyboard)

    # Dehn Tipp wenn Dehnen noch nicht erledigt
    if not heute_erledigt(tracker, "dehnen"):
        tipp = hole_dehn_tipp()
        if tipp:
            time.sleep(2)
            send(f"💡 Du hast heute noch nicht gedehnt:{tipp}")

# ═══════════════════════════════════════
# HABIT TOGGLE (Callback von James)
# ═══════════════════════════════════════

def toggle_habit(habit_id: str):
    tracker = lade_tracker()
    erledigt = heute_erledigt(tracker, habit_id)
    markiere_habit(tracker, habit_id, not erledigt)
    speichere_json(TRACKER_DATEI, tracker)

    habit = next((h for h in HABITS if h["id"] == habit_id), None)
    if habit:
        status = "✅ Abgehakt" if not erledigt else "⬜ Zurückgenommen"
        send(f"{status}: {habit['emoji']} {habit['name']}")

# ═══════════════════════════════════════
# AUSWERTUNG
# ═══════════════════════════════════════

def sende_auswertung():
    tracker = lade_tracker()
    gate = lade_gate()
    score_daten = berechne_wochen_score(tracker)
    gesamt = score_daten["gesamt"]
    balken = "█" * (gesamt // 10) + "░" * (10 - gesamt // 10)

    msg = f"📊 <b>Habit Auswertung diese Woche</b>\n\n{balken} {gesamt}%\n\n"

    for habit in HABITS:
        hid = habit["id"]
        s = score_daten["habits"].get(hid, {})
        erreicht = s.get("erreicht", 0)
        ziel = s.get("ziel", 0)
        check = "✅" if erreicht >= ziel else "⚠️" if erreicht > 0 else "❌"
        msg += f"{check} {habit['emoji']} {habit['name']}: {erreicht}/{ziel}\n"

    # Gate Check
    neue = pruefe_gates(tracker, gate)
    if neue:
        msg += "\n🔓 <b>FEATURE FREIGESCHALTET!</b>\n"
        for f in neue:
            msg += f"• {f}\n"
        msg += "\nGlückwunsch! Du hast es dir verdient. 🎉"

    # Gate Status
    msg += "\n\n🔒 <b>Noch gesperrt:</b>\n"
    wochen_scores = gate.get("wochen_scores", [])
    for feature, bedingung in HABIT_GATES.items():
        if feature in gate.get("freigeschaltet", []):
            continue
        if "wochen" in bedingung:
            gute = sum(1 for w in wochen_scores if w["score"] >= bedingung["min_score"])
            msg += f"• {feature}: {gute}/{bedingung['wochen']} Wochen >{bedingung['min_score']}%\n"
        elif "habit" in bedingung:
            hid = bedingung["habit"]
            erreicht = score_daten["habits"].get(hid, {}).get("erreicht", 0)
            msg += f"• {feature}: {erreicht}/{bedingung['min_tage']} Tage {hid}\n"

    send(msg)

# ═══════════════════════════════════════
# WOCHEN SCORE (Sonntags)
# ═══════════════════════════════════════

def sende_wochen_score():
    sende_auswertung()

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

if __name__ == "__main__":
    modus = sys.argv[1] if len(sys.argv) > 1 else "check"

    if modus == "check":
        sende_abend_check()
    elif modus == "score":
        sende_wochen_score()
    elif modus == "toggle":
        habit_id = sys.argv[2]
        toggle_habit(habit_id)
    elif modus == "auswerten":
        sende_auswertung()
