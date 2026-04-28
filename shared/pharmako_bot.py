#!/usr/bin/env python3
# pharmako_bot.py — PharmakoVigilanz Monitor
# Überwacht EMA, BfArM, FDA, PEI auf neue Sicherheitsmeldungen
# Täglich automatisch, nur NEUE Einträge, Ollama Zusammenfassung

import json
import os
import requests
import feedparser
import hashlib
import time
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv('/home/jens/JobAgent/.env')

BOT_TOKEN  = os.getenv("JAMES_TOKEN", "")
CHAT_ID    = os.getenv("CHAT_ID", "8656887627")
API_URL    = f"https://api.telegram.org/bot{BOT_TOKEN}"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://192.168.178.80:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

SEEN_FILE  = "/home/jens/JobAgent/daten/pharmako_seen.json"
LOG_FILE   = "/home/jens/JobAgent/logs/pharmako.log"

# ═══════════════════════════════════════
# QUELLEN
# ═══════════════════════════════════════

QUELLEN = [
    {"name": "FDA Drugs News", "emoji": "US", "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/drugs/rss.xml", "typ": "rss"},
    {"name": "Drugs.com Alerts", "emoji": "ALERT", "url": "https://www.drugs.com/feeds/fda_alerts.xml", "typ": "rss"},
    {"name": "Drugs.com Approvals", "emoji": "OK", "url": "https://www.drugs.com/feeds/new_drug_approvals.xml", "typ": "rss"},
    {"name": "DailyMed Labels", "emoji": "NIH", "url": "https://dailymed.nlm.nih.gov/dailymed/rss.cfm?type=rsstype2", "typ": "rss"},
    {"name": "MHRA UK Safety", "emoji": "UK", "url": "https://www.gov.uk/search/news-and-communications.atom?keywords=recall+medicine&organisations%5B%5D=medicines-and-healthcare-products-regulatory-agency", "typ": "rss"},
    {"name": "ClinicalTrials Arena", "emoji": "EU", "url": "https://www.clinicaltrialsarena.com/feed/", "typ": "rss"},
    {"name": "PMLive Pharma News", "emoji": "EU", "url": "https://www.pmlive.com/rss", "typ": "rss"},
]

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

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{ts}] {msg}\n")
    except:
        pass

def lade_seen() -> set:
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def speichere_seen(seen: set):
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    # Nur letzte 2000 IDs behalten
    seen_liste = list(seen)[-2000:]
    with open(SEEN_FILE, "w") as f:
        json.dump(seen_liste, f)

def eintrag_id(quelle: str, link: str, titel: str) -> str:
    content = f"{quelle}_{link}_{titel}"
    return hashlib.md5(content.encode()).hexdigest()

def ist_relevant(titel: str, beschreibung: str) -> bool:
    """Filtert nur relevante PharmakoVigilanz Meldungen."""
    keywords_positiv = [
        "recall", "rückruf", "safety", "sicherheit", "alert", "warnung", "warning",
        "adverse", "nebenwirkung", "risk", "risiko", "withdrawal", "rücknahme",
        "shortage", "engpass", "contraindication", "kontraindikation",
        "drug interaction", "wechselwirkung", "black box", "rote hand",
        "market withdrawal", "death", "fatal", "serious", "schwerwiegend",
        "approval", "zulassung", "label change", "label update"
    ]
    keywords_negativ = [
        "committee site", "rdrc", "user fee", "fiscal year", "dmf list",
        "hauskatalog", "forms", "meeting agenda", "procurement", "career",
        "guideline comment", "docket", "grand rounds", "internet pharmacy",
        "warning letters", "drug alerts and statements", "accelerated approvals",
        "compounding", "bulk drug", "oncology approval notifications",
        "verified clinical benefit", "activities report", "rss feed",
        "stay informed", "fda resources"
    ]

    text = (titel + " " + beschreibung).lower()

    # Negative Keywords ausschließen
    for kw in keywords_negativ:
        if kw in text:
            return False

    # Mindestens ein positives Keyword
    for kw in keywords_positiv:
        if kw in text:
            return True

    return False


