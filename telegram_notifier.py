"""
telegram_notifier.py
JensHQ – Telegram Automation System
Grundmodul für JensJobBot und JensLernBot
"""

import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────
#  BOT KONFIGURATION
# ──────────────────────────────────────────
BOTS = {
    "job": {
        "token": os.getenv("JOBBOT_TOKEN", ""),
        "name": "JensJobBot",
    },
    "lern": {
        "token": os.getenv("LERNBOT_TOKEN", ""),
        "name": "JensLernBot",
    },
    "deal": {
        "token": os.getenv("DEALBOT_TOKEN", ""),
        "name": "JensDealBot",
    },
}

CHAT_ID = os.getenv("CHAT_ID", "8656887627")

# ──────────────────────────────────────────
#  LOGGING
# ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(r"C:\JobAgent\logs\telegram_notifier.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────
#  KERN-FUNKTION
# ──────────────────────────────────────────
def send_message(bot_key: str, text: str, chat_id: str = CHAT_ID, parse_mode: str = "HTML") -> bool:
    """
    Sendet eine Nachricht über den angegebenen Bot.

    Args:
        bot_key:    'job' oder 'lern'
        text:       Nachrichtentext (HTML erlaubt)
        chat_id:    Ziel-Chat-ID (Standard: Jens)
        parse_mode: 'HTML' oder 'Markdown'

    Returns:
        True bei Erfolg, False bei Fehler
    """
    if bot_key not in BOTS:
        log.error(f"Unbekannter Bot-Key: '{bot_key}'. Erlaubt: {list(BOTS.keys())}")
        return False

    bot = BOTS[bot_key]
    url = f"https://api.telegram.org/bot{bot['token']}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get("ok"):
            log.info(f"[{bot['name']}] Nachricht erfolgreich gesendet.")
            return True
        else:
            log.error(f"[{bot['name']}] Telegram API Fehler: {result}")
            return False

    except requests.exceptions.Timeout:
        log.error(f"[{bot['name']}] Timeout beim Senden.")
        return False
    except requests.exceptions.RequestException as e:
        log.error(f"[{bot['name']}] Verbindungsfehler: {e}")
        return False


def send_job_message(text: str) -> bool:
    """Shortcut für JensJobBot."""
    return send_message("job", text)


def send_lern_message(text: str) -> bool:
    """Shortcut für JensLernBot."""
    return send_message("lern", text)


def send_deal_message(text: str) -> bool:
    """Shortcut für JensDealBot."""
    return send_message("deal", text)


# ──────────────────────────────────────────
#  TEST-FUNKTION
# ──────────────────────────────────────────
def test_bots():
    """Sendet Testnachrichten über beide Bots."""
    ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    job_msg = (
        f"✅ <b>JensJobBot – Verbindungstest</b>\n"
        f"────────────────────\n"
        f"🕐 Zeit: {ts}\n"
        f"📁 System: JensHQ JobAgent\n"
        f"Status: Bereit ✔️"
    )

    deal_msg = (
        f"✅ <b>JensDealBot – Verbindungstest</b>\n"
        f"────────────────────\n"
        f"🕐 Zeit: {ts}\n"
        f"🃏 System: JensHQ DealFinder\n"
        f"Status: Bereit ✔️"
    )

    lern_msg = (
        f"✅ <b>JensLernBot – Verbindungstest</b>\n"
        f"────────────────────\n"
        f"🕐 Zeit: {ts}\n"
        f"📚 System: JensHQ Lernplan\n"
        f"Status: Bereit ✔️"
    )

    print("\n── Teste JensJobBot ──")
    ok1 = send_job_message(job_msg)
    print(f"  → {'OK ✅' if ok1 else 'FEHLER ❌'}")

    print("\n── Teste JensLernBot ──")
    ok2 = send_lern_message(lern_msg)
    print(f"  → {'OK ✅' if ok2 else 'FEHLER ❌'}")

    print("\n── Teste JensDealBot ──")
    ok3 = send_deal_message(deal_msg)
    print(f"  → {'OK ✅' if ok3 else 'FEHLER ❌'}")

    print(f"\nErgebnis: {'Alle Bots OK ✅' if ok1 and ok2 and ok3 else 'Mindestens ein Bot fehlgeschlagen ❌'}")


# ──────────────────────────────────────────
#  DIREKT AUSFÜHRBAR
# ──────────────────────────────────────────
if __name__ == "__main__":
    test_bots()