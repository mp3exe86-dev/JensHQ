#!/usr/bin/env python3
# az900_quiz.py — AZ-900 Spaced Repetition System für James
# Täglich 5 Runden à 5 Fragen, Adaptive Wiederholung, Sonntags Score

import json
import os
import random
import requests
import sys
import time
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv('/home/jens/JobAgent/.env')

# ═══════════════════════════════════════
# KONFIGURATION
# ═══════════════════════════════════════

BOT_TOKEN   = os.getenv("JAMES_TOKEN", "")
CHAT_ID     = os.getenv("CHAT_ID", "8656887627")
API_URL     = f"https://api.telegram.org/bot{BOT_TOKEN}"

FRAGEN_DATEI  = "/home/jens/JobAgent/daten/az900_fragen.json"
TRACKER_DATEI = "/home/jens/JobAgent/daten/az900_tracker.json"

FRAGEN_PRO_RUNDE = 5
RUNDEN_PRO_TAG   = 5
TIMEOUT_ANTWORT  = 120  # Sekunden bis nächste Frage

# ═══════════════════════════════════════
# HILFSFUNKTIONEN
# ═══════════════════════════════════════

def send(text: str, parse_mode="HTML"):
    try:
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }, timeout=10)
    except Exception as e:
        print(f"[Send Fehler] {e}")

def send_quiz_frage(frage: dict, nummer: int, gesamt: int) -> str:
    """Schickt eine Frage mit ABCD Inline Buttons. Gibt message_id zurück."""
    text = (
        f"🎓 <b>AZ-900 Quiz — Frage {nummer}/{gesamt}</b>\n"
        f"📚 Thema: {frage['thema']}\n"
        f"────────────────────\n"
        f"{frage['frage']}\n\n"
        f"A) {frage['optionen']['A']}\n"
        f"B) {frage['optionen']['B']}\n"
        f"C) {frage['optionen']['C']}\n"
        f"D) {frage['optionen']['D']}"
    )
    keyboard = {
        "inline_keyboard": [[
            {"text": "A", "callback_data": f"quiz_A_{frage['id']}"},
            {"text": "B", "callback_data": f"quiz_B_{frage['id']}"},
            {"text": "C", "callback_data": f"quiz_C_{frage['id']}"},
            {"text": "D", "callback_data": f"quiz_D_{frage['id']}"}
        ]]
    }
    try:
        r = requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": keyboard
        }, timeout=10)
        return str(r.json().get("result", {}).get("message_id", ""))
    except Exception as e:
        print(f"[Quiz Frage Fehler] {e}")
        return ""

def warte_auf_antwort(frage_id: int, timeout: int = TIMEOUT_ANTWORT) -> str:
    """Wartet auf ABCD Callback für diese Frage."""
    offset = 0
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{API_URL}/getUpdates",
                params={"offset": offset, "timeout": 5}, timeout=10)
            updates = r.json().get("result", [])
            for update in updates:
                offset = update["update_id"] + 1
                callback = update.get("callback_query")
                if callback:
                    data = callback.get("data", "")
                    chat = callback.get("message", {}).get("chat", {}).get("id")
                    if str(chat) == str(CHAT_ID) and data.startswith("quiz_") and data.endswith(f"_{frage_id}"):
                        # Callback bestätigen
                        try:
                            requests.post(f"{API_URL}/answerCallbackQuery",
                                json={"callback_query_id": callback["id"]}, timeout=5)
                        except:
                            pass
                        # Antwort extrahieren (quiz_A_123 → A)
                        return data.split("_")[1]
        except:
            pass
        time.sleep(1)
    return ""  # Timeout

def lade_tracker() -> dict:
    try:
        with open(TRACKER_DATEI, "r") as f:
            return json.load(f)
    except:
        return {
            "gesamt_richtig": 0,
            "gesamt_falsch": 0,
            "fragen": {},  # id → {richtig: int, falsch: int, letzte: str}
            "wochen_richtig": 0,
            "wochen_falsch": 0,
            "wochen_start": str(date.today())
        }

