"""
job_report_sender.py
JensHQ – JobAgent → JensJobBot
Liest jobs.csv und sendet Bericht der letzten 3 Tage per Telegram
Aufruf: täglich per Task Scheduler
"""

import csv
import os
import sys
import requests
from datetime import datetime, date, timedelta

import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from shared.telegram_notifier import send_job_message

# ──────────────────────────────────────────
#  KONFIGURATION
# ──────────────────────────────────────────
JOBS_CSV     = os.path.join(_ROOT, "jobagent", "jobs", "jobs.csv")
MAX_JOBS_MSG = 10
MIN_SCORE    = 17        # 33% von ~50 Max-Score
DAYS_WINDOW  = 3

REMOTE_KEYWORDS = ["remote", "homeoffice", "home office", "bundesweit", "deutschlandweit"]

SONDER_KEYWORDS = [
    "weihnachtsgeld", "urlaubsgeld", "13. gehalt", "13. monatsgehalt",
    "sonderzahlung", "jahressonderzahlung", "sondervergütung",
    "13. monatsentgelt", "weihnachtliche zuwendung"
]

def score_emoji(score: int) -> str:
    if score >= 40: return "🔥"
    if score >= 28: return "⭐"
    if score >= 17: return "✅"
    return "📋"


# ──────────────────────────────────────────
#  CSV EINLESEN
# ──────────────────────────────────────────
def load_jobs(csv_path: str) -> list[dict]:
    if not os.path.exists(csv_path):
        return []
    jobs = []
    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                normalized = {k.strip().lower(): v.strip() for k, v in row.items()}
                jobs.append(normalized)
    except Exception as e:
        print(f"Fehler beim Lesen der CSV: {e}")
    return jobs


# ──────────────────────────────────────────
#  SONDERZAHLUNGEN PRÜFEN
# ──────────────────────────────────────────
def check_sonderzahlungen(url: str) -> bool:
    """
    Ruft die Stellenanzeige ab und prüft ob Sonderzahlungs-Keywords vorkommen.
    Gibt True zurück wenn gefunden, False wenn nicht oder bei Fehler.
    """
    if not url:
        return False
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=8)
        text = r.text.lower()
        return any(kw in text for kw in SONDER_KEYWORDS)
    except Exception:
        return False


# ──────────────────────────────────────────
#  FILTER
# ──────────────────────────────────────────
def filter_jobs_recent(jobs: list[dict], days: int = DAYS_WINDOW) -> list[dict]:
    cutoff = date.today() - timedelta(days=days)
    result = []
    for j in jobs:
        raw = j.get("datum", "").strip()
        if not raw:
            result.append(j)
            continue
        try:
            fmt = "%Y-%m-%d" if "-" in raw else "%d.%m.%Y"
            if datetime.strptime(raw[:10], fmt).date() >= cutoff:
                result.append(j)
        except ValueError:
            result.append(j)
    return result if result else jobs


def filter_remote(jobs: list[dict]) -> list[dict]:
    return [
        j for j in jobs
        if not any(kw in j.get("ort", "").lower() for kw in REMOTE_KEYWORDS)
    ]

def split_remote(jobs: list) -> tuple:
    """Trennt lokale und Remote-Jobs."""
    lokal  = [j for j in jobs if not any(kw in j.get("ort","").lower() for kw in REMOTE_KEYWORDS)]
    remote = [j for j in jobs if any(kw in j.get("ort","").lower() for kw in REMOTE_KEYWORDS)]
    return lokal, remote


def filter_by_score(jobs: list[dict], min_score: int = MIN_SCORE) -> list[dict]:
    result = []
    for j in jobs:
        try:
            if int(j.get("score", 0)) >= min_score:
                result.append(j)
        except (ValueError, TypeError):
            result.append(j)
    return result


def sort_jobs(jobs: list[dict]) -> list[dict]:
    def get_score(j):
        try:
            return int(j.get("score", 0))
        except (ValueError, TypeError):
            return 0
    return sorted(jobs, key=get_score, reverse=True)


