import json
import requests
import feedparser
import base64
from datetime import datetime, date, timedelta
import os
import random
import sys
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("FOKUSBOT_TOKEN", "")
CHAT_ID   = os.getenv("CHAT_ID", "8656887627")

VAULT_PATH     = os.getenv("WINDOWS_VAULT", r"C:\JobAgent\vault\SecondBrain")
TODOS_FILE     = os.path.join(VAULT_PATH, "todos.json")
VERTRAEGE_FILE = os.path.join(VAULT_PATH, "vertraege.json")

PROBEZEIT_START = date(2026, 4, 1)
PROBEZEIT_ENDE  = date(2026, 6, 30)
ALERT_TAGE = 21

YOUTUBE_FEEDS = [
    ("Niklas Steenfatt",   "https://www.youtube.com/feeds/videos.xml?channel_id=UCzsfkUFa1_4F4cZeSLv5dFQ"),
    ("Julian Ivanov",      "https://www.youtube.com/feeds/videos.xml?channel_id=UCdoTbckiMelGtWvGMfhlkgQ"),
    ("Everlast AI",        "https://www.youtube.com/feeds/videos.xml?channel_id=UC8T5gQ4U4GbI2h8kYCkEcvg"),
    ("c't 3003",           "https://www.youtube.com/feeds/videos.xml?channel_id=UC1t9VFj-O6YUDPQxaVg-NkQ"),
    ("Torben Platzer",     "https://www.youtube.com/feeds/videos.xml?channel_id=UCbUEpvGgmm2BnRnIWi5ScJg"),
    ("Doppelter Espresso", "https://www.youtube.com/feeds/videos.xml?channel_id=UCVEljrpqZg3o7UJZoWgjKQA"),
    ("IchBinFabian",       "https://www.youtube.com/feeds/videos.xml?channel_id=UCIQteZ7qbDXcrYWT8sYWtzw"),
    ("Felicia Simon",      "https://www.youtube.com/feeds/videos.xml?channel_id=UCM2u6Uvi5XBBlh5GDv4otsg"),
    ("Calvin Hollywood",   "https://www.youtube.com/feeds/videos.xml?channel_id=UCWIGLQhEkdlfpCCGP7oMbZg"),
    ("David Rau",          "https://www.youtube.com/feeds/videos.xml?channel_id=UC3OwD9SyZYcRYGSwXrN9iPw"),
    ("The Geek Freaks",    "https://www.youtube.com/feeds/videos.xml?channel_id=UCFWYwf9rNEnL3mmNSNXSL3Q"),
    ("Hellintech",         "https://www.youtube.com/feeds/videos.xml?channel_id=UCTlL9C9UgVUU_eU1RbnHUKw"),
]

def lade_json(pfad):
    with open(pfad, "r", encoding="utf-8") as f:
        return json.load(f)

def fortschrittsbalken(prozent, breite=15):
    gefuellt = int(breite * prozent / 100)
    return "█" * gefuellt + "░" * (breite - gefuellt)

def berechne_probezeit():
    heute = date.today()
    gesamt = (PROBEZEIT_ENDE - PROBEZEIT_START).days
    vergangen = max(0, min((heute - PROBEZEIT_START).days, gesamt))
    prozent = int((vergangen / gesamt) * 100)
    noch = (PROBEZEIT_ENDE - heute).days
    return vergangen, gesamt, prozent, noch, fortschrittsbalken(prozent)

def berechne_vertrag(vertrag):
    heute = date.today()
    start = date.fromisoformat(vertrag["start"])
    ende = date.fromisoformat(vertrag["ende"])
    gesamt = (ende - start).days
    vergangen = max(0, min((heute - start).days, gesamt))
    prozent = int((vergangen / gesamt) * 100)
    gesamt_monate = (ende.year - start.year) * 12 + (ende.month - start.month)
    vergangene_monate = (heute.year - start.year) * 12 + (heute.month - start.month)
    noch_monate = max(0, gesamt_monate - vergangene_monate)
    restbetrag = vertrag.get("schlussrate", 0) if noch_monate <= 1 else (noch_monate - 1) * vertrag["monatliche_rate"] + vertrag.get("schlussrate", 0)
    return prozent, noch_monate, restbetrag