def speichere_tracker(tracker: dict):
    os.makedirs(os.path.dirname(TRACKER_DATEI), exist_ok=True)
    with open(TRACKER_DATEI, "w") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)

def lade_fragen() -> list:
    with open(FRAGEN_DATEI, "r") as f:
        return json.load(f)

def waehle_fragen_adaptiv(alle_fragen: list, tracker: dict, anzahl: int) -> list:
    """Wählt Fragen adaptiv — falsch beantwortete kommen häufiger."""
    gewichtet = []
    for frage in alle_fragen:
        fid = str(frage["id"])
        stats = tracker["fragen"].get(fid, {"richtig": 0, "falsch": 0})
        # Mehr Gewicht für falsche Fragen, neue Fragen (0/0) bekommen mittleres Gewicht
        if stats["richtig"] == 0 and stats["falsch"] == 0:
            gewicht = 2  # Neue Frage
        elif stats["falsch"] > stats["richtig"]:
            gewicht = 4  # Häufig falsch
        elif stats["falsch"] > 0:
            gewicht = 2  # Manchmal falsch
        else:
            gewicht = 1  # Gut bekannt
        gewichtet.extend([frage] * gewicht)
    
    random.shuffle(gewichtet)
    # Deduplizieren
    gesehen = set()
    ausgewählt = []
    for f in gewichtet:
        if f["id"] not in gesehen:
            gesehen.add(f["id"])
            ausgewählt.append(f)
        if len(ausgewählt) >= anzahl:
            break
    return ausgewählt

def berechne_wochen_score(tracker: dict) -> tuple:
    """Berechnet Wochen-Score und resetzt wenn neue Woche."""
    heute = date.today()
    wochen_start = date.fromisoformat(tracker.get("wochen_start", str(heute)))
    
    # Neue Woche?
    if (heute - wochen_start).days >= 7:
        tracker["wochen_richtig"] = 0
        tracker["wochen_falsch"] = 0
        tracker["wochen_start"] = str(heute)
    
    richtig = tracker.get("wochen_richtig", 0)
    falsch = tracker.get("wochen_falsch", 0)
    gesamt = richtig + falsch
    prozent = int((richtig / gesamt) * 100) if gesamt > 0 else 0
    return richtig, falsch, gesamt, prozent

# ═══════════════════════════════════════
# QUIZ RUNDE
# ═══════════════════════════════════════