# ──────────────────────────────────────────
#  NACHRICHT ZUSAMMENBAUEN
# ──────────────────────────────────────────
def build_job_message(jobs: list[dict], total_found: int) -> str:
    today      = datetime.now().strftime("%d.%m.%Y")
    cutoff_str = (date.today() - timedelta(days=DAYS_WINDOW)).strftime("%d.%m.%Y")
    header = (
        f"💼 <b>JobAgent Bericht</b>\n"
        f"📅 {today} | letzte {DAYS_WINDOW} Tage (ab {cutoff_str})\n"
        f"────────────────────\n"
        f"📊 Gefunden: <b>{total_found}</b> | Relevant: <b>{len(jobs)}</b>\n\n"
    )

    if not jobs:
        return header + "ℹ️ Keine passenden Jobs in den letzten 3 Tagen.\n\nWeiter suchen! 💪"

    lines = []
    for i, job in enumerate(jobs[:MAX_JOBS_MSG], 1):
        titel     = job.get("titel",  "Unbekannt")
        firma     = job.get("firma",  "–")
        ort       = job.get("ort",    "–")
        score_raw = job.get("score",  "–")
        gehalt    = job.get("gehalt", "")
        url       = job.get("link",   job.get("url", ""))
        datum     = job.get("datum",  "")

        try:
            score_int = int(score_raw)
            emoji     = score_emoji(score_int)
            score_str = str(score_int)
        except (ValueError, TypeError):
            emoji     = "📋"
            score_str = str(score_raw)

        # Sonderzahlungen prüfen
        print(f"   [{i}] Prüfe Sonderzahlungen: {titel[:40]}...")
        sonder = check_sonderzahlungen(url)
        sonder_str = "✅" if sonder else "❌"

        block  = f"{emoji} <b>{i}. {titel}</b>\n"
        block += f"   🏢 {firma} | 📍 {ort}\n"
        block += f"   🎯 Score: {score_str}"
        if gehalt:
            block += f" | 💶 {gehalt}"
        block += "\n"
        block += f"   🎁 Sonderzahlungen: {sonder_str}"
        if datum:
            block += f" | 📆 {datum[:10]}"
        block += "\n"
        if url:
            block += f"   🔗 <a href='{url}'>Zum Job</a>\n"
        lines.append(block)

    body = "\n".join(lines)

    if len(jobs) > MAX_JOBS_MSG:
        body += f"\n<i>... und {len(jobs) - MAX_JOBS_MSG} weitere in jobs.csv</i>\n"

    footer = "\n────────────────────\n🤖 JensJobBot | JensHQ"
    return header + body + footer


# ──────────────────────────────────────────
#  HAUPTFUNKTION
# ──────────────────────────────────────────
def send_daily_job_report():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starte Job-Bericht (letzte {DAYS_WINDOW} Tage)...")

    all_jobs    = load_jobs(JOBS_CSV)
    recent_jobs = filter_jobs_recent(all_jobs)
    lokal_jobs, remote_jobs = split_remote(recent_jobs)
    filtered    = filter_by_score(lokal_jobs)
    sorted_jobs = sort_jobs(filtered)

    print(f"Scanne {min(len(sorted_jobs), MAX_JOBS_MSG)} Jobs auf Sonderzahlungen...")
    msg = build_job_message(sorted_jobs, total_found=len(recent_jobs))

    # Remote-Hinweis anhängen
    remote_relevant = filter_by_score(remote_jobs)
    if remote_relevant:
        msg += f"\n\n🌐 <b>{len(remote_relevant)} Remote-Job(s) verfügbar</b>\n"
        for rj in remote_relevant[:3]:
            titel = rj.get("titel", "–")[:50]
            score = rj.get("score", "–")
            url   = rj.get("link", rj.get("url", ""))
            msg += f"   • <a href=\'{url}\'>{titel}</a> (Score: {score})\n"
        if len(remote_relevant) > 3:
            msg += f"   <i>+ {len(remote_relevant)-3} weitere Remote-Jobs</i>\n"

    success = send_job_message(msg)

    if success:
        print("✅ Bericht erfolgreich gesendet.")
    else:
        print("❌ Fehler beim Senden.")

    return success


if __name__ == "__main__":
    send_daily_job_report()