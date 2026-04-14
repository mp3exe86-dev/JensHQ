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
# ──────────────────────────────────────────
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

# ──────────────────────────────────────────
#  ANTWORT VERARBEITEN
# ──────────────────────────────────────────
def antwort_verarbeiten(tracker: dict, antwort_raw: str) -> dict:
    from lernbot_quiz import get_frage_by_id
    frage = get_frage_by_id(tracker["letzte_frage_id"])

    if not frage:
        send("⚠️ Konnte die Frage nicht laden. Tippe /frage für eine neue.")
        return tracker

    thema = frage["thema"]

    # Mehrfachauswahl: "AB" oder "A B" oder "A,B" → ["A", "B"]
    if ist_mehrfachauswahl(frage):
        antwort_clean = antwort_raw.upper().replace(",", "").replace(" ", "")
        antwort = sorted([c for c in antwort_clean if c in "ABCD"])
        richtig = sorted(frage["richtig"])
        korrekt = antwort == richtig
        richtig_str = "".join(richtig)
        antwort_str = "".join(antwort)
    else:
        antwort = antwort_raw.upper().strip()
        richtig = frage["richtig"]
        korrekt = antwort == richtig
        richtig_str = richtig
        antwort_str = antwort

    if korrekt:
        tracker["themen"][thema]["richtig"] += 1
        tracker["gesamt_richtig"] += 1
        antwort_text = frage["antworten"][richtig]
        msg = (
            f"✅ <b>Richtig!</b>\n\n"
            f"<b>{richtig}: {antwort_text}</b>\n\n"
            f"💡 {frage['erklaerung']}\n\n"
            f"Tippe /frage für die nächste Frage oder /status für deinen Fortschritt."
        )
    else:
        tracker["themen"][thema]["falsch"] += 1
        tracker["gesamt_falsch"] += 1
        richtig_text = frage["antworten"][richtig]
        falsch_text  = frage["antworten"].get(antwort, "–")
        msg = (
            f"❌ <b>Leider falsch.</b>\n\n"
            f"Du hast gewählt: <b>{antwort}: {falsch_text}</b>\n"
            f"Richtig wäre: <b>{richtig}: {richtig_text}</b>\n\n"
            f"💡 {frage['erklaerung']}\n\n"
            f"Tippe /frage für die nächste Frage oder /status für deinen Fortschritt."
        )

    send(msg)
    tracker["warte_auf_antwort"] = False
    tracker["letzte_frage_id"]   = None
    save_tracker(tracker)
    return tracker