def starte_quiz_runde(runde: int):
    """Eine Runde mit 5 Fragen."""
    alle_fragen = lade_fragen()
    tracker = lade_tracker()
    fragen = waehle_fragen_adaptiv(alle_fragen, tracker, FRAGEN_PRO_RUNDE)
    
    send(
        f"🎓 <b>AZ-900 Quiz — Runde {runde}/{RUNDEN_PRO_TAG}</b>\n"
        f"📊 Heute gesamt: {tracker.get('gesamt_richtig', 0)} ✅ | {tracker.get('gesamt_falsch', 0)} ❌\n"
        f"Beantworte die nächsten {FRAGEN_PRO_RUNDE} Fragen!"
    )
    time.sleep(2)

    runde_richtig = 0
    runde_falsch = 0

    for i, frage in enumerate(fragen, 1):
        send_quiz_frage(frage, i, FRAGEN_PRO_RUNDE)
        antwort = warte_auf_antwort(frage["id"])
        
        fid = str(frage["id"])
        if fid not in tracker["fragen"]:
            tracker["fragen"][fid] = {"richtig": 0, "falsch": 0, "letzte": ""}
        
        tracker["fragen"][fid]["letzte"] = str(date.today())
        
        if antwort == frage["antwort"]:
            tracker["fragen"][fid]["richtig"] += 1
            tracker["gesamt_richtig"] = tracker.get("gesamt_richtig", 0) + 1
            tracker["wochen_richtig"] = tracker.get("wochen_richtig", 0) + 1
            runde_richtig += 1
            send(
                f"✅ <b>Richtig!</b>\n\n"
                f"💡 {frage['erklaerung']}"
            )
        elif antwort == "":
            send(f"⏰ Zeit abgelaufen! Die richtige Antwort war: <b>{frage['antwort']}</b>\n\n💡 {frage['erklaerung']}")
            tracker["fragen"][fid]["falsch"] += 1
            tracker["gesamt_falsch"] = tracker.get("gesamt_falsch", 0) + 1
            tracker["wochen_falsch"] = tracker.get("wochen_falsch", 0) + 1
            runde_falsch += 1
        else:
            tracker["fragen"][fid]["falsch"] += 1
            tracker["gesamt_falsch"] = tracker.get("gesamt_falsch", 0) + 1
            tracker["wochen_falsch"] = tracker.get("wochen_falsch", 0) + 1
            runde_falsch += 1
            send(
                f"❌ <b>Falsch!</b> Du hast <b>{antwort}</b> gewählt.\n"
                f"✅ Richtige Antwort: <b>{frage['antwort']}</b>\n\n"
                f"💡 {frage['erklaerung']}"
            )
        
        speichere_tracker(tracker)
        time.sleep(2)

    # Runden-Zusammenfassung
    prozent = int((runde_richtig / FRAGEN_PRO_RUNDE) * 100)
    emoji = "🔥" if prozent >= 80 else "💪" if prozent >= 60 else "📚"
    send(
        f"{emoji} <b>Runde {runde} abgeschlossen!</b>\n\n"
        f"✅ Richtig: {runde_richtig}/{FRAGEN_PRO_RUNDE} ({prozent}%)\n"
        f"❌ Falsch: {runde_falsch}/{FRAGEN_PRO_RUNDE}\n\n"
        f"{'Stark! Weiter so! 💪' if prozent >= 80 else 'Nicht aufgeben, du schaffst das! 📚'}"
    )

# ═══════════════════════════════════════
# WOCHEN SCORE (Sonntags)
# ═══════════════════════════════════════

def sende_wochen_score():
    tracker = lade_tracker()
    richtig, falsch, gesamt, prozent = berechne_wochen_score(tracker)
    
    # Schwache Themen analysieren
    alle_fragen = lade_fragen()
    thema_stats = {}
    for frage in alle_fragen:
        fid = str(frage["id"])
        stats = tracker["fragen"].get(fid, {"richtig": 0, "falsch": 0})
        thema = frage["thema"]
        if thema not in thema_stats:
            thema_stats[thema] = {"richtig": 0, "falsch": 0}
        thema_stats[thema]["richtig"] += stats["richtig"]
        thema_stats[thema]["falsch"] += stats["falsch"]
    
    # Schwächstes Thema
    schwach = sorted(thema_stats.items(), 
                     key=lambda x: x[1]["falsch"] - x[1]["richtig"], 
                     reverse=True)[:3]
    
    balken = "█" * (prozent // 10) + "░" * (10 - prozent // 10)
    
    msg = (
        f"📊 <b>AZ-900 Wochen-Score</b>\n\n"
        f"{balken} {prozent}%\n"
        f"✅ Richtig: {richtig}\n"
        f"❌ Falsch: {falsch}\n"
        f"📝 Gesamt: {gesamt} Fragen\n\n"
    )
    
    if schwach:
        msg += "🎯 <b>Diese Themen brauchst du mehr:</b>\n"
        for thema, stats in schwach:
            if stats["falsch"] > 0:
                msg += f"• {thema}: {stats['falsch']} ❌\n"
    
    if prozent >= 80:
        msg += "\n🏆 <b>80%+ erreicht — Zeit die Prüfung zu buchen!</b>"
    elif prozent >= 70:
        msg += "\n💪 <b>Gut! Noch ein bisschen, dann bist du bereit!</b>"
    else:
        msg += "\n📚 <b>Weiter üben — du schaffst das!</b>"
    
    send(msg)
    speichere_tracker(tracker)

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

if __name__ == "__main__":
    modus = sys.argv[1] if len(sys.argv) > 1 else "quiz"
    runde = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    if modus == "score":
        sende_wochen_score()
    elif modus == "quiz":
        starte_quiz_runde(runde)
