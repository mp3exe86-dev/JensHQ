# -*- coding: utf-8 -*-
"""
james_agent.py
JensHQ — James, der autonome KI-Agent
Liest Aufgaben aus Obsidian, fuehrt sie per SSH auf dem RasPi aus,
meldet Ergebnisse via Telegram zurueck.

Aufruf: python james_agent.py
Telegram Befehle:
  /status    — RasPi Status
  /logs      — Letzte Log-Eintraege
  /restart [service] — Service neustarten
  /aufgaben  — Offene Aufgaben aus Obsidian
  /analyse   — Vault analysieren
  /analyse_code [datei] — Code auf RasPi analysieren
  /fix_code [datei] [problem] — Code analysieren + Fix vorschlagen
  /deploy_fix [datei] — Fix deployen + Service neustarten
  /deploy [datei] — Datei auf RasPi deployen
  /todo [ID] [PROZENT] — Todo updaten
  /todo add [name] — Neues Todo hinzufuegen
  /todo list — Alle Todos anzeigen
  /fokus [text] — Fokus updaten
  /queue [befehl] — Auftrag in Queue speichern
"""

import requests
import paramiko
import json
import time
import urllib3
import sys
import os
from datetime import datetime

urllib3.disable_warnings()

# ══════════════════════════════════════════
#  KONFIGURATION
# ══════════════════════════════════════════
TELEGRAM_TOKEN = "8462751325:AAEh60tfD67v4Qdl6PPv_iLjYXAJ5XFSWfE"
CHAT_ID        = 8656887627
API_URL        = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

RASPI_HOST     = "192.168.178.47"
RASPI_USER     = "jens"
RASPI_KEY_PATH = r"C:\Users\Jens\.ssh\id_rsa"
RASPI_PASS     = "Eins23456-"

OBSIDIAN_URL   = "https://localhost:27124"
OBSIDIAN_KEY   = "26b5285e80b76a9b8f309cea78853022399bf50ef468bbd6c9b75ac9a860f795"

OLLAMA_URL     = "http://localhost:11434"
OLLAMA_MODEL   = "gemma3:4b"

POLL_SEC       = 3

SERVICES = ["lernbot", "jobbot", "dealbot", "pokedexbot"]

TODOS_PFAD       = r"C:\JobAgent\vault\SecondBrain\todos.json"
TODOS_RASPI_PFAD = "/home/jens/JobAgent/shared/daten/todos.json"
FOKUS_PFAD       = r"C:\JobAgent\vault\SecondBrain\fokus.json"
FOKUS_RASPI_PFAD = "/home/jens/JobAgent/shared/daten/fokus.json"
QUEUE_PFAD       = "/home/jens/JobAgent/queue.json"

FIX_CACHE: dict = {}

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
    except Exception:
        return []


# ══════════════════════════════════════════
#  SSH FUNKTIONEN
# ══════════════════════════════════════════
def ssh_verbinden():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if RASPI_PASS:
            client.connect(RASPI_HOST, username=RASPI_USER, password=RASPI_PASS,
               timeout=10, look_for_keys=False, allow_agent=False)
        else:
            client.connect(RASPI_HOST, username=RASPI_USER, key_filename=RASPI_KEY_PATH, timeout=10)
        return client
    except Exception as e:
        raise Exception(f"SSH Verbindung fehlgeschlagen: {e}")


def ssh_befehl(befehl: str) -> tuple:
    client = ssh_verbinden()
    try:
        stdin, stdout, stderr = client.exec_command(befehl, timeout=30)
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()
        code = stdout.channel.recv_exit_status()
        return out, err, code
    finally:
        client.close()


def ssh_datei_hochladen(lokal: str, remote: str) -> bool:
    client = ssh_verbinden()
    try:
        sftp = client.open_sftp()
        sftp.put(lokal, remote)
        sftp.close()
        return True
    except Exception as e:
        print(f"SFTP Fehler: {e}")
        return False
    finally:
        client.close()