def pruefe_alert(last_updated_str):
    delta = (date.today() - date.fromisoformat(last_updated_str)).days
    return delta >= ALERT_TAGE, delta

def refresh_fitbit_token():
    client_id     = os.getenv("FITBIT_CLIENT_ID")
    client_secret = os.getenv("FITBIT_CLIENT_SECRET")
    refresh_token = os.getenv("FITBIT_REFRESH_TOKEN")
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    r = requests.post("https://api.fitbit.com/oauth2/token",
        headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
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

def hole_youtube_neu(stunden=24):
    from time import mktime
    grenze = datetime.utcnow() - timedelta(hours=stunden)
    videos = []
    for kanal_name, feed_url in YOUTUBE_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                vp = entry.get("published_parsed")
                if vp and datetime.utcfromtimestamp(mktime(vp)) >= grenze:
                    videos.append((kanal_name, entry.get("title", ""), entry.get("link", "")))
        except:
            pass
    return videos

def sende_telegram(text, parse_mode=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    return requests.post(url, json=payload).status_code

# ═══════════════════════════════════
# MORNING DIGEST (täglich)
# ═══════════════════════════════════

def baue_morning_digest():
    datum = date.today().strftime("%d.%m.%Y")
    wochentag = ["Mo","Di","Mi","Do","Fr","Sa","So"][date.today().weekday()]
    lines = [f"☀️ *Guten Morgen Jens — {wochentag} {datum}*\n"]

    # Fitbit
    try:
        token = refresh_fitbit_token()
        user_id = os.getenv("FITBIT_USER_ID", "7PS3ZT")
        gestern = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        h = {"Authorization": f"Bearer {token}"}
        schritte = requests.get(f"https://api.fitbit.com/1/user/{user_id}/activities/date/{gestern}.json", headers=h).json().get("summary", {}).get("steps", 0)
        schlaf_min = requests.get(f"https://api.fitbit.com/1.2/user/{user_id}/sleep/date/{gestern}.json", headers=h).json().get("summary", {}).get("totalMinutesAsleep", 0)
        ruhepuls = requests.get(f"https://api.fitbit.com/1/user/{user_id}/activities/heart/date/{gestern}/1d.json", headers=h).json().get("activities-heart", [{}])[0].get("value", {}).get("restingHeartRate", 0)
        lines.append(f"💪 *Gestern ({gestern}):*")
        lines.append(f"👟 {schritte:,} Schritte  😴 {schlaf_min//60}h {schlaf_min%60:02d}min  ❤️ {ruhepuls} bpm\n")
    except Exception as e:
        lines.append(f"💪 Fitbit: Fehler ({e})\n")

    # The Decoder
    decoder_links = []
    try:
        feed = feedparser.parse("https://the-decoder.de/feed/")
        lines.append("🤖 *The Decoder — Neu:*")
        for entry in feed.entries[:3]:
            lines.append(f"• {entry.get('title', '')}")
            decoder_links.append(entry.get("link", ""))
        lines.append("")
    except:
        lines.append("🤖 The Decoder: nicht erreichbar\n")

    # YouTube
    videos = hole_youtube_neu(stunden=24)
    if videos:
        lines.append("📺 *Neue Videos (24h):*")
        for kanal, titel, link in videos[:8]:
            lines.append(f"• [{kanal}] {titel}")
        if len(videos) > 8:
            lines.append(f"• ...und {len(videos)-8} weitere")
    else:
        lines.append("📺 Keine neuen Videos in den letzten 24h")

    digest = "\n".join(lines)

    # Links separat
    yt_links_msg = ""
    if videos:
        yt_lines = ["🔗 <b>YouTube Links:</b>"]
        for kanal, titel, link in videos[:10]:
            if link:
                yt_lines.append(f"• <a href='{link}'>[{kanal}] {titel[:50]}</a>")
        yt_links_msg = "\n".join(yt_lines)

    dec_links_msg = ""
    if decoder_links:
        dec_lines = ["🔗 <b>The Decoder Links:</b>"]
        feed = feedparser.parse("https://the-decoder.de/feed/")
        for entry in feed.entries[:3]:
            link = entry.get("link", "")
            titel = entry.get("title", "")
            if link:
                dec_lines.append(f"• <a href='{link}'>{titel[:60]}</a>")
        dec_links_msg = "\n".join(dec_lines)

    return digest, dec_links_msg, yt_links_msg

# ═══════════════════════════════════
# WEEKLY DIGEST (Sonntag)
# ═══════════════════════════════════

def baue_digest():
    kw = date.today().isocalendar()[1]
    datum = date.today().strftime("%d.%m.%Y")
    lines = [f"📰 *JENS HQ — Weekly Digest KW{kw} ({datum})*\n"]

    # Probezeit
    vergangen, gesamt, prozent, noch, balken = berechne_probezeit()
    lines.append(f"🏢 *MOTECS Probezeit:*")
    lines.append(f"{balken} {prozent}%")
    lines.append(f"Tag {vergangen}/{gesamt} — noch {noch} Tage\n")

    # Fitbit
    try:
        token = refresh_fitbit_token()
        user_id = os.getenv("FITBIT_USER_ID", "7PS3ZT")
        gestern = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        h = {"Authorization": f"Bearer {token}"}
        schritte = requests.get(f"https://api.fitbit.com/1/user/{user_id}/activities/date/{gestern}.json", headers=h).json().get("summary", {}).get("steps", 0)
        schlaf_min = requests.get(f"https://api.fitbit.com/1.2/user/{user_id}/sleep/date/{gestern}.json", headers=h).json().get("summary", {}).get("totalMinutesAsleep", 0)
        ruhepuls = requests.get(f"https://api.fitbit.com/1/user/{user_id}/activities/heart/date/{gestern}/1d.json", headers=h).json().get("activities-heart", [{}])[0].get("value", {}).get("restingHeartRate", 0)
        lines.append(f"💪 *Gestern:* 👟 {schritte:,} | 😴 {schlaf_min//60}h {schlaf_min%60:02d}min | ❤️ {ruhepuls} bpm\n")
    except:
        lines.append("💪 Fitbit: Fehler\n")

    # Todos
    try:
        data = lade_json(TODOS_FILE)
        offene = [t for t in data["todos"] if t["prozent"] < 100]
        lines.append("📋 *Offene Todos:*")
        for todo in offene:
            ist_alert, delta = pruefe_alert(todo["last_updated"])
            symbol = "⚠️" if ist_alert else todo["prio"]
            lines.append(f"{symbol} {todo['name']} — {todo['prozent']}%")
        lines.append("")
    except:
        lines.append("📋 Todos: Fehler\n")

    # Verträge
    try:
        data = lade_json(VERTRAEGE_FILE)
        lines.append("💰 *Verträge:*")
        for v in data["vertraege"]:
            prozent, noch_monate, restbetrag = berechne_vertrag(v)
            lines.append(f"{v['emoji']} {v['name']}: {prozent}% | {noch_monate} Monate | ~{restbetrag:.0f}€")
        lines.append("")
    except:
        lines.append("💰 Verträge: Fehler\n")

    # Fokus
    try:
        fokus_file = os.path.join(VAULT_PATH, "fokus.json")
        data = lade_json(fokus_file)
        lines.append("🎯 *Fokus diese Woche:*")
        for p in data.get("fokus", [])[:3]:
            lines.append(f"» {p}")
        lines.append("")
    except:
        pass

    # IT Trends
    feeds = [
        ("Heise", "https://www.heise.de/developer/rss/news-atom.xml"),
        ("t3n", "https://t3n.de/feed/"),
        ("Decoder", "https://the-decoder.de/feed/"),
        ("Golem", "https://rss.golem.de/rss.php?feed=RSS2.0"),
    ]
    trend_links = []
    lines.append("📈 *IT/Cloud Trends:*")
    for name, url in feeds:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                titel = feed.entries[0].title
                link = feed.entries[0].get("link", "")
                lines.append(f"• [{name}] {titel}")
                trend_links.append((name, titel, link))
        except:
            pass
    lines.append("")

    # Zertifikate
    zert_links = [
        ("AZ-900", "Azure Fundamentals", "https://learn.microsoft.com/de-de/credentials/certifications/azure-fundamentals/"),
        ("SC-900", "Security Fundamentals", "https://learn.microsoft.com/de-de/credentials/certifications/security-compliance-and-identity-fundamentals/"),
        ("MD-102", "Endpoint Admin", "https://learn.microsoft.com/de-de/credentials/certifications/modern-desktop/"),
        ("AZ-104", "Azure Administrator", "https://learn.microsoft.com/de-de/credentials/certifications/azure-administrator/"),
    ]
    lines.append("🎓 *Zertifikate:*")
    lines.append("⏳ AZ-900 | 📅 SC-900 | 📅 MD-102 | 📅 AZ-104\n")

    # YouTube
    videos = hole_youtube_neu(stunden=168)
    if videos:
        lines.append("📺 *YouTube diese Woche:*")
        for kanal, titel, link in videos[:8]:
            lines.append(f"• [{kanal}] {titel}")
        if len(videos) > 8:
            lines.append(f"• ...und {len(videos)-8} weitere")
        lines.append("")

    # Quote
    quotes = [
        ("First, solve the problem. Then write the code.", "John Johnson"),
        ("Make it work, make it right, make it fast.", "Kent Beck"),
        ("Talk is cheap. Show me the code.", "Linus Torvalds"),
        ("The best time to start was yesterday.", "unbekannt"),
    ]
    q, autor = random.choice(quotes)
    lines.append(f"💬 _{q}_")
    lines.append(f"— {autor}")

    digest = "\n".join(lines)

    # Links Nachricht
    link_lines = ["🔗 <b>Links zum Digest:</b>\n", "<b>📈 IT Trends:</b>"]
    for name, titel, link in trend_links:
        if link:
            link_lines.append(f"• <a href='{link}'>[{name}] {titel[:50]}</a>")
    link_lines.append("\n<b>🎓 Zertifikate:</b>")
    for kuerzel, name, link in zert_links:
        link_lines.append(f"• <a href='{link}'>{kuerzel} — {name}</a>")
    if videos:
        link_lines.append("\n<b>📺 YouTube:</b>")
        for kanal, titel, link in videos[:10]:
            if link:
                link_lines.append(f"• <a href='{link}'>[{kanal}] {titel[:50]}</a>")

    return digest, "\n".join(link_lines)

def speichere_obsidian(text):
    kw = date.today().isocalendar()[1]
    jahr = date.today().year
    dateiname = f"WeeklyDigest_KW{kw:02d}_{jahr}.md"
    pfad = os.path.join(VAULT_PATH, dateiname)
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(f"# Weekly Digest KW{kw:02d} {jahr}\n\n{text}\n")
    print(f"✅ Obsidian gespeichert: {dateiname}")

if __name__ == "__main__":
    modus = sys.argv[1] if len(sys.argv) > 1 else ("weekly" if date.today().weekday() == 6 else "daily")

    if modus == "daily":
        print("☀️ Baue Morning Digest...")
        digest, dec_links, yt_links = baue_morning_digest()
        print(digest)
        sende_telegram(digest, parse_mode="Markdown")
        if dec_links:
            sende_telegram(dec_links, parse_mode="HTML")
        if yt_links:
            sende_telegram(yt_links, parse_mode="HTML")

    elif modus == "weekly":
        print("📰 Baue Weekly Digest...")
        digest, links_msg = baue_digest()
        print(digest)
        sende_telegram(digest, parse_mode="Markdown")
        sende_telegram(links_msg, parse_mode="HTML")
        speichere_obsidian(digest)