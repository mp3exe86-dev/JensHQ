#!/usr/bin/env python3
# az900_quiz.py — AZ-900 Spaced Repetition System
# Keine Timeouts — Fragen bleiben offen bis beantwortet
# Neue Fragen stellen sich hinten an

import json
import os
import random
import requests
import sys
import time
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv('/home/jens/JobAgent/.env')

BOT_TOKEN   = os.getenv("JAMES_TOKEN", "")
CHAT_ID     = os.getenv("CHAT_ID", "8656887627")
API_URL     = f"https://api.telegram.org/bot{BOT_TOKEN}"

FRAGEN_DATEI   = "/home/jens/JobAgent/daten/az900_fragen.json"
TRACKER_DATEI  = "/home/jens/JobAgent/daten/az900_tracker.json"
QUEUE_DATEI    = "/home/jens/JobAgent/daten/az900_queue.json"

FRAGEN_PRO_RUNDE = 5

# ═══════════════════════════════════════
# HILFSFUNKTIONEN
# ═══════════════════════════════════════

def send(text: str):
    try:
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=10)
    except Exception as e:
        print(f"[Send Fehler] {e}")

def lade_json(pfad: str, default):
    try:
        with open(pfad, "r") as f:
            return json.load(f)
    except:
        return default

def speichere_json(pfad: str, daten):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "w") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)

def lade_tracker() -> dict:
    return lade_json(TRACKER_DATEI, {
        "gesamt_richtig": 0,
        "gesamt_falsch": 0,
        "fragen": {},
        "wochen_richtig": 0,
        "wochen_falsch": 0,
        "wochen_start": str(date.today())
    })

def lade_queue() -> dict:
    return lade_json(QUEUE_DATEI, {
        "aktive_frage": None,   # aktuell offene Frage
        "queue": [],            # wartende Fragen IDs
        "runde": 0
    })

def lade_fragen() -> list:
    return lade_json(FRAGEN_DATEI, [])

def waehle_fragen_adaptiv(alle_fragen: list, tracker: dict, anzahl: int) -> list:
    gewichtet = []
    for frage in alle_fragen:
        fid = str(frage["id"])
        stats = tracker["fragen"].get(fid, {"richtig": 0, "falsch": 0})
        if stats["richtig"] == 0 and stats["falsch"] == 0:
            gewicht = 2
        elif stats["falsch"] > stats["richtig"]:
            gewicht = 4
        elif stats["falsch"] > 0:
            gewicht = 2
        else:
            gewicht = 1
        gewichtet.extend([frage] * gewicht)

    random.shuffle(gewichtet)
    gesehen = set()
    ausgewaehlt = []
    for f in gewichtet:
        if f["id"] not in gesehen:
            gesehen.add(f["id"])
            ausgewaehlt.append(f)
        if len(ausgewaehlt) >= anzahl:
            break
    return ausgewaehlt

def sende_frage(frage: dict, nummer: int, gesamt: int):
    text = (
        f"🎓 <b>AZ-900 — Frage {nummer}/{gesamt}</b>\n"
        f"📚 {frage['thema']}\n"
        f"────────────────────\n"
        f"{frage['frage']}\n\n"
        f"A) {frage['optionen']['A']}\n"
        f"B) {frage['optionen']['B']}\n"
        f"C) {frage['optionen']['C']}\n"
        f"D) {frage['optionen']['D']}"
    )
    keyboard = {"inline_keyboard": [[
        {"text": "A", "callback_data": f"quiz_A_{frage['id']}"},
        {"text": "B", "callback_data": f"quiz_B_{frage['id']}"},
        {"text": "C", "callback_data": f"quiz_C_{frage['id']}"},
        {"text": "D", "callback_data": f"quiz_D_{frage['id']}"}
    ]]}
    try:
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": keyboard
        }, timeout=10)
    except Exception as e:
        print(f"[Frage Fehler] {e}")

# ═══════════════════════════════════════
# NEUE RUNDE STARTEN — legt Fragen in Queue
# ═══════════════════════════════════════

def starte_runde(runde: int):
    alle_fragen = lade_fragen()
    tracker = lade_tracker()
    queue = lade_queue()

    # Prüfen ob noch offene Frage wartet
    if queue.get("aktive_frage"):
        send(
            f"⏳ Du hast noch eine offene Frage!\n"
            f"Beantworte sie zuerst, dann kommen neue."
        )
        return

    fragen = waehle_fragen_adaptiv(alle_fragen, tracker, FRAGEN_PRO_RUNDE)

    queue["queue"] = [f["id"] for f in fragen[1:]]  # Rest in Queue
    queue["runde"] = runde
    queue["runde_fragen"] = [f["id"] for f in fragen]
    queue["runde_nummer"] = 1
    queue["runde_gesamt"] = FRAGEN_PRO_RUNDE

    # Erste Frage direkt schicken
    erste_frage = fragen[0]
    queue["aktive_frage"] = erste_frage["id"]
    speichere_json(QUEUE_DATEI, queue)

    send(
        f"🎓 <b>AZ-900 Runde {runde}</b>\n"
        f"📊 {tracker.get('gesamt_richtig', 0)} ✅ | {tracker.get('gesamt_falsch', 0)} ❌ gesamt\n"
        f"Beantworte die Fragen wann du Zeit hast!"
    )
    time.sleep(1)
    sende_frage(erste_frage, 1, FRAGEN_PRO_RUNDE)

# ═══════════════════════════════════════
# ANTWORT VERARBEITEN — wird von James aufgerufen
# ═══════════════════════════════════════

