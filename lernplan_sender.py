"""
lernplan_sender.py
JensHQ – LernBot Tagesplan
Sendet morgens den Lernimpuls + erste Quizfrage
Aufruf: täglich 07:30 per Task Scheduler
"""

import sys
import random
from datetime import datetime, date

sys.path.insert(0, r"/home/jens/JobAgent")
from telegram_notifier import send_lern_message
from lernbot_quiz import FRAGEN, THEMEN
import json, os

TRACKER = r"/home/jens/JobAgent/daten/lernbot_tracker.json"

LERNIMPULSE = {
    "Cloud-Konzepte": {
        "impuls": "IaaS = Du verwaltest OS. PaaS = Du verwaltest nur Code. SaaS = Du nutzt nur die App.",
        "link": "https://learn.microsoft.com/de-de/training/modules/describe-cloud-service-types/"
    },
    "SLA-Regeln": {
        "impuls": "Composite SLA = SLA_A × SLA_B. Zwei Dienste mit 99,9% ergeben ~99,8% gesamt.",
        "link": "https://learn.microsoft.com/de-de/training/modules/describe-benefits-use-cloud-services/"
    },
    "Identity & Security": {
        "impuls": "AuthN = Wer bist du? AuthZ = Was darfst du? Zero Trust: Verify, Least Privilege, Assume Breach.",
        "link": "https://learn.microsoft.com/de-de/training/modules/describe-azure-identity-access-security/"
    },
    "Pricing & Cost Management": {
        "impuls": "TCO Calc = On-Prem vs Cloud Vergleich. Pricing Calc = konkrete Azure Kosten berechnen.",
        "link": "https://azure.microsoft.com/de-de/pricing/calculator/"
    },
    "Governance": {
        "impuls": "RBAC = Wer darf etwas tun. Policy = Was darf getan werden. Hierarchie: MG → Sub → RG → Resource.",
        "link": "https://learn.microsoft.com/de-de/training/modules/describe-features-tools-azure-for-governance-compliance/"
    },
    "Azure Dienste": {
        "impuls": "Blob = unstrukturierte Daten. Azure SQL = PaaS Datenbank. VNet = isoliertes Netzwerk in Azure.",
        "link": "https://learn.microsoft.com/de-de/training/paths/azure-fundamentals-describe-azure-architecture-services/"
    },
}

MOTIVATIONS = [
    "Jeden Tag ein bisschen besser. 📈",
    "Fokus heute, AZ-900 bald. 🎯",
    "Cloud-Wissen wächst Schritt für Schritt. ☁️",
    "MOTECS wartet – bring dein Wissen mit! 🚀",
    "AZ-900 → AZ-104 → SC-900. Der Weg ist klar. 🗺️",
    "Du schaffst das! 💪",
]

def get_schwachstes_thema() -> str:
    """Liest Tracker und gibt schwächstes Thema zurück."""
    if not os.path.exists(TRACKER):
        return random.choice(THEMEN)
    try:
        with open(TRACKER, encoding="utf-8") as f:
            tracker = json.load(f)
        themen_data = tracker.get("themen", {})
        # Thema mit schlechtester Quote
        def quote(t):
            d = themen_data.get(t, {"richtig": 0, "falsch": 0})
            total = d["richtig"] + d["falsch"]
            if total == 0:
                return -1  # Noch nie gespielt → höchste Prio
            return d["richtig"] / total
        return min(THEMEN, key=quote)
    except Exception:
        return random.choice(THEMEN)

def send_tagesplan():
    thema      = get_schwachstes_thema()
    impuls     = LERNIMPULSE.get(thema, {})
    today      = date.today().strftime("%d.%m.%Y")
    wochentag  = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"][date.today().weekday()]
    motivation = MOTIVATIONS[date.today().day % len(MOTIVATIONS)]

    msg = (
        f"📚 <b>Guten Morgen! Lernplan {wochentag}, {today}</b>\n"
        f"────────────────────\n"
        f"🎯 <b>Fokus heute: {thema}</b>\n\n"
        f"💡 {impuls.get('impuls', '')}\n\n"
        f"🔗 <a href='{impuls.get('link', '')}'>Microsoft Learn öffnen</a>\n"
        f"────────────────────\n"
        f"🧠 Bereit für das Quiz? Schreib <b>/frage</b> an den LernBot!\n\n"
        f"✨ {motivation}\n"
        f"🤖 JensLernBot | JensHQ"
    )

    success = send_lern_message(msg)
    if success:
        print("✅ Tagesplan gesendet.")
    else:
        print("❌ Fehler beim Senden.")

if __name__ == "__main__":
    send_tagesplan()