def ollama_zusammenfassung(titel: str, beschreibung: str, quelle: str) -> str:
    try:
        prompt = (
            f"Pharmako-Sicherheitsmeldung zusammenfassen. NUR die Antwort, kein Prompt-Text wiederholen.\n"
            f"Titel: {titel}\n"
            f"Text: {beschreibung[:800]}\n"
            f"Schreibe genau 2 kurze Saetze auf Deutsch: 1) Betroffenes Medikament/Wirkstoff. 2) Konkrete Massnahme oder Risiko. Nur die 2 Saetze, nichts anderes."
        )
        r = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=60)
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"Zusammenfassung nicht verfuegbar."

# ═══════════════════════════════════════
# HAUPTLOGIK
# ═══════════════════════════════════════

def pruefe_quelle(quelle: dict, seen: set) -> list:
    """Prüft eine Quelle und gibt neue Einträge zurück."""
    neue = []
    try:
        feed = feedparser.parse(quelle["url"])
        if not feed.entries:
            log(f"Keine Einträge: {quelle['name']}")
            return []

        for entry in feed.entries[:20]:  # max 20 neueste prüfen
            titel = entry.get("title", "").strip()
            link  = entry.get("link", "")
            desc  = entry.get("summary", entry.get("description", ""))

            eid = eintrag_id(quelle["name"], link, titel)
            if eid not in seen:
                # Relevanz prüfen
                if not ist_relevant(titel, desc):
                    seen.add(eid)  # als gesehen markieren aber nicht senden
                    continue
                seen.add(eid)
                neue.append({
                    "titel": titel,
                    "link": link,
                    "beschreibung": desc,
                    "quelle": quelle["name"],
                    "emoji": quelle["emoji"]
                })

        log(f"{quelle['name']}: {len(neue)} neue Einträge")
    except Exception as e:
        log(f"Fehler bei {quelle['name']}: {e}")

    return neue

def sende_alert(eintrag: dict):
    """Sendet einen formatierten Alert für einen neuen Eintrag."""
    zusammenfassung = ollama_zusammenfassung(
        eintrag["titel"],
        eintrag["beschreibung"],
        eintrag["quelle"]
    )

    msg = (
        f"{eintrag['emoji']} <b>Neue PharmakoVigilanz-Meldung</b>\n"
        f"📋 <b>{eintrag['quelle']}</b>\n"
        f"────────────────────\n"
        f"<b>{eintrag['titel']}</b>\n\n"
        f"🤖 <i>{zusammenfassung}</i>\n\n"
        f"🔗 <a href='{eintrag['link']}'>Vollständige Meldung</a>"
    )
    send(msg)
    time.sleep(2)  # Telegram Rate Limit

def run():
    """Hauptfunktion — alle Quellen prüfen."""
    log("=== PharmakoBot Start ===")
    seen = lade_seen()
    alle_neuen = []

    for quelle in QUELLEN:
        neue = pruefe_quelle(quelle, seen)
        alle_neuen.extend(neue)
        time.sleep(1)

    if not alle_neuen:
        log("Keine neuen Meldungen.")
        # Kein Telegram Alert wenn nichts Neues
    else:
        log(f"{len(alle_neuen)} neue Meldungen gefunden!")

        # Max 10 Alerts pro Lauf um Spam zu vermeiden
        for eintrag in alle_neuen[:10]:
            sende_alert(eintrag)

        if len(alle_neuen) > 10:
            send(
                f"ℹ️ <b>PharmakoBot:</b> {len(alle_neuen)} neue Meldungen heute. "
                f"Die ersten 10 wurden gesendet."
            )

    speichere_seen(seen)
    log("=== PharmakoBot Ende ===")

def status():
    """Zeigt Status der Datenbank."""
    seen = lade_seen()
    send(
        f"💊 <b>PharmakoVigilanz Bot Status</b>\n\n"
        f"📊 Bekannte Einträge: {len(seen)}\n"
        f"🔍 Quellen: {len(QUELLEN)}\n"
        f"📅 Letzter Run: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Quellen:\n" +
        "\n".join(f"• {q['emoji']} {q['name']}" for q in QUELLEN)
    )

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

if __name__ == "__main__":
    import sys
    modus = sys.argv[1] if len(sys.argv) > 1 else "run"

    if modus == "run":
        run()
    elif modus == "status":
        status()
    elif modus == "test":
        # Testet nur die erste Quelle ohne seen zu ändern
        log("TEST MODUS")
        seen_test = set()
        neue = pruefe_quelle(QUELLEN[0], seen_test)
        if neue:
            log(f"Test: {len(neue)} Einträge gefunden")
            sende_alert(neue[0])
        else:
            log("Test: Keine Einträge")
