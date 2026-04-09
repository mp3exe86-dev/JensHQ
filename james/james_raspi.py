# -*- coding: utf-8 -*-
"""
james_raspi.py
JensHQ — James RasPi Version
Läuft 24/7 auf RasPi als systemd Service.
Obsidian + Ollama werden über Netzwerk auf Windows angesprochen.
PC-Online-Check vor KI-Befehlen.
"""

import requests
import json
import time
import subprocess
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════
#  KONFIGURATION
# ══════════════════════════════════════════
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("JAMES_TOKEN", "")
CHAT_ID        = int(os.getenv("CHAT_ID", "8656887627"))
API_URL        = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Windows PC
PC_IP          = os.getenv("PC_IP", "192.168.178.80")
OBSIDIAN_URL   = f"https://{PC_IP}:27124"
OBSIDIAN_KEY   = os.getenv("OBSIDIAN_KEY", "")
OLLAMA_URL     = os.getenv("OLLAMA_URL", f"http://{PC_IP}:11434")
OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# RasPi Pfade
BASE           = os.getenv("BASE_PATH", "/home/jens/JobAgent")
TODOS_PFAD     = f"{BASE}/daten/todos.json"
FOKUS_PFAD     = f"{BASE}/daten/fokus.json"
QUEUE_PFAD     = f"{BASE}/queue.json"

POLL_SEC       = 3
SERVICES       = ["lernbot", "jobbot", "dealbot", "pokedexbot"]

# ══════════════════════════════════════════
#  PC ONLINE CHECK
# ══════════════════════════════════════════
def pc_online() -> bool:
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", PC_IP],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except:
        return False

def pc_check_oder_queue(befehl: str, args: list) -> bool:
    """Gibt True zurück wenn PC online, sonst in Queue speichern."""
    if pc_online():
        return True
    # In Queue speichern
    auftrag = befehl + " " + " ".join(args)
    try:
        queue = lade_queue()
        queue.append({
            "befehl": auftrag,
            "erstellt": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "offen"
        })
        speichere_queue(queue)
        send(
            f"💤 <b>PC ist offline</b>\n\n"
            f"📥 Auftrag gespeichert: <code>{auftrag}</code>\n"
            f"⏳ Wird ausgefuehrt wenn PC online ist"
        )
    except Exception as e:
        send(f"❌ Queue Fehler: {e}")
    return False

# ══════════════════════════════════════════
#  TELEGRAM
# ══════════════════════════════════════════
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
        print(f"[Telegram Fehler] {e}")
        return False

def get_updates(offset: int) -> list:
    try:
        r = requests.get(f"{API_URL}/getUpdates",
                         params={"offset": offset, "timeout": 2}, timeout=10)
        return r.json().get("result", []) if r.json().get("ok") else []
    except:
        return []

# ══════════════════════════════════════════
#  OBSIDIAN
# ══════════════════════════════════════════
def obs_read(path: str) -> str:
    try:
        r = requests.get(f"{OBSIDIAN_URL}/vault/{path}",
                         headers={"Authorization": f"Bearer {OBSIDIAN_KEY}", "Accept": "text/markdown"},
                         verify=False, timeout=10)
        return r.text if r.status_code == 200 else ""
    except:
        return ""

def obs_write(path: str, content: str) -> bool:
    try:
        r = requests.put(f"{OBSIDIAN_URL}/vault/{path}",
                         headers={"Authorization": f"Bearer {OBSIDIAN_KEY}", "Content-Type": "text/markdown"},
                         data=content.encode("utf-8"), verify=False, timeout=10)
        return r.status_code in [200, 201, 204]
    except:
        return False

# ══════════════════════════════════════════
#  OLLAMA
# ══════════════════════════════════════════
def ollama_analyse(frage: str) -> str:
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": frage}],
            "stream": False
        }
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=300)
        return r.json().get("message", {}).get("content", "Keine Antwort")
    except Exception as e:
        return f"Ollama Fehler: {e}"

