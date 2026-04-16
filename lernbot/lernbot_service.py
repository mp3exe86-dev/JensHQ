```python
"""
lernbot_service.py
JensHQ – LernBot Service
Läuft dauerhaft, empfängt Antworten per Polling, trackt Fortschritt
Start: python lernbot_service.py
"""

import requests
import json
import os
import sys
import time
import random
from datetime import datetime

import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_MOD  = _os.path.dirname(_os.path.abspath(__file__))
import sys as _sys
_sys.path.insert(0, _ROOT)
_sys.path.insert(0, _MOD)
from lernbot_quiz import FRAGEN, THEMEN, get_fragen_by_thema, ist_mehrfachauswahl, ist_antwort_korrekt
from lernbot_lektionen import LEKTIONEN, THEMEN_LEKTIONEN, get_lektion_by_id

# ──────────────────────────────────────────
#  KONFIGURATION
# ──────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

TOKEN    = os.getenv("LERNBOT_TOKEN", "")
CHAT_ID  = int(os.getenv("CHAT_ID", "8656887627"))
API_URL  = f"https://api.telegram.org/bot{TOKEN}"
TRACKER  = os.path.join(os.getenv("BASE_PATH", "/home/jens/JobAgent"), "shared", "daten", "lernbot_tracker.json")
POLL_SEC = 3

# ──────────────────────────────────────────
#  TRACKER: LADEN & SPEICHERN
# ──────────────────────────────────────────
def load_tracker() -> dict:
    if os.path.exists(TRACKER):
        try:
            with open(TRACKER, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Neu anlegen
    return {
        "letzte_frage_id": None,
        "warte_auf_antwort": False,
        "themen": {t: {"richtig": 0, "falsch": 0, "gesehen": []} for t in THEMEN},
        "gesamt_richtig": 0,
        "gesamt_falsch": 0,
        "last_update_id": 0,
        "gesendete_lektionen": []
    }

def save_tracker(tracker: dict):
    os.makedirs(os.path.dirname(TRACKER), exist_ok=True)
    with open(TRACKER, "w", encoding="utf-8") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────
#  TELEGRAM: SENDEN & EMPFANGEN
# ──────────────────────────────────────────
def send(text: str, parse_mode: str = "HTML") -> bool:
    try:
        r = requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[FEHLER] Senden: {e}")
        return False

def get_updates(offset: int) -> list:
    try:
        r = requests.get(f"{API_URL}/getUpdates", params={
            "offset": offset,
            "timeout": 2
        }, timeout=10)
        data = r.json()
        return data.get("result", []) if data.get("ok") else []
    except Exception:
        return []

# ──────────────────────────────────────────
#  NÄCHSTE FRAGE AUSWÄHLEN
# ──────────────────────────────────────────
def naechste_frage(tracker: dict) -> dict:
    """
    Wählt die nächste Frage intelligent aus:
    - Schwache Themen (hohe Fehlerquote) bevorzugt
    - Noch nicht gesehene Fragen bevorzugt
    - Bereits falsch beantwortete Fragen kommen wieder
    """
    # Alle gesehenen IDs
    alle_gesehen = set()
    for t_data in tracker["themen"].values():
        alle_gesehen.update(t_data.get("gesehen", []))

    # Ungesehene Fragen
    ungesehen = [f for f in FRAGEN if f["id"] not in alle_gesehen]

    if ungesehen:
        # Thema mit schlechtester Quote bevorzugen
        def thema_score(thema):
            t = tracker["themen"].get(thema, {"richtig": 0, "falsch": 0})
            total = t["richtig"] + t["falsch"]
            if total == 0:
                return 0.5  # Noch nicht gespielt → mittlere Prio
            return t["falsch"] / total  # Höhere Fehlerquote → höhere Prio

        # Gewichtete Auswahl nach Thema-Schwäche
        ungesehen_nach_thema = {}
        for f in ungesehen:
            ungesehen_nach_thema.setdefault(f["thema"], []).append(f)

        themen_gewichtet = [(t, thema_score(t)) for t in ungesehen_nach_thema]
        themen_gewichtet.sort(key=lambda x: x[1], reverse=True)

        # Top-3 schwächste Themen, zufällig aus denen wählen
        top_themen = [t for t, _ in themen_gewichtet[:3]]
        gewaehltes_thema = random.choice(top_themen)
        return random.choice(ungesehen_nach_thema[gewaehltes_thema])
    else:
        # Alle gesehen → schwächstes Thema wiederholen
        schwachstes = min(
            THEMEN,
            key=lambda t: (
                tracker["themen"][t]["richtig"] /
                max(1, tracker["themen"][t]["richtig"] + tracker["themen"][t]["falsch"])
            )
        )
        # Reset gesehen für dieses Thema
        tracker["themen"][schwachstes]["gesehen"] = []
        save_tracker(tracker)
        fragen = get_fragen_by_thema(schwachstes)
        return random.choice(fragen)

# ──────────────────────────────────────────
#  FRAGE SENDEN
# ────
def frage_senden(tracker: dict) -> dict:
    frage = naechste_frage(tracker)

    mehrfach = ist_mehrfachauswahl(frage)
    hinweis  = "<i>⚠️ Mehrfachauswahl! Antworte z.B. mit AB oder BC</i>" if mehrfach else "<i>Antworte mit A, B, C oder D</i>"

    text = (
        f"🧠 <b>AZ-900 Quizfrage</b>\n"
        f"📚 Thema: {frage['thema']}\n"
        f"────────────────────\n"
        f"<b>{frage['frage']}</b>\n\n"
        f"🅐 {frage['antworten']['A']}\n"
        f"🅑 {frage['antworten']['B']}\n"
        f"🅒 {frage['antworten']['C']}\n"
        f"🅓 {frage['antworten']['D']}\n\n"
        f"{hinweis}"
    )

    if send(text):
        tracker["letzte_frage_id"] = frage["id"]
        tracker["warte_auf_antwort"] = True
        # Als gesehen markieren
        tracker["themen"][frage["thema"]]["gesehen"].append(frage["id"])
        save_tracker(tracker)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Frage gesendet: {frage['id']}")

    return tracker

def pause_frage():
    global CHAT_ID
    tracker = load_tracker()
    if tracker["warte_auf_antwort"]:
        tracker["warte_auf_antwort"] = False
        save_tracker(tracker)
        send(f"⏸️ Pause! Die aktuelle Frage wurde gestoppt.", parse_mode="HTML")
        CHAT_ID = 8656887627 #Zurücksetzen auf den alten Chat ID
    else:
        send("Die Pause wurde bereits aktiviert.", parse_mode="HTML")

# ──────────────────────────────────────────
#  STARTER
# ──────────────────────────────────────────
def main():
    tracker = load_tracker()
    print("LernBot Service gestartet...")
    while True:
        update = get_updates(0)
        if update:
            for u in update:
                if u["text"] == "/start":
                    tracker = load_tracker()
                    send("Hallo! Ich bin dein LernBot. Starte mit /quiz.", parse_mode="HTML")
                elif u["text"] == "/pauseAirbnb":
                    pause_frage()
                elif u["text"].startswith("/quiz"):
                    tracker = frage_senden(tracker)
                elif u["text"] == "/help":
                    send("Verfügbare Befehle: /start, /pauseAirbnb, /quiz, /help", parse_mode="HTML")
        else:
            continue
        
        #Überprüfen ob die Variable ChatID verändert wurde
        if CHAT_ID != 8656887627:
            print(f"ChatID wurde geändert auf {CHAT_ID}")
            CHAT_ID = 8656887627


if __name__ == "__main__":
    main()
