"""
jobbot_service.py
JensHQ – JensJobBot Service
Lauscht dauerhaft, reagiert auf /jobs Befehl
Start: python3 jobbot_service.py
"""

import os
import requests
import subprocess
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN    = os.getenv("JOBBOT_TOKEN", "")
CHAT_ID  = int(os.getenv("CHAT_ID", "8656887627"))
API_URL  = f"https://api.telegram.org/bot{TOKEN}"
BASE     = os.getenv("BASE_PATH", "/home/jens/JobAgent")
POLL_SEC = 3


def send(text: str) -> bool:
    try:
        r = requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[FEHLER] Senden: {e}")
        return False


def get_updates(offset: int) -> list:
    try:
        r = requests.get(f"{API_URL}/getUpdates", params={
            "offset": offset, "timeout": 2
        }, timeout=10)
        data = r.json()
        return data.get("result", []) if data.get("ok") else []
    except Exception:
        return []


def run_jobs_scan():
    """Startet jobfinder_agent + job_report_sender."""
    send("🔍 <b>JobAgent gestartet...</b>\nSuche neue Stellen, dauert ~30 Sekunden.")
    try:
        subprocess.run(["python3", f"{BASE}/agents/jobfinder_agent.py"], cwd=BASE, timeout=120)
        subprocess.run(["python3", f"{BASE}/job_report_sender.py"],      cwd=BASE, timeout=60)
    except subprocess.TimeoutExpired:
        send("⚠️ JobAgent Timeout – zu lange gelaufen.")
    except Exception as e:
        send(f"❌ JobAgent Fehler: {e}")


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] JensJobBot Service gestartet.")
    last_update_id = 0

    while True:
        try:
            updates = get_updates(last_update_id + 1)

            for update in updates:
                last_update_id = update["update_id"]
                msg = update.get("message", {})
                if not msg:
                    continue
                if msg.get("chat", {}).get("id") != CHAT_ID:
                    continue

                text = msg.get("text", "").strip().lower()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Empfangen: '{text}'")

                if text in ["/jobs", "/jobscan", "/start"]:
                    t = threading.Thread(target=run_jobs_scan, daemon=True)
                    t.start()
                elif text == "/hilfe":
                    send("💼 <b>JensJobBot – Befehle</b>\n\n/jobs – JobAgent jetzt starten\n/hilfe – Diese Hilfe")

            time.sleep(POLL_SEC)

        except KeyboardInterrupt:
            print("\nService gestoppt.")
            break
        except Exception as e:
            print(f"[FEHLER] {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()