# ──────────────────────────────────────────
#  STATUS SENDEN
# ──────────────────────────────────────────
def status_senden(tracker: dict):
    gesamt_r = tracker["gesamt_richtig"]
    gesamt_f = tracker["gesamt_falsch"]
    gesamt   = gesamt_r + gesamt_f
    gesamt_pct = round(gesamt_r / gesamt * 100) if gesamt > 0 else 0

    thema_emojis = {
        "Cloud-Konzepte":        "☁️",
        "SLA-Regeln":            "📋",
        "Identity & Security":   "🔐",
        "Pricing & Cost Management": "💰",
        "Governance":            "🏛️",
        "Azure Dienste":         "⚙️",
    }

    lines = ["📊 <b>Dein AZ-900 Fortschritt</b>\n────────────────────"]

    schwachstes_thema = None
    schwachstes_pct   = 101

    for thema in THEMEN:
        t   = tracker["themen"].get(thema, {"richtig": 0, "falsch": 0})
        r   = t["richtig"]
        f   = t["falsch"]
        tot = r + f
        pct = round(r / tot * 100) if tot > 0 else 0

        balken = "█" * (pct // 10) + "░" * (10 - pct // 10)
        emoji  = thema_emojis.get(thema, "📌")

        lines.append(f"{emoji} {thema}\n   {balken} {pct}%  ({r}/{tot})")

        if tot > 0 and pct < schwachstes_pct:
            schwachstes_pct   = pct
            schwachstes_thema = thema

    lines.append("────────────────────")
    lines.append(f"🎯 Gesamt: <b>{gesamt_pct}%</b> | {gesamt_r}/{gesamt} Fragen")

    if schwachstes_thema:
        lines.append(f"📌 Fokus: <b>{schwachstes_thema}</b> ({schwachstes_pct}%) 🎯")

    send("\n".join(lines))

# ──────────────────────────────────────────
#  LEKTION SENDEN
# ──────────────────────────────────────────
def naechste_lektion(tracker: dict) -> dict:
    gesendete = set(tracker.get("gesendete_lektionen", []))
    alle_ids  = [l["id"] for l in LEKTIONEN]
    ungesehen = [lid for lid in alle_ids if lid not in gesendete]
    if not ungesehen:
        # Alle gesehen → reset
        tracker["gesendete_lektionen"] = []
        gesendete = set()
        ungesehen = alle_ids
    lektion_id = random.choice(ungesehen)
    return get_lektion_by_id(lektion_id)

def lektion_senden(tracker: dict) -> dict:
    lektion = naechste_lektion(tracker)
    if not lektion:
        send("⚠️ Keine Lektion gefunden.")
        return tracker

    hat_frage = "frage" in lektion and "antworten" in lektion
    text = (
        f"📖 <b>Tageslektion – {lektion['thema']}</b>\n"
        f"<b>{lektion['titel']}</b>\n"
        f"────────────────────\n"
        f"{lektion['inhalt']}"
    )
    if hat_frage:
        antworten = lektion["antworten"]
        buchstaben = ["A", "B", "C", "D"]
        text += f"\n\n❓ <b>Mini-Quiz:</b> {lektion['frage']}\n"
        for i, a in enumerate(antworten[:4]):
            text += f"  {buchstaben[i]}) {a}\n"
        text += "\n<i>Antworte mit A, B, C oder D</i>"

    if send(text):
        tracker.setdefault("gesendete_lektionen", []).append(lektion["id"])
        if hat_frage:
            tracker["letzte_lektion_id"]      = lektion["id"]
            tracker["warte_auf_lektion_antwort"] = True
        save_tracker(tracker)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Lektion gesendet: {lektion['id']}")
    return tracker

def lektion_antwort_verarbeiten(tracker: dict, antwort_raw: str) -> dict:
    lektion_id = tracker.get("letzte_lektion_id")
    lektion = get_lektion_by_id(lektion_id)
    if not lektion or "frage" not in lektion:
        tracker["warte_auf_lektion_antwort"] = False
        return tracker

    antworten = lektion["antworten"]
    richtig_idx = lektion.get("richtig", 0)
    buchstaben = ["A", "B", "C", "D"]
    antwort = antwort_raw.upper().strip()

    if antwort in buchstaben and buchstaben.index(antwort) == richtig_idx:
        msg = (
            f"✅ <b>Richtig!</b>\n\n"
            f"💡 {lektion.get('erklaerung', '')}\n\n"
            f"Tippe /lektionen für die nächste Lektion."
        )
    else:
        richtig_buchstabe = buchstaben[richtig_idx]
        richtige_antwort  = antworten[richtig_idx] if richtig_idx < len(antworten) else "–"
        msg = (
            f"❌ <b>Leider falsch.</b>\n\n"
            f"Richtig wäre: <b>{richtig_buchstabe}) {richtige_antwort}</b>\n\n"
            f"💡 {lektion.get('erklaerung', '')}\n\n"
            f"Tippe /lektionen für die nächste Lektion."
        )

    send(msg)
    tracker["warte_auf_lektion_antwort"] = False
    tracker["letzte_lektion_id"]         = None
    save_tracker(tracker)
    return tracker


# ──────────────────────────────────────────
#  HAUPTSCHLEIFE
# ──────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] JensLernBot Service gestartet. Lausche auf Nachrichten...")
    send("🤖 <b>LernBot gestartet!</b>\n\nVerfügbare Befehle:\n/frage – Neue Quizfrage\n/status – Dein Fortschritt\n/hilfe – Alle Befehle")

    tracker = load_tracker()

    while True:
        try:
            updates = get_updates(tracker["last_update_id"] + 1)

            for update in updates:
                tracker["last_update_id"] = update["update_id"]

                msg = update.get("message", {})
                if not msg:
                    continue

                chat_id = msg.get("chat", {}).get("id")
                if chat_id != CHAT_ID:
                    continue  # Nur Nachrichten von Jens

                text = msg.get("text", "").strip()
                ts   = datetime.now().strftime("%H:%M:%S")
                print(f"[{ts}] Empfangen: '{text}'")

                # Befehle
                if text.lower() in ["/frage", "/quiz", "/next"]:
                    tracker = frage_senden(tracker)

                elif text.lower() in ["/lektionen", "/lektion", "/lernen"]:
                    tracker = lektion_senden(tracker)

                elif text.lower() in ["/status", "/fortschritt"]:
                    status_senden(tracker)

                elif text.lower() in ["/hilfe", "/help", "/start"]:
                    send(
                        "🤖 <b>JensLernBot – Befehle</b>\n\n"
                        "/frage – Neue Quizfrage starten\n"
                        "/lektionen – Tageslektion anzeigen\n"
                        "/status – Fortschritt & Themen-Übersicht\n"
                        "/hilfe – Diese Hilfe\n\n"
                        "<i>Antworte auf eine Frage mit A, B, C oder D</i>"
                    )

                elif all(c in "ABCDabcd, " for c in text) and any(c in "ABCDabcd" for c in text) and len(text.strip()) <= 6:
                    if tracker.get("warte_auf_lektion_antwort"):
                        tracker = lektion_antwort_verarbeiten(tracker, text)
                    elif tracker["warte_auf_antwort"]:
                        tracker = antwort_verarbeiten(tracker, text)
                    # Kein Feedback bei A/B/C/D ohne aktive Frage → still ignorieren

                save_tracker(tracker)

            time.sleep(POLL_SEC)

        except KeyboardInterrupt:
            print("\nService gestoppt.")
            break
        except Exception as e:
            print(f"[FEHLER] {e}")
            time.sleep(10)

if __name__ == "__main__":
    import sys
    if "--lektion" in sys.argv:
        # Einmaliger Modus: Lektion senden und beenden (für Cron)
        tracker = load_tracker()
        lektion_senden(tracker)
    else:
        main()