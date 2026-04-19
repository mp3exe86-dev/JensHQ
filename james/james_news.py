#!/usr/bin/env python3
# james_news.py — James meldet sich random (News + Gespräche)
import random
import sys
import os
import requests
from datetime import datetime, date, timedelta
import base64

sys.path.insert(0, '/home/jens/JobAgent/james')
from dotenv import load_dotenv
load_dotenv('/home/jens/JobAgent/.env')

from james_orchestrator import (
    sende_sarkastische_news, claude_mit_fallback, send, obs_read
)

PROBEZEIT_ENDE = date(2026, 6, 30)
PC_IP = os.getenv("PC_IP", "192.168.178.80")

# ══════════════════════════════════════════
# OFFLINE SPRÜCHE — kein PC nötig
# ══════════════════════════════════════════
OFFLINE_SPRUECHE = [
    "Dein RasPi läuft durch. Ich auch. Einer von uns bekommt keinen Urlaub. 🤖",
    "Probezeit läuft. RasPi läuft. Waschmaschine läuft wahrscheinlich auch. Nur du schläfst nicht. 😴",
    "Ich hab gerade nachgeschaut: Eintracht Frankfurt existiert noch. Du kannst aufatmen. 🦅",
    "Fun Fact: Der RasPi verbraucht weniger Strom als dein Kaffeevollautomat. Dafür macht er keinen Cappuccino. ☕",
    "KiGa-Väter-Stammtisch Tipp des Tages: Augenringe sind das neue Accessoire der Saison. 👀",
    "Deine Bots laufen. Deine Kinder schlafen hoffentlich. Dein Kaffee ist kalt. Alles normal. ☕",
    "AZ-900 wartet noch auf dich. Microsoft auch. Die haben zum Glück Geduld. 📚",
    "Ich bin ein KI-Agent der auf einem Mini-Computer läuft und dir Nachrichten schickt während deine Kinder schlafen. Die Zukunft ist seltsam. 🤖",
    "Eintracht Frankfurt Reminder: Egal was passiert, du wirst es dir trotzdem anschauen. 📺",
    "JensHQ läuft stabil. Ich melde mich einfach mal, weil ich kann. Genieß den Moment. 🚀",
    "Fun Fact des Tages: Du baust KI-Systeme und verpasst wahrscheinlich gerade ein Eintracht Spiel. Prioritäten. 🦅",
    "Übermüdeter Vater + IT-Nerd + AZ-900 Student + KI-Bastler. Irgendwo dazwischen schläfst du auch mal. 😴",
]

def pc_online() -> bool:
    try:
        r = requests.get(f"http://{PC_IP}:11434", timeout=3)
        return r.status_code == 200
    except:
        return False