# ══════════════════════════════════════════
#  OBSIDIAN FUNKTIONEN
# ══════════════════════════════════════════
def obs_read(path: str) -> str:
    try:
        r = requests.get(f"{OBSIDIAN_URL}/vault/{path}",
                         headers={"Authorization": f"Bearer {OBSIDIAN_KEY}", "Accept": "text/markdown"},
                         verify=False, timeout=10)
        return r.text if r.status_code == 200 else ""
    except Exception:
        return ""


def obs_write(path: str, content: str) -> bool:
    try:
        r = requests.put(f"{OBSIDIAN_URL}/vault/{path}",
                         headers={"Authorization": f"Bearer {OBSIDIAN_KEY}", "Content-Type": "text/markdown"},
                         data=content.encode("utf-8"), verify=False, timeout=10)
        return r.status_code in [200, 201, 204]
    except Exception:
        return False


def obs_get_aufgaben() -> list:
    inhalt = obs_read("Tasks/Offene_Aufgaben.md")
    aufgaben = []
    for zeile in inhalt.splitlines():
        if zeile.strip().startswith("- [ ]"):
            aufgaben.append(zeile.strip()[6:].strip())
    return aufgaben


# ══════════════════════════════════════════
#  OLLAMA
# ══════════════════════════════════════════
def ollama_analyse(kontext: str, frage: str) -> str:
    try:
        prompt = frage if not kontext else f"Notizen:\n\n{kontext}\n\nFrage: {frage}"
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=300)
        return r.json().get("message", {}).get("content", "Keine Antwort")
    except Exception as e:
        return f"Ollama Fehler: {e}"


# ══════════════════════════════════════════
#  QUEUE FUNKTIONEN
# ══════════════════════════════════════════
def lade_queue() -> list:
    try:
        out, _, _ = ssh_befehl(f"cat {QUEUE_PFAD}")
        return json.loads(out) if out else []
    except:
        return []

def speichere_queue(queue: list):
    inhalt = json.dumps(queue, ensure_ascii=False, indent=2)
    inhalt_escaped = inhalt.replace("'", "'\"'\"'")
    ssh_befehl(f"echo '{inhalt_escaped}' > {QUEUE_PFAD}")

def handle_queue(args: list):
    if not args:
        send("❌ Nutzung: /queue [befehl]\nBeispiel: /queue todo 5 100")
        return

    auftrag = " ".join(args)
    try:
        queue = lade_queue()
        queue.append({
            "befehl": auftrag,
            "erstellt": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "offen"
        })
        speichere_queue(queue)
        send(
            f"📥 <b>Auftrag in Queue gespeichert</b>\n\n"
            f"📋 Befehl: {auftrag}\n"
            f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            f"⏳ Wird ausgefuehrt wenn PC online ist"
        )
    except Exception as e:
        send(f"❌ Fehler: {e}")