# ══════════════════════════════════════════
#  QUEUE
# ══════════════════════════════════════════
def lade_queue() -> list:
    try:
        with open(QUEUE_PFAD, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def speichere_queue(queue: list):
    with open(QUEUE_PFAD, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

def verarbeite_queue():
    try:
        queue = lade_queue()
        offen = [q for q in queue if q.get("status") == "offen"]
        if not offen:
            return

        # Nur verarbeiten wenn PC online
        if not pc_online():
            return

        send(f"📥 <b>Queue: {len(offen)} offene Auftraege</b>\nPC online — verarbeite...")

        for auftrag in offen:
            befehl = auftrag.get("befehl", "")
            parts  = befehl.split()
            cmd    = parts[0].lower() if parts else ""

            try:
                if cmd == "todo":
                    handle_todo(parts[1:])
                elif cmd == "fokus":
                    handle_fokus(parts[1:])
                elif cmd == "analyse":
                    handle_analyse()
                elif cmd == "analyse_code":
                    handle_analyse_code(parts[1:])
                elif cmd == "restart":
                    handle_restart(parts[1] if len(parts) > 1 else "")
                auftrag["status"] = "erledigt"
                auftrag["erledigt"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            except Exception as e:
                auftrag["status"] = "fehler"
                auftrag["fehler"] = str(e)

        speichere_queue(queue)
        erledigt = len([q for q in queue if q["status"] == "erledigt"])
        send(f"✅ Queue abgearbeitet: {erledigt} Auftraege erledigt")

    except Exception as e:
        print(f"Queue Fehler: {e}")

# ══════════════════════════════════════════
#  BEFEHLS-HANDLER
# ══════════════════════════════════════════
def handle_status():
    try:
        service_lines = []
        for svc in SERVICES:
            result = subprocess.run(["systemctl", "is-active", svc],
                                    capture_output=True, text=True)
            status = result.stdout.strip()
            emoji  = "🟢" if status == "active" else "🔴"
            service_lines.append(f"{emoji} {svc}: {status}")

        cpu   = subprocess.run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'",
                               shell=True, capture_output=True, text=True).stdout.strip()
        ram   = subprocess.run("free -m | awk 'NR==2{printf \"%.0f%%\", $3*100/$2}'",
                               shell=True, capture_output=True, text=True).stdout.strip()
        disk  = subprocess.run("df -h / | awk 'NR==2{print $5}'",
                               shell=True, capture_output=True, text=True).stdout.strip()
        pc    = "🟢 Online" if pc_online() else "🔴 Offline"

        msg = (
            "📊 <b>JensHQ Status</b>\n"
            "────────────────────\n"
            "⚙️ <b>Services:</b>\n"
            + "\n".join(f"   {s}" for s in service_lines) + "\n"
            "────────────────────\n"
            f"💻 CPU: {cpu}% | 🧠 RAM: {ram} | 💾 Disk: {disk}\n"
            f"🖥️ Windows PC: {pc}"
        )
        send(msg)
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_logs(service: str, zeilen: int = 20):
    try:
        result = subprocess.run(
            ["journalctl", "-u", service, "-n", str(zeilen), "--no-pager"],
            capture_output=True, text=True
        )
        out = result.stdout.strip()
        if out:
            if len(out) > 3000:
                out = "..." + out[-3000:]
            send(f"📋 <b>Logs: {service}</b>\n<code>{out}</code>")
        else:
            send(f"ℹ️ Keine Logs fuer {service}")
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_restart(service: str):
    if service not in SERVICES:
        send(f"❌ Unbekannter Service. Verfuegbar: {', '.join(SERVICES)}")
        return
    try:
        subprocess.run(["sudo", "systemctl", "restart", service])
        time.sleep(2)
        result = subprocess.run(["systemctl", "is-active", service],
                                capture_output=True, text=True)
        status = result.stdout.strip()
        emoji  = "✅" if status == "active" else "❌"
        send(f"{emoji} {service} neugestartet. Status: {status}")
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_analyse():
    if not pc_check_oder_queue("analyse", []):
        return
    send("🧠 Analysiere Vault...")
    try:
        kontext = ""
        for datei in ["Wissen/JensHQ_System.md", "Wissen/Zertifizierungen.md", "Tasks/Offene_Aufgaben.md"]:
            inhalt = obs_read(datei)
            if inhalt:
                kontext += f"\n\n--- {datei} ---\n{inhalt[:2000]}"
        if not kontext:
            send("❌ Keine Vault-Dateien gefunden — ist Obsidian offen?")
            return
        frage = f"Analysiere meine Notizen. Was sind die wichtigsten offenen Punkte? Sei konkret und kurz.\n\n{kontext}"
        antwort = ollama_analyse(frage)
        obs_write(f"KI-Vorschlaege/James_Analyse_{datetime.now().strftime('%Y-%m-%d')}.md",
                  f"# James Analyse — {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{antwort}\n")
        if len(antwort) > 3000:
            antwort = antwort[:3000] + "...\n<i>(In Obsidian gespeichert)</i>"
        send(f"🧠 <b>James Analyse:</b>\n\n{antwort}")
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_analyse_code(args: list):
    if not args:
        send("❌ Nutzung: /analyse_code [datei]")
        return
    if not pc_check_oder_queue("analyse_code", args):
        return

    datei = args[0]
    pfad  = f"{BASE}/{datei}"
    send(f"🔍 Lese {datei}...")

    try:
        with open(pfad, "r", encoding="utf-8") as f:
            code_inhalt = f.read()

        if len(code_inhalt) > 6000:
            code_inhalt = code_inhalt[:6000]

        frage = (
            f"Du bist ein Python-Experte. Analysiere diesen Code aus '{datei}'.\n"
            f"1. Was macht dieser Code?\n"
            f"2. Gibt es Bugs oder potenzielle Fehler?\n"
            f"3. Was koennte man verbessern?\n\n"
            f"CODE:\n```python\n{code_inhalt}\n```"
        )
        send("🧠 Analysiere mit Ollama...")
        antwort = ollama_analyse(frage)

        obs_write(
            f"KI-Vorschlaege/CodeAnalyse_{datei}_{datetime.now().strftime('%Y-%m-%d_%H%M')}.md",
            f"# Code-Analyse: {datei}\n\n{antwort}\n"
        )

        if len(antwort) > 3500:
            antwort = antwort[:3500] + "\n<i>... (in Obsidian gespeichert)</i>"
        send(f"🧠 <b>Code-Analyse: {datei}</b>\n━━━━━━━━━━━━━━━━━━━━\n{antwort}")
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_todo(args: list):
    if not args:
        send("❌ Nutzung: /todo [ID] [PROZENT]")
        return

    if args[0].lower() == "list":
        try:
            with open(TODOS_PFAD, "r", encoding="utf-8") as f:
                data = json.load(f)
            offen = [t for t in data["todos"] if t["prozent"] < 100]
            msg = "📋 <b>Offene Todos:</b>\n\n"
            for t in offen:
                msg += f"{t['prio']} <b>#{t['id']}</b> {t['name']} — {t['prozent']}%\n"
            send(msg)
        except Exception as e:
            send(f"❌ Fehler: {e}")
        return

    if args[0].lower() == "add":
        name = " ".join(args[1:])
        try:
            with open(TODOS_PFAD, "r", encoding="utf-8") as f:
                data = json.load(f)
            max_id = max(t["id"] for t in data["todos"]) if data["todos"] else 0
            data["todos"].append({
                "id": max_id + 1, "name": name, "prio": "🟡",
                "prozent": 0, "details": "",
                "last_updated": datetime.now().strftime("%Y-%m-%d"), "aktiv": True
            })
            with open(TODOS_PFAD, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            send(f"➕ Todo hinzugefuegt: {name} (#{max_id + 1})")
        except Exception as e:
            send(f"❌ Fehler: {e}")
        return

    try:
        todo_id = int(args[0])
        prozent = int(args[1])
        with open(TODOS_PFAD, "r", encoding="utf-8") as f:
            data = json.load(f)
        for todo in data["todos"]:
            if todo["id"] == todo_id:
                alter = todo["prozent"]
                todo["prozent"] = prozent
                todo["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                if prozent >= 100:
                    todo["aktiv"] = False
                    todo["prio"] = "✅"
                with open(TODOS_PFAD, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                send(f"📝 {todo['name']}: {alter}% → {prozent}%")
                return
        send(f"❌ Todo #{todo_id} nicht gefunden")
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_fokus(args: list):
    if not args:
        send("❌ Nutzung: /fokus [text]")
        return
    fokus_text = " ".join(args)
    try:
        with open(FOKUS_PFAD, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["fokus"].append(fokus_text)
        data["fokus"] = data["fokus"][-3:]
        with open(FOKUS_PFAD, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        send("🎯 <b>Fokus aktualisiert</b>\n\n" + "\n".join(f"» {p}" for p in data["fokus"]))
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_hilfe():
    send(
        "🤖 <b>James RasPi — Befehle</b>\n\n"
        "/status — RasPi + PC Status\n"
        "/logs [service] — Logs anzeigen\n"
        "/restart [service] — Service neustarten\n"
        "/analyse — Vault analysieren (PC nötig)\n"
        "/analyse_code [datei] — Code analysieren (PC nötig)\n"
        "/todo [ID] [PROZENT] — Todo updaten\n"
        "/todo add [name] — Neues Todo\n"
        "/todo list — Alle Todos\n"
        "/fokus [text] — Fokus updaten\n"
        "/hilfe — Diese Hilfe\n\n"
        f"<i>Services: {', '.join(SERVICES)}</i>\n"
        f"<i>PC IP: {PC_IP}</i>"
    )


# ══════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════
def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] James RasPi gestartet.")
    pc_status = "🟢 Online" if pc_online() else "🔴 Offline"
    send(
        f"🤖 <b>James RasPi ist online!</b>\n\n"
        f"🖥️ Windows PC: {pc_status}\n"
        f"Tippe /hilfe fuer alle Befehle."
    )

    verarbeite_queue()

    last_update_id = 0
    queue_check    = 0

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
                text = msg.get("text", "").strip()
                ts   = datetime.now().strftime("%H:%M:%S")
                print(f"[{ts}] Empfangen: '{text}'")
                parts = text.split()
                cmd   = parts[0].lower() if parts else ""

                if cmd == "/status":
                    handle_status()
                elif cmd == "/logs":
                    svc = parts[1] if len(parts) > 1 else "pokedexbot"
                    handle_logs(svc)
                elif cmd == "/restart":
                    svc = parts[1] if len(parts) > 1 else ""
                    if svc:
                        handle_restart(svc)
                    else:
                        send("❌ Nutzung: /restart [service]")
                elif cmd == "/analyse_code":
                    handle_analyse_code(parts[1:])
                elif cmd == "/analyse":
                    handle_analyse()
                elif cmd == "/todo":
                    handle_todo(parts[1:])
                elif cmd == "/fokus":
                    handle_fokus(parts[1:])
                elif cmd in ["/hilfe", "/help", "/start"]:
                    handle_hilfe()

            # Queue alle 5 Minuten prüfen
            queue_check += 1
            if queue_check >= 100:
                verarbeite_queue()
                queue_check = 0

            time.sleep(POLL_SEC)

        except KeyboardInterrupt:
            print("\nJames gestoppt.")
            break
        except Exception as e:
            print(f"[FEHLER] {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()