def verarbeite_antwort(frage_id: int, antwort: str):
    alle_fragen = lade_fragen()
    tracker = lade_tracker()
    queue = lade_queue()

    # Frage finden
    frage = next((f for f in alle_fragen if f["id"] == frage_id), None)
    if not frage:
        return

    fid = str(frage_id)
    if fid not in tracker["fragen"]:
        tracker["fragen"][fid] = {"richtig": 0, "falsch": 0, "letzte": ""}
    tracker["fragen"][fid]["letzte"] = str(date.today())

    # Auswerten
    if antwort == frage["antwort"]:
        tracker["fragen"][fid]["richtig"] += 1
        tracker["gesamt_richtig"] = tracker.get("gesamt_richtig", 0) + 1
        tracker["wochen_richtig"] = tracker.get("wochen_richtig", 0) + 1
        send(f"✅ <b>Richtig!</b>\n\n💡 {frage['erklaerung']}")
    else:
        tracker["fragen"][fid]["falsch"] += 1
        tracker["gesamt_falsch"] = tracker.get("gesamt_falsch", 0) + 1
        tracker["wochen_falsch"] = tracker.get("wochen_falsch", 0) + 1
        send(
            f"❌ <b>Falsch!</b> Du hast <b>{antwort}</b> gewählt.\n"
            f"✅ Richtig: <b>{frage['antwort']}</b>\n\n"
            f"💡 {frage['erklaerung']}"
        )

    speichere_json(TRACKER_DATEI, tracker)

    # Nächste Frage aus Queue
    time.sleep(2)
    if queue.get("queue"):
        naechste_id = queue["queue"].pop(0)
        queue["aktive_frage"] = naechste_id
        queue["runde_nummer"] = queue.get("runde_nummer", 1) + 1
        speichere_json(QUEUE_DATEI, queue)

        naechste_frage = next((f for f in alle_fragen if f["id"] == naechste_id), None)
        if naechste_frage:
            sende_frage(naechste_frage, queue["runde_nummer"], queue["runde_gesamt"])
    else:
        # Runde fertig
        queue["aktive_frage"] = None
        speichere_json(QUEUE_DATEI, queue)

        runde_fragen = queue.get("runde_fragen", [])
        richtig = sum(1 for fid in runde_fragen
                      if tracker["fragen"].get(str(fid), {}).get("richtig", 0) > 0)
        falsch = FRAGEN_PRO_RUNDE - richtig
        prozent = int((richtig / FRAGEN_PRO_RUNDE) * 100)
        emoji = "🔥" if prozent >= 80 else "💪" if prozent >= 60 else "📚"

        send(
            f"{emoji} <b>Runde {queue.get('runde', '?')} abgeschlossen!</b>\n\n"
            f"✅ Richtig: {richtig}/{FRAGEN_PRO_RUNDE} ({prozent}%)\n"
            f"❌ Falsch: {falsch}/{FRAGEN_PRO_RUNDE}\n\n"
            f"{'Stark! 💪' if prozent >= 80 else 'Weiter üben! 📚'}"
        )

# ═══════════════════════════════════════
# WOCHEN SCORE
# ═══════════════════════════════════════

def sende_wochen_score():
    tracker = lade_tracker()
    alle_fragen = lade_fragen()

    heute = date.today()
    wochen_start = date.fromisoformat(tracker.get("wochen_start", str(heute)))
    if (heute - wochen_start).days >= 7:
        tracker["wochen_richtig"] = 0
        tracker["wochen_falsch"] = 0
        tracker["wochen_start"] = str(heute)

    richtig = tracker.get("wochen_richtig", 0)
    falsch = tracker.get("wochen_falsch", 0)
    gesamt = richtig + falsch
    prozent = int((richtig / gesamt) * 100) if gesamt > 0 else 0
    balken = "█" * (prozent // 10) + "░" * (10 - prozent // 10)

    # Schwache Themen
    thema_stats = {}
    for frage in alle_fragen:
        fid = str(frage["id"])
        stats = tracker["fragen"].get(fid, {"richtig": 0, "falsch": 0})
        thema = frage["thema"]
        if thema not in thema_stats:
            thema_stats[thema] = {"richtig": 0, "falsch": 0}
        thema_stats[thema]["richtig"] += stats["richtig"]
        thema_stats[thema]["falsch"] += stats["falsch"]

    schwach = sorted(thema_stats.items(),
                     key=lambda x: x[1]["falsch"] - x[1]["richtig"],
                     reverse=True)[:3]

    msg = (
        f"📊 <b>AZ-900 Wochen-Score</b>\n\n"
        f"{balken} {prozent}%\n"
        f"✅ Richtig: {richtig}\n"
        f"❌ Falsch: {falsch}\n"
        f"📝 Gesamt: {gesamt} Fragen\n\n"
    )

    if schwach:
        msg += "🎯 <b>Fokus drauf:</b>\n"
        for thema, stats in schwach:
            if stats["falsch"] > 0:
                msg += f"• {thema}: {stats['falsch']} ❌\n"

    if prozent >= 80:
        msg += "\n🏆 <b>80%+ — Prüfung buchen!</b>"
    elif prozent >= 70:
        msg += "\n💪 <b>Fast da!</b>"
    else:
        msg += "\n📚 <b>Weiter üben!</b>"

    send(msg)
    speichere_json(TRACKER_DATEI, tracker)

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

if __name__ == "__main__":
    modus = sys.argv[1] if len(sys.argv) > 1 else "quiz"
    runde = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    if modus == "score":
        sende_wochen_score()
    elif modus == "quiz":
        starte_runde(runde)
    elif modus == "antwort":
        # Aufruf: az900_quiz.py antwort FRAGE_ID ANTWORT
        frage_id = int(sys.argv[2])
        antwort = sys.argv[3]
        verarbeite_antwort(frage_id, antwort)