def verarbeite_queue():
    try:
        queue = lade_queue()
        offen = [q for q in queue if q.get("status") == "offen"]
        if not offen:
            return

        send(f"📥 <b>Queue: {len(offen)} offene Auftraege</b>\nVerarbeite...")

        for auftrag in offen:
            befehl = auftrag.get("befehl", "")
            parts = befehl.split()
            cmd = parts[0].lower() if parts else ""

            try:
                if cmd == "todo":
                    handle_todo(parts[1:])
                elif cmd == "deploy":
                    handle_deploy(parts[1] if len(parts) > 1 else "")
                elif cmd == "restart":
                    handle_restart(parts[1] if len(parts) > 1 else "")
                elif cmd == "fokus":
                    handle_fokus(parts[1:])
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
    send("🔍 Pruefe RasPi Status...")
    try:
        service_lines = []
        for svc in SERVICES:
            out, _, code = ssh_befehl(f"systemctl is-active {svc}")
            emoji = "🟢" if out.strip() == "active" else "🔴"
            service_lines.append(f"{emoji} {svc}: {out.strip()}")
        cpu_out, _, _ = ssh_befehl("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
        ram_out, _, _ = ssh_befehl("free -m | awk 'NR==2{printf \"%.0f%%\", $3*100/$2}'")
        disk_out, _, _ = ssh_befehl("df -h / | awk 'NR==2{print $5}'")
        msg = (
            "📊 <b>RasPi Status</b>\n"
            "────────────────────\n"
            "⚙️ <b>Services:</b>\n"
            + "\n".join(f"   {s}" for s in service_lines) + "\n"
            "────────────────────\n"
            f"💻 CPU: {cpu_out.strip()}% | 🧠 RAM: {ram_out.strip()} | 💾 Disk: {disk_out.strip()}"
        )
        send(msg)
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_logs(service: str = "pokedexbot", zeilen: int = 20):
    send(f"📋 Lade Logs von {service}...")
    try:
        out, err, _ = ssh_befehl(f"journalctl -u {service} -n {zeilen} --no-pager")
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
    send(f"🔄 Starte {service} neu...")
    try:
        out, err, code = ssh_befehl(f"sudo systemctl restart {service}")
        time.sleep(2)
        status_out, _, _ = ssh_befehl(f"systemctl is-active {service}")
        emoji = "✅" if status_out.strip() == "active" else "❌"
        send(f"{emoji} {service} neugestartet. Status: {status_out.strip()}")
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_aufgaben():
    aufgaben = obs_get_aufgaben()
    if not aufgaben:
        send("✅ Keine offenen Aufgaben gefunden.")
        return
    msg = "📋 <b>Offene Aufgaben:</b>\n\n"
    for i, a in enumerate(aufgaben, 1):
        msg += f"{i}. {a}\n"
    send(msg)


def handle_analyse():
    send("🧠 Analysiere Vault...")
    try:
        kontext = ""
        for datei in ["JensHQ_System.md", "Zertifizierungen.md", "Tasks/Offene_Aufgaben.md"]:
            inhalt = obs_read(datei)
            if inhalt:
                kontext += f"\n\n--- {datei} ---\n{inhalt[:2000]}"
        if not kontext:
            send("❌ Keine Vault-Dateien gefunden")
            return
        antwort = ollama_analyse(kontext,
            "Analysiere meine Notizen. Was sind die wichtigsten offenen Punkte? "
            "Was sollte ich als naechstes tun? Sei konkret und kurz.")
        datum = datetime.now().strftime("%Y-%m-%d %H:%M")
        obs_write(f"KI-Vorschlaege/James_Analyse_{datetime.now().strftime('%Y-%m-%d')}.md",
                  f"# James Analyse — {datum}\n\n{antwort}\n")
        if len(antwort) > 3000:
            antwort = antwort[:3000] + "...\n\n<i>(In Obsidian gespeichert)</i>"
        send(f"🧠 <b>James Analyse:</b>\n\n{antwort}")
    except Exception as e:
        send(f"❌ Fehler bei Analyse: {e}")


def handle_analyse_code(args: list):
    if not args:
        send(
            "❌ Nutzung: /analyse_code [datei]\n"
            "Beispiel: /analyse_code lernbot_service.py\n"
            "Beispiel: /analyse_code agents/jobfinder_agent.py"
        )
        return

    datei = args[0]
    remote_pfad = f"/home/jens/JobAgent/{datei}"
    send(f"🔍 Lese {datei} vom RasPi...")

    try:
        out, err, code = ssh_befehl(f"cat {remote_pfad}")
        if code != 0 or not out:
            send(f"❌ Datei nicht gefunden: {remote_pfad}\n{err}")
            return

        code_inhalt = out
        gekuerzt = False
        if len(code_inhalt) > 6000:
            code_inhalt = code_inhalt[:6000]
            gekuerzt = True

        send(f"🧠 Analysiere mit Ollama ({len(code_inhalt)} Zeichen)...")

        frage = (
            f"Du bist ein Python-Experte. Analysiere diesen Code aus '{datei}'.\n\n"
            f"Beantworte auf Deutsch:\n"
            f"1. Was macht dieser Code?\n"
            f"2. Gibt es Bugs oder potenzielle Fehler?\n"
            f"3. Was koennte man verbessern?\n"
            f"4. Gibt es auffaellige Stellen die Probleme machen koennten?\n\n"
            f"Sei konkret, kurz und praxisorientiert.\n\n"
            f"CODE:\n```python\n{code_inhalt}\n```"
        )

        antwort = ollama_analyse("", frage)

        if gekuerzt:
            antwort = "⚠️ Datei war zu lang, nur erste 6000 Zeichen analysiert.\n\n" + antwort

        datum = datetime.now().strftime("%Y-%m-%d_%H%M")
        obs_pfad = f"KI-Vorschlaege/CodeAnalyse_{datei.replace('/', '_')}_{datum}.md"
        obs_inhalt = (
            f"# Code-Analyse: {datei}\n"
            f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"{antwort}\n\n"
            f"---\n🔗 **Verknuepft mit:** [[JensHQ_System]] | [[James_Ollama_Agent]]\n"
        )
        obs_write(obs_pfad, obs_inhalt)

        if len(antwort) > 3500:
            antwort = antwort[:3500] + "\n\n<i>... (vollstaendig in Obsidian gespeichert)</i>"

        send(
            f"🧠 <b>Code-Analyse: {datei}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{antwort}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>📝 In Obsidian gespeichert</i>"
        )

    except Exception as e:
        send(f"❌ Fehler bei Code-Analyse: {e}")


def handle_fix_code(args: list):
    if len(args) < 2:
        send(
            "❌ Nutzung: /fix_code [datei] [problembeschreibung]\n"
            "Beispiel: /fix_code lernbot_service.py Duplikate werden gesendet"
        )
        return

    datei = args[0]
    problem = " ".join(args[1:])
    remote_pfad = f"/home/jens/JobAgent/{datei}"

    send(
        f"🔧 <b>Fix-Modus gestartet</b>\n\n"
        f"📄 Datei: {datei}\n"
        f"🐛 Problem: {problem}\n\n"
        f"⏳ Lese Code vom RasPi..."
    )

    try:
        out, err, code = ssh_befehl(f"cat {remote_pfad}")
        if code != 0 or not out:
            send(f"❌ Datei nicht gefunden: {remote_pfad}")
            return

        code_inhalt = out
        gekuerzt = False
        if len(code_inhalt) > 5000:
            code_inhalt = code_inhalt[:5000]
            gekuerzt = True
            send("⚠️ Datei gekuerzt auf 5000 Zeichen fuer Analyse.")

        send("🧠 Ollama analysiert und erstellt Fix...")

        frage = (
            f"Du bist ein Python-Experte. Hier ist Code aus '{datei}'.\n"
            f"Problem: {problem}\n\n"
            f"Aufgabe:\n"
            f"1. Analysiere den Bug kurz (2-3 Saetze)\n"
            f"2. Zeige NUR die geaenderten Zeilen als vollstaendigen korrekten Code-Block\n"
            f"3. Erklaere was du geaendert hast (1-2 Saetze)\n\n"
            f"Antworte in diesem Format:\n"
            f"ANALYSE: [kurze Analyse]\n"
            f"FIX: [vollstaendiger korrigierter Code-Block]\n"
            f"ERKLAERUNG: [was wurde geaendert]\n\n"
            f"CODE:\n```python\n{code_inhalt}\n```"
        )

        antwort = ollama_analyse("", frage)

        analyse    = ""
        fix_code   = ""
        erklaerung = ""

        if "ANALYSE:" in antwort:
            analyse = antwort.split("ANALYSE:")[1].split("FIX:")[0].strip()
        if "FIX:" in antwort:
            fix_block = antwort.split("FIX:")[1]
            if "ERKLAERUNG:" in fix_block:
                fix_code = fix_block.split("ERKLAERUNG:")[0].strip()
                erklaerung = antwort.split("ERKLAERUNG:")[1].strip()
            else:
                fix_code = fix_block.strip()

        fix_code = fix_code.replace("```python", "").replace("```", "").strip()

        if not fix_code:
            send(
                f"🧠 <b>Analyse:</b>\n{analyse}\n\n"
                f"⚠️ Kein automatischer Fix moeglich — zu komplex.\n"
                f"Bitte manuell pruefen."
            )
            return

        fix_preview = fix_code[:800] + "..." if len(fix_code) > 800 else fix_code
        send(
            f"🧠 <b>Analyse:</b>\n{analyse}\n\n"
            f"🔧 <b>Vorgeschlagener Fix:</b>\n"
            f"<code>{fix_preview}</code>\n\n"
            f"💡 <b>Erklaerung:</b>\n{erklaerung}\n\n"
            f"⚠️ <b>Deploy mit /deploy_fix {datei} bestaetigen</b>"
        )

        datum = datetime.now().strftime("%Y-%m-%d_%H%M")
        obs_pfad = f"KI-Vorschlaege/Fix_{datei.replace('/', '_')}_{datum}.md"
        obs_inhalt = (
            f"# Code-Fix: {datei}\n"
            f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            f"Problem: {problem}\n\n"
            f"## Analyse\n{analyse}\n\n"
            f"## Fix\n```python\n{fix_code}\n```\n\n"
            f"## Erklaerung\n{erklaerung}\n\n"
            f"---\n🔗 **Verknuepft mit:** [[JensHQ_System]] | [[James_Ollama_Agent]]\n"
        )
        obs_write(obs_pfad, obs_inhalt)

        FIX_CACHE[datei] = {
            "fix_code": fix_code,
            "remote":   remote_pfad,
            "service":  datei.split("/")[-1].replace(".py", "").replace("_service", ""),
        }

    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_deploy_fix(args: list):
    if not args:
        send("❌ Nutzung: /deploy_fix [datei]\nBeispiel: /deploy_fix lernbot_service.py")
        return

    datei = args[0]
    if datei not in FIX_CACHE:
        send("❌ Kein Fix im Cache. Bitte zuerst /fix_code ausfuehren.")
        return

    fix = FIX_CACHE[datei]
    remote_pfad = fix["remote"]
    service     = fix["service"]

    send(f"📤 Deploye Fix fuer {datei}...")

    try:
        # 1. Backup auf RasPi erstellen
        out, err, code = ssh_befehl(f"cp {remote_pfad} {remote_pfad}.bak")
        if code != 0:
            send(f"⚠️ Backup fehlgeschlagen: {err}\nDeploy abgebrochen.")
            return

        # 2. Fix lokal als Temp-Datei speichern
        temp_pfad = r"C:\JobAgent\_james_fix_temp.py"
        with open(temp_pfad, "w", encoding="utf-8") as f:
            f.write(fix["fix_code"])

        # 3. Via SFTP hochladen
        if not ssh_datei_hochladen(temp_pfad, remote_pfad):
            send("❌ Upload fehlgeschlagen.")
            return

        # 4. Temp-Datei lokal loeschen
        os.remove(temp_pfad)

        # 5. Syntax-Check auf RasPi
        send("🔍 Pruefe Python-Syntax...")
        out, err, code = ssh_befehl(f"python3 -m py_compile {remote_pfad}")
        if code != 0:
            send(
                f"❌ <b>Syntax-Fehler im Fix!</b>\n"
                f"<code>{err}</code>\n\n"
                f"♻️ Stelle Backup wieder her..."
            )
            ssh_befehl(f"cp {remote_pfad}.bak {remote_pfad}")
            send("✅ Backup wiederhergestellt. Kein Schaden entstanden.")
            return

        # 6. Service neustarten wenn bekannt
        if service in SERVICES:
            send(f"🔄 Starte {service} neu...")
            ssh_befehl(f"sudo systemctl restart {service}")
            time.sleep(3)
            status, _, _ = ssh_befehl(f"systemctl is-active {service}")
            emoji = "✅" if status.strip() == "active" else "❌"

            if status.strip() != "active":
                send(
                    f"❌ Service {service} laeuft nicht!\n"
                    f"♻️ Stelle Backup wieder her..."
                )
                ssh_befehl(f"cp {remote_pfad}.bak {remote_pfad}")
                ssh_befehl(f"sudo systemctl restart {service}")
                time.sleep(2)
                status2, _, _ = ssh_befehl(f"systemctl is-active {service}")
                send(f"✅ Backup wiederhergestellt. Service: {status2.strip()}")
                return

            send(
                f"✅ <b>Fix erfolgreich deployed!</b>\n\n"
                f"📄 {datei}\n"
                f"🔄 Service {service}: {status.strip()}\n"
                f"💾 Backup: {remote_pfad}.bak\n"
                f"📝 Fix in Obsidian gespeichert"
            )
        else:
            send(
                f"✅ <b>Fix deployed!</b>\n\n"
                f"📄 {datei}\n"
                f"💾 Backup: {remote_pfad}.bak\n"
                f"⚠️ Service unbekannt — bitte manuell neustarten"
            )

        # 7. Cache leeren
        del FIX_CACHE[datei]

    except Exception as e:
        send(f"❌ Fehler beim Deploy: {e}")
        # Sicherheitshalber Backup wiederherstellen
        try:
            ssh_befehl(f"cp {remote_pfad}.bak {remote_pfad}")
            send("♻️ Backup sicherheitshalber wiederhergestellt.")
        except:
            pass


def handle_deploy(datei_name: str):
    lokal = f"C:/JobAgent/{datei_name}"
    remote = f"/home/jens/JobAgent/{datei_name}"
    if not os.path.exists(lokal):
        send(f"❌ Datei nicht gefunden: {lokal}")
        return
    send(f"📤 Deploye {datei_name}...")
    try:
        if ssh_datei_hochladen(lokal, remote):
            send(f"✅ {datei_name} deployed nach {remote}")
        else:
            send(f"❌ Deploy fehlgeschlagen")
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_fokus(args: list):
    if not args:
        send("❌ Nutzung: /fokus [text]\nBeispiel: /fokus AZ-900 Woche 2")
        return

    fokus_text = " ".join(args)
    try:
        with open(FOKUS_PFAD, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["fokus"].append(fokus_text)
        data["fokus"] = data["fokus"][-3:]

        with open(FOKUS_PFAD, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        ssh_datei_hochladen(FOKUS_PFAD, FOKUS_RASPI_PFAD)

        send(
            f"🎯 <b>Fokus aktualisiert</b>\n\n"
            + "\n".join(f"» {p}" for p in data["fokus"])
        )
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_todo_add(args: list):
    if not args:
        send("❌ Nutzung: /todo add [name]\nBeispiel: /todo add Neues Projekt")
        return

    name = " ".join(args)
    try:
        with open(TODOS_PFAD, "r", encoding="utf-8") as f:
            data = json.load(f)

        max_id = max(t["id"] for t in data["todos"]) if data["todos"] else 0

        neues_todo = {
            "id": max_id + 1,
            "name": name,
            "prio": "🟡",
            "prozent": 0,
            "details": "",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "aktiv": True
        }
        data["todos"].append(neues_todo)

        with open(TODOS_PFAD, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        ssh_datei_hochladen(TODOS_PFAD, TODOS_RASPI_PFAD)

        send(
            f"➕ <b>Todo hinzugefuegt</b>\n\n"
            f"📋 {name}\n"
            f"🆔 ID: {max_id + 1}\n"
            f"📅 {datetime.now().strftime('%d.%m.%Y')}"
        )
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_todo_list():
    try:
        with open(TODOS_PFAD, "r", encoding="utf-8") as f:
            data = json.load(f)

        offen = [t for t in data["todos"] if t["prozent"] < 100]
        if not offen:
            send("✅ Keine offenen Todos!")
            return

        msg = "📋 <b>Offene Todos:</b>\n\n"
        for t in offen:
            msg += f"{t['prio']} <b>#{t['id']}</b> {t['name']} — {t['prozent']}%\n"

        send(msg)
    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_todo(args: list):
    if not args:
        send(
            "❌ Nutzung:\n"
            "/todo [ID] [PROZENT] — updaten\n"
            "/todo add [name] — neu hinzufuegen\n"
            "/todo list — alle anzeigen"
        )
        return

    if args[0].lower() == "add":
        handle_todo_add(args[1:])
        return
    if args[0].lower() == "list":
        handle_todo_list()
        return

    try:
        todo_id = int(args[0])
        prozent = int(args[1])
        if not 0 <= prozent <= 100:
            send("❌ Prozent muss zwischen 0 und 100 liegen")
            return
    except (ValueError, IndexError):
        send("❌ Nutzung: /todo [ID] [PROZENT]\nBeispiel: /todo 3 100")
        return

    try:
        with open(TODOS_PFAD, "r", encoding="utf-8") as f:
            data = json.load(f)

        gefunden = False
        alter_wert = 0
        name = ""
        for todo in data["todos"]:
            if todo["id"] == todo_id:
                alter_wert = todo["prozent"]
                todo["prozent"] = prozent
                todo["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                if prozent >= 100:
                    todo["aktiv"] = False
                    todo["prio"] = "✅"
                gefunden = True
                name = todo["name"]
                break

        if not gefunden:
            send(f"❌ Todo ID {todo_id} nicht gefunden")
            return

        with open(TODOS_PFAD, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        ssh_datei_hochladen(TODOS_PFAD, TODOS_RASPI_PFAD)

        emoji = "✅" if prozent >= 100 else "📝"
        send(
            f"{emoji} <b>Todo aktualisiert</b>\n\n"
            f"📋 {name}\n"
            f"📊 {alter_wert}% → {prozent}%\n"
            f"📅 {datetime.now().strftime('%d.%m.%Y')}"
        )

    except Exception as e:
        send(f"❌ Fehler: {e}")


def handle_hilfe():
    send(
        "🤖 <b>James — Befehle</b>\n\n"
        "/status — RasPi Service Status\n"
        "/logs [service] — Logs anzeigen\n"
        "/restart [service] — Service neustarten\n"
        "/aufgaben — Offene Aufgaben aus Obsidian\n"
        "/analyse — Vault mit KI analysieren\n"
        "/analyse_code [datei] — Code analysieren\n"
        "/fix_code [datei] [problem] — Fix vorschlagen\n"
        "/deploy_fix [datei] — Fix deployen + neustarten\n"
        "/deploy [datei] — Datei manuell deployen\n"
        "/todo [ID] [PROZENT] — Todo updaten\n"
        "/todo add [name] — Neues Todo\n"
        "/todo list — Alle Todos anzeigen\n"
        "/fokus [text] — Fokus updaten\n"
        "/queue [befehl] — Auftrag in Queue speichern\n"
        "/hilfe — Diese Hilfe\n\n"
        f"<i>Services: {', '.join(SERVICES)}</i>"
    )


# ══════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════
def main():
    if not TELEGRAM_TOKEN:
        print("FEHLER: Kein Telegram Token gesetzt!")
        sys.exit(1)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] James gestartet.")
    send(
        "🤖 <b>James ist online!</b>\n\n"
        "Ich bin dein autonomer Agent.\n"
        "Tippe /hilfe fuer alle Befehle."
    )

    verarbeite_queue()

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
                text = msg.get("text", "").strip()
                ts = datetime.now().strftime("%H:%M:%S")
                print(f"[{ts}] Empfangen: '{text}'")
                parts = text.split()
                cmd = parts[0].lower() if parts else ""

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
                        send("❌ Nutzung: /restart [service]\nServices: " + ", ".join(SERVICES))
                elif cmd == "/aufgaben":
                    handle_aufgaben()
                elif cmd == "/analyse_code":
                    handle_analyse_code(parts[1:])
                elif cmd == "/fix_code":
                    handle_fix_code(parts[1:])
                elif cmd == "/deploy_fix":
                    handle_deploy_fix(parts[1:])
                elif cmd == "/analyse":
                    handle_analyse()
                elif cmd == "/deploy":
                    datei = parts[1] if len(parts) > 1 else ""
                    if datei:
                        handle_deploy(datei)
                    else:
                        send("❌ Nutzung: /deploy [dateiname]")
                elif cmd == "/todo":
                    handle_todo(parts[1:])
                elif cmd == "/fokus":
                    handle_fokus(parts[1:])
                elif cmd == "/queue":
                    handle_queue(parts[1:])
                elif cmd in ["/hilfe", "/help", "/start"]:
                    handle_hilfe()

            time.sleep(POLL_SEC)
        except KeyboardInterrupt:
            print("\nJames gestoppt.")
            break
        except Exception as e:
            print(f"[FEHLER] {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()