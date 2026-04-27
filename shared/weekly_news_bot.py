import json
import requests
import feedparser
import base64
from datetime import datetime, date, timedelta
import os
import random
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════
# KONFIGURATION
# ═══════════════════════════════════════

BOT_TOKEN = os.getenv("FOKUSBOT_TOKEN", "")
CHAT_ID   = os.getenv("CHAT_ID", "8656887627")

VAULT_PATH     = os.getenv("WINDOWS_VAULT", r"C:\JobAgent\vault\SecondBrain")
TODOS_FILE     = os.path.join(VAULT_PATH, "todos.json")
VERTRAEGE_FILE = os.path.join(VAULT_PATH, "vertraege.json")

PROBEZEIT_START = date(2026, 4, 1)
PROBEZEIT_ENDE  = date(2026, 6, 30)

ALERT_TAGE = 21

# ═══════════════════════════════════════
# HILFSFUNKTIONEN
# ═══════════════════════════════════════

def lade_json(pfad):
    with open(pfad, "r", encoding="utf-8") as f:
        return json.load(f)

def fortschrittsbalken(prozent, breite=20):
    gefuellt = int(breite * prozent / 100)
    leer = breite - gefuellt
    return "█" * gefuellt + "░" * leer

def berechne_probezeit():
    heute = date.today()
    gesamt = (PROBEZEIT_ENDE - PROBEZEIT_START).days
    vergangen = (heute - PROBEZEIT_START).days
    vergangen = max(0, min(vergangen, gesamt))
    prozent = int((vergangen / gesamt) * 100)
    noch = (PROBEZEIT_ENDE - heute).days
    balken = fortschrittsbalken(prozent)
    return vergangen, gesamt, prozent, noch, balken

def berechne_vertrag(vertrag):
    heute = date.today()
    start = date.fromisoformat(vertrag["start"])
    ende = date.fromisoformat(vertrag["ende"])
    gesamt = (ende - start).days
    vergangen = (heute - start).days
    vergangen = max(0, min(vergangen, gesamt))
    prozent = int((vergangen / gesamt) * 100)
    noch_tage = (ende - heute).days
    gesamt_monate = (ende.year - start.year) * 12 + (ende.month - start.month)
    vergangene_monate = (heute.year - start.year) * 12 + (heute.month - start.month)
    noch_monate = max(0, gesamt_monate - vergangene_monate)
    if noch_monate <= 1:
        restbetrag = vertrag.get("schlussrate", 0)
    else:
        restbetrag = (noch_monate - 1) * vertrag["monatliche_rate"] + vertrag.get("schlussrate", 0)
    return prozent, noch_tage, restbetrag, noch_monate

def pruefe_alert(last_updated_str):
    heute = date.today()
    last = date.fromisoformat(last_updated_str)
    delta = (heute - last).days
    return delta >= ALERT_TAGE, delta

# ═══════════════════════════════════════
# BLÖCKE
# ═══════════════════════════════════════

def block_probezeit():
    vergangen, gesamt, prozent, noch, balken = berechne_probezeit()
    kw = date.today().isocalendar()[1]
    lines = [
        "┌─ 🏢 MOTECS PROBEZEIT ───────────────┐",
        f"│ Start    01.04.2026                │",
        f"│ Ende     30.06.2026                │",
        f"│ Tag      {vergangen} von {gesamt}               │",
        f"│ {balken}  {prozent}% ✅  │",
        f"│ Noch {noch} Tage — du schaffst das! │",
        "└────────────────────────────────────┘"
    ]
    return "\n".join(lines)

def block_todos():
    data = lade_json(TODOS_FILE)
    lines = ["┌─ 📋 OFFENE TO-DOs ──────────────────┐"]
    alerts = []

    for todo in data["todos"]:
        if todo["prozent"] >= 100:
            continue

        ist_alert, delta = pruefe_alert(todo["last_updated"])
        if ist_alert and todo.get("aktiv", True):
            alerts.append((todo["name"], delta))

        name_kurz = todo["name"][:16]
        symbol = "⚠️" if (ist_alert and todo.get("aktiv", True)) else todo["prio"]
        zeile = f"│ {symbol} {name_kurz:<16} {todo['prozent']:>3}% │"
        lines.append(zeile)

    lines.append("└────────────────────────────────────┘")

    if alerts:
        lines.append("")
        lines.append("╔════════════════════════════════════╗")
        lines.append("║ 🚨 PROJEKT VERNACHLÄSSIGT! 🚨      ║")
        for name, delta in alerts:
            lines.append(f"║  » {name:<20} {delta} Tage  ║")
        lines.append("╚════════════════════════════════════╝")

    return "\n".join(lines)

def block_vertraege():
    data = lade_json(VERTRAEGE_FILE)
    lines = ["┌─ 💰 VERTRÄGE ───────────────────────┐"]

    for v in data["vertraege"]:
        prozent, noch_tage, restbetrag, noch_monate = berechne_vertrag(v)
        balken = fortschrittsbalken(prozent, breite=12)
        lines.append(f"│ {v['emoji']} {v['name']:<20}             │")
        lines.append(f"│   {balken}  {prozent}%        │")
        lines.append(f"│   Noch {noch_monate} Monate | ~{restbetrag:.0f}€ offen   │")

    for t in data.get("termine", []):
        faellig = date.fromisoformat(t["faellig"])
        noch = (faellig - date.today()).days
        lines.append(f"│ {t['emoji']} {t['name']}: {t['faellig']} ({noch}d)  │")

    lines.append("└────────────────────────────────────┘")
    return "\n".join(lines)

def block_fokus():
    try:
        fokus_file = os.path.join(VAULT_PATH, "fokus.json")
        data = lade_json(fokus_file)
        punkte = data.get("fokus", [])
    except:
        punkte = ["Kein Fokus definiert"]

    lines = ["┌─ 🎯 FOKUS DIESE WOCHE ──────────────┐"]
    for p in punkte[:3]:
        lines.append(f"│ » {p[:36]:<36} │")
    lines.append("└────────────────────────────────────┘")
    return "\n".join(lines)

def hole_it_trends():
    feeds = [
        ("Heise", "https://www.heise.de/developer/rss/news-atom.xml"),
        ("t3n", "https://t3n.de/feed/"),
        ("Decoder", "https://the-decoder.de/feed/"),
        ("Golem", "https://rss.golem.de/rss.php?feed=RSS2.0"),
    ]

    schlagzeilen = []
    links = []

    for name, url in feeds:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                titel = feed.entries[0].title
                link = feed.entries[0].get("link", "")
                schlagzeilen.append(f"│ » [{name}] {titel[:34]:<34} │")
                links.append((name, titel, link))
        except:
            schlagzeilen.append(f"│ » {name}: nicht erreichbar             │")

    lines = ["┌─ 📈 IT/CLOUD TRENDS ────────────────┐"]
    lines.extend(schlagzeilen[:4])
    lines.append("└────────────────────────────────────┘")

    return "\n".join(lines), links

def hole_zertifikate():
    ms_feed = "https://techcommunity.microsoft.com/plugins/custom/microsoft/o365/custom-blog-rss?board=MicrosoftLearnBlog"
    azure_feed = "https://azure.microsoft.com/en-us/blog/feed/"

    neuigkeiten = []
    links = []

    for url in [ms_feed, azure_feed]:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                titel = feed.entries[0].title
                link = feed.entries[0].get("link", "")
                neuigkeiten.append(f"│ 🆕 {titel[:34]:<34} │")
                links.append(("MS Learn", titel, link))
        except:
            pass

    zertifikate_fix = [
        ("AZ-900", "Azure Fundamentals",    "165€", "⏳", "https://learn.microsoft.com/de-de/credentials/certifications/azure-fundamentals/"),
        ("SC-900", "Security Fundamentals", "165€", "📅", "https://learn.microsoft.com/de-de/credentials/certifications/security-compliance-and-identity-fundamentals/"),
        ("MD-102", "Endpoint Admin",        "165€", "📅", "https://learn.microsoft.com/de-de/credentials/certifications/modern-desktop/"),
        ("AZ-104", "Azure Administrator",   "165€", "📅", "https://learn.microsoft.com/de-de/credentials/certifications/azure-administrator/"),
    ]

    lines = ["┌─ 🎓 KURSE & ZERTIFIKATE ────────────┐"]

    if neuigkeiten:
        lines.append("│ NEU AUS MS LEARN:                  │")
        lines.extend(neuigkeiten[:2])
        lines.append("│                                    │")

    for kuerzel, name, preis, status, link in zertifikate_fix:
        lines.append(f"│ {status} {kuerzel:<8} {name:<20} {preis} │")
        links.append((kuerzel, name, link))

    lines.append("└────────────────────────────────────┘")

    return "\n".join(lines), links

def block_quote():
    quotes = [
        ("First, solve the problem. Then write the code.", "John Johnson"),
        ("Make it work, make it right, make it fast.", "Kent Beck"),
        ("Simplicity is the soul of efficiency.", "Austin Freeman"),
        ("Talk is cheap. Show me the code.", "Linus Torvalds"),
        ("Any fool can write code a computer understands.", "Martin Fowler"),
        ("The best time to start was yesterday.", "unbekannt"),
        ("Code is like humor. When you explain it, its bad.", "Cory House"),
    ]
    q, autor = random.choice(quotes)
    lines = [
        "┌─ 💬 QUOTE OF THE WEEK ──────────────┐",
        f"│ \"{q[:34]}\"  │",
        f"│  — {autor:<33} │",
        "└────────────────────────────────────┘"
    ]
    return "\n".join(lines)


def refresh_fitbit_token():
    client_id     = os.getenv("FITBIT_CLIENT_ID")
    client_secret = os.getenv("FITBIT_CLIENT_SECRET")
    refresh_token = os.getenv("FITBIT_REFRESH_TOKEN")

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    r = requests.post("https://api.fitbit.com/oauth2/token",
        headers={"Authorization": f"Basic {credentials}",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "refresh_token", "refresh_token": refresh_token}
    )
    data = r.json()
    if "access_token" in data:
        env_pfad = os.path.join(os.getenv("WINDOWS_BASE", r"C:\JobAgent"), ".env")
        with open(env_pfad, "r") as f:
            inhalt = f.read()
        inhalt = inhalt.replace(os.getenv("FITBIT_ACCESS_TOKEN"), data["access_token"])
        inhalt = inhalt.replace(os.getenv("FITBIT_REFRESH_TOKEN"), data["refresh_token"])
        with open(env_pfad, "w") as f:
            f.write(inhalt)
        return data["access_token"]
    return os.getenv("FITBIT_ACCESS_TOKEN")


def block_fitbit():
    try:
        token = refresh_fitbit_token()
        user_id = os.getenv("FITBIT_USER_ID", "7PS3ZT")
        gestern = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        headers = {"Authorization": f"Bearer {token}"}

        r = requests.get(f"https://api.fitbit.com/1/user/{user_id}/activities/date/{gestern}.json", headers=headers)
        schritte = r.json().get("summary", {}).get("steps", 0)

        r = requests.get(f"https://api.fitbit.com/1.2/user/{user_id}/sleep/date/{gestern}.json", headers=headers)
        schlaf_min = r.json().get("summary", {}).get("totalMinutesAsleep", 0)
        schlaf_h = schlaf_min // 60
        schlaf_m = schlaf_min % 60

        r = requests.get(f"https://api.fitbit.com/1/user/{user_id}/activities/heart/date/{gestern}/1d.json", headers=headers)
        ruhepuls = r.json().get("activities-heart", [{}])[0].get("value", {}).get("restingHeartRate", 0)

        lines = [
            "┌─ 💪 GESTERN ───────────────────────┐",
            f"│ 👟 Schritte   {schritte:>8,}              │",
            f"│ 😴 Schlaf     {schlaf_h}h {schlaf_m:02d}min             │",
            f"│ ❤️  Ruhepuls   {ruhepuls:>8} bpm           │",
            "└────────────────────────────────────┘"
        ]
        return "\n".join(lines)

    except Exception as e:
        return f"┌─ 💪 FITBIT ────────────────────────┐\n│ ❌ Fehler: {str(e)[:28]:<28} │\n└────────────────────────────────────┘"


def block_habits():
    """Habits Wochenübersicht für Weekly Digest."""
    try:
        HABITS = [
            {"id": "sport",        "emoji": "💪", "name": "Sport",          "ziel": 3},
            {"id": "liegestuetze", "emoji": "🤸", "name": "100 Liegestütze","ziel": 5},
            {"id": "dehnen",       "emoji": "🧘", "name": "Dehnen",          "ziel": 3},
            {"id": "az900",        "emoji": "📚", "name": "AZ-900",          "ziel": 4},
            {"id": "jenshq",       "emoji": "🤖", "name": "JensHQ",          "ziel": 4},
            {"id": "lesen",        "emoji": "📖", "name": "Lesen",           "ziel": 4},
            {"id": "bett",         "emoji": "😴", "name": "Vor 23 Uhr Bett", "ziel": 6},
        ]

        tracker_pfad = r"C:\JobAgent\daten\habits_tracker.json" if os.name == "nt" else "/home/jens/JobAgent/daten/habits_tracker.json"
        with open(tracker_pfad, "r") as f:
            tracker = json.load(f)

        heute = date.today()
        kw = heute.isocalendar()[1]
        kw_key = f"{heute.year}_KW{kw}"
        woche = tracker.get("wochen", {}).get(kw_key, {})

        gesamt_prozent = []
        lines = [f"🏆 *Habit Score KW{kw}:*\n"]

        for habit in HABITS:
            hid = habit["id"]
            erreicht = len(woche.get(hid, []))
            ziel = habit["ziel"]
            prozent = min(int((erreicht / ziel) * 100), 100)
            gesamt_prozent.append(prozent)
            check = "✅" if erreicht >= ziel else "⚠️" if erreicht > 0 else "❌"
            lines.append(f"{check} {habit['emoji']} {habit['name']}: {erreicht}/{ziel}")

        gesamt = int(sum(gesamt_prozent) / len(gesamt_prozent))
        balken = "█" * (gesamt // 10) + "░" * (10 - gesamt // 10)
        lines.append(f"\n{balken} {gesamt}%")

        if gesamt >= 80:
            lines.append("🔥 Stark! Feature-Freischaltung möglich!")
        elif gesamt >= 60:
            lines.append("💪 Guter Fortschritt!")
        else:
            lines.append("📚 Nächste Woche mehr!")

        return "\n".join(lines)
    except Exception as e:
        return f"🏆 Habits: Keine Daten ({e})"


def baue_morning_digest():
    """Täglicher Morning Digest mit Fitbit + Dehn-Tipp."""
    datum = date.today().strftime("%d.%m.%Y")
    wochentag = ["Mo","Di","Mi","Do","Fr","Sa","So"][date.today().weekday()]

    lines = [f"☀️ *Guten Morgen Jens — {wochentag} {datum}*\n"]

    # Fitbit
    try:
        token = refresh_fitbit_token()
        user_id = os.getenv("FITBIT_USER_ID", "7PS3ZT")
        gestern = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        headers = {"Authorization": f"Bearer {token}"}
        schritte = requests.get(f"https://api.fitbit.com/1/user/{user_id}/activities/date/{gestern}.json", headers=headers).json().get("summary", {}).get("steps", 0)
        schlaf_min = requests.get(f"https://api.fitbit.com/1.2/user/{user_id}/sleep/date/{gestern}.json", headers=headers).json().get("summary", {}).get("totalMinutesAsleep", 0)
        ruhepuls = requests.get(f"https://api.fitbit.com/1/user/{user_id}/activities/heart/date/{gestern}/1d.json", headers=headers).json().get("activities-heart", [{}])[0].get("value", {}).get("restingHeartRate", 0)
        lines.append(f"💪 *Gestern:* 👟 {schritte:,} | 😴 {schlaf_min//60}h {schlaf_min%60:02d}min | ❤️ {ruhepuls} bpm\n")
    except:
        lines.append("💪 Fitbit: nicht verfügbar\n")

    # Dehn Tipp
    try:
        dehn_pfad = r"C:\JobAgent\daten\dehn_tipps.json" if os.name == "nt" else "/home/jens/JobAgent/daten/dehn_tipps.json"
        with open(dehn_pfad, "r") as f:
            tipps = json.load(f)
        tipp = random.choice(tipps)
        lines.append(f"🧘 *Dehn-Tipp: {tipp['name']}* ({tipp['dauer']})")
        lines.append(f"{tipp['anleitung']}\n")
    except:
        pass

    # The Decoder
    try:
        feed = feedparser.parse("https://the-decoder.de/feed/")
        lines.append("🤖 *The Decoder — Neu:*")
        decoder_links = []
        for entry in feed.entries[:3]:
            lines.append(f"• {entry.get('title', '')}")
            decoder_links.append(entry.get("link", ""))
    except:
        decoder_links = []

    return "\n".join(lines), decoder_links


def baue_links_nachricht(trend_links, zert_links):
    lines = ["🔗 <b>LINKS ZUM DIGEST</b>", "", "📈 <b>IT Trends:</b>"]
    for name, titel, link in trend_links:
        if link:
            lines.append(f"• <a href='{link}'>[{name}] {titel[:50]}</a>")

    lines.append("")
    lines.append("🎓 <b>Zertifikate &amp; Kurse:</b>")
    for name, titel, link in zert_links:
        if link:
            lines.append(f"• <a href='{link}'>{name} — {titel[:40]}</a>")

    return "\n".join(lines)

# ═══════════════════════════════════════
# DIGEST
# ═══════════════════════════════════════

import sys

def baue_digest():
    kw = date.today().isocalendar()[1]
    datum = date.today().strftime("%d.%m.%Y")

    header = (
        f"╔════════════════════════════════════╗\n"
        f"║  JENS HQ — WEEKLY DIGEST KW {kw:<2}    ║\n"
        f"║  {datum}                      ║\n"
        f"╚════════════════════════════════════╝"
    )

    footer = (
        "╔════════════════════════════════════╗\n"
        "║ 💾 OBSIDIAN SYNC............ OK   ║\n"
        "║ 🟢 ALLE SYSTEME NOMINAL           ║\n"
        "╚════════════════════════════════════╝"
    )

    print("⏳ Hole IT Trends...")
    trends_block, trend_links = hole_it_trends()

    print("⏳ Hole Zertifikate...")
    zert_block, zert_links = hole_zertifikate()

    print("⏳ Hole Fitbit Daten...")

    teile = [
        header, "",
        block_probezeit(), "",
        block_fitbit(), "",
        block_habits(), "",
        block_todos(), "",
        block_vertraege(), "",
        block_fokus(), "",
        trends_block, "",
        zert_block, "",
        block_quote(), "",
        footer
    ]

    return "\n".join(teile), trend_links, zert_links

# ═══════════════════════════════════════
# SENDEN + OBSIDIAN
# ═══════════════════════════════════════

def sende_telegram(text, parse_mode=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    r = requests.post(url, json=payload)
    return r.status_code

def speichere_obsidian(text):
    kw = date.today().isocalendar()[1]
    jahr = date.today().year
    dateiname = f"WeeklyDigest_KW{kw:02d}_{jahr}.md"
    pfad = os.path.join(VAULT_PATH, dateiname)
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(f"# Weekly Digest KW{kw:02d} {jahr}\n\n")
        f.write("```\n")
        f.write(text)
        f.write("\n```\n")
    print(f"✅ Obsidian gespeichert: {dateiname}")

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

if __name__ == "__main__":
    modus = sys.argv[1] if len(sys.argv) > 1 else ("weekly" if date.today().weekday() == 6 else "daily")

    if modus == "daily":
        print("☀️ Baue Morning Digest...")
        digest, decoder_links = baue_morning_digest()
        print(digest)
        sende_telegram(digest, parse_mode="Markdown")
        if decoder_links:
            links_msg = "🔗 <b>The Decoder Links:</b>\n"
            for link in decoder_links:
                if link:
                    links_msg += f"• <a href='{link}'>{link[:60]}</a>\n"
            sende_telegram(links_msg, parse_mode="HTML")

    elif modus == "weekly":
        print("📰 Baue Weekly Digest...")
        digest, trend_links, zert_links = baue_digest()
        print(digest)
        print("\n📤 Sende Digest...")
        status = sende_telegram(digest)
        print(f"Digest Status: {status}")
        print("📤 Sende Links...")
        links_msg = baue_links_nachricht(trend_links, zert_links)
        status2 = sende_telegram(links_msg, parse_mode="HTML")
        print(f"Links Status: {status2}")
        speichere_obsidian(digest)