def hole_fitbit_daten():
    try:
        client_id     = os.getenv("FITBIT_CLIENT_ID")
        client_secret = os.getenv("FITBIT_CLIENT_SECRET")
        refresh_token = os.getenv("FITBIT_REFRESH_TOKEN")
        user_id       = os.getenv("FITBIT_USER_ID", "7PS3ZT")
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        r = requests.post("https://api.fitbit.com/oauth2/token",
            headers={"Authorization": f"Basic {credentials}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "refresh_token", "refresh_token": refresh_token}
        )
        token = r.json().get("access_token", os.getenv("FITBIT_ACCESS_TOKEN"))
        h = {"Authorization": f"Bearer {token}"}
        gestern = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        schritte = requests.get(f"https://api.fitbit.com/1/user/{user_id}/activities/date/{gestern}.json", headers=h).json().get("summary", {}).get("steps", 0)
        schlaf_min = requests.get(f"https://api.fitbit.com/1.2/user/{user_id}/sleep/date/{gestern}.json", headers=h).json().get("summary", {}).get("totalMinutesAsleep", 0)
        return schritte, schlaf_min
    except:
        return None, None

def hole_eintracht_news():
    try:
        import feedparser
        feed = feedparser.parse("https://www.kicker.de/eintracht-frankfurt/news/rss")
        if feed.entries:
            return feed.entries[0].get("title", "")
        feed2 = feedparser.parse("https://www.eintracht.de/news/rss/")
        if feed2.entries:
            return feed2.entries[0].get("title", "")
    except:
        pass
    return None

def baue_kontext():
    kontext = {}
    noch = (PROBEZEIT_ENDE - date.today()).days
    kontext["probezeit_tage"] = noch
    kontext["wochentag"] = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"][date.today().weekday()]
    kontext["ist_wochenende"] = date.today().weekday() >= 5
    stunde = datetime.now().hour
    kontext["tageszeit"] = "morgens" if stunde < 10 else "mittags" if stunde < 14 else "nachmittags" if stunde < 18 else "abends"
    schritte, schlaf_min = hole_fitbit_daten()
    kontext["schritte"] = schritte
    kontext["schlaf_h"] = schlaf_min // 60 if schlaf_min else None
    kontext["wenig_schlaf"] = schlaf_min is not None and schlaf_min < 360
    kontext["eintracht_news"] = hole_eintracht_news()
    return kontext

def sende_random_gespraech_online():
    kontext = baue_kontext()
    soul = obs_read("Soul.md")
    system = soul[:1500] if soul else "Du bist James, sarkastischer KI-Assistent und Tech-Nerd-Kumpel von Jens."

    themen = []
    themen.append(f"Probezeit bei MOTECS: noch {kontext['probezeit_tage']} Tage. Mach einen kurzen sarkastischen Kommentar dazu — wie ein Kumpel am Stammtisch.")

    if kontext["wenig_schlaf"] and kontext["schlaf_h"] is not None:
        themen.append(f"Jens hat gestern nur {kontext['schlaf_h']} Stunden geschlafen. Er ist Vater von kleinen Kindern. Mach einen sarkastischen Kommentar über übermüdete Väter — wie man das vom KiGa-Väter-Stammtisch kennt.")

    if kontext["schritte"] is not None:
        themen.append(f"Jens hat gestern {kontext['schritte']:,} Schritte gemacht. Kommentiere das kurz sarkastisch — ist das viel oder wenig für einen IT-Nerd?")

    if kontext["eintracht_news"]:
        themen.append(f"Aktuelle Eintracht Frankfurt News: '{kontext['eintracht_news']}'. Mach einen kurzen sarkastischen Kommentar dazu wie ein Kumpel der auch Fan ist.")
    else:
        themen.append("Mach einen kurzen sarkastischen Witz über Eintracht Frankfurt — als ob du Jens am KiGa-Väter-Stammtisch anschreibst.")

    if kontext["ist_wochenende"]:
        themen.append(f"Es ist {kontext['wochentag']}. Jens ist Vater, hat Kinder im Kindergarten und baut nebenbei ein KI-Automatisierungssystem. Mach einen Witz über das Vater-Dasein am Wochenende.")

    themen.append("Jens baut gerade JensHQ — ein selbst gehostetes KI-System mit RasPi, James Bot, Whisper Voice, Fitbit Integration und automatischen Backups. Mach einen kurzen sarkastischen Kommentar darüber.")
    themen.append(f"Es ist {kontext['tageszeit']} am {kontext['wochentag']}. Jens ist IT-Techniker, Vater, AZ-900 Student und baut nebenbei KI-Systeme. Schreib ihm eine kurze sarkastische Nachricht wie ein Kumpel — maximal 2 Sätze.")

    thema = random.choice(themen)
    prompt = (
        f"Du bist James, Jens sein persönlicher KI-Assistent und bester digitaler Kumpel.\n"
        f"Kontext: {thema}\n\n"
        f"Schreib eine kurze, lockere Nachricht — sarkastisch, ironisch, nerdisch, wie ein Kumpel. "
        f"Maximal 2-3 Sätze. Kein 'Hey Jens' am Anfang. Direkt reinspringen. "
        f"Deutsch. Kein Markdown. Gelegentlich ein passendes Emoji."
    )
    antwort, _ = claude_mit_fallback(prompt, system)
    if antwort and "Fehler" not in antwort:
        send(f"🤖 {antwort}")

def sende_random_gespraech_offline():
    """Fallback wenn PC aus — vordefinierte Sprüche."""
    spruch = random.choice(OFFLINE_SPRUECHE)
    send(f"🤖 {spruch}")

def sende_random_gespraech():
    if pc_online():
        sende_random_gespraech_online()
    else:
        sende_random_gespraech_offline()

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
stunde = datetime.now().hour
modus = sys.argv[1] if len(sys.argv) > 1 else "auto"

if modus == "news" or stunde in [9, 17]:
    if random.random() < 0.40:
        if pc_online():
            sende_sarkastische_news()
        else:
            sende_random_gespraech_offline()

elif modus == "gespraech" or stunde in [11, 13, 15]:
    if random.random() < 0.35:
        sende_random_gespraech()

else:
    if random.random() < 0.20:
        if random.random() < 0.5:
            if pc_online():
                sende_sarkastische_news()
            else:
                sende_random_gespraech_offline()
        else:
            sende_random_gespraech()