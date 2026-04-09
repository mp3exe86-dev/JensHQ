# -*- coding: utf-8 -*-
"""
james_orchestrator.py
JensHQ — James Orchestrator v1
James empfängt freie Textnachrichten, analysiert die Absicht
und entscheidet selbst welches Tool er nutzt:
  - Einfach (Todo/Fokus/Status/Restart) → James direkt
  - Code-Analyse/Fix → Ollama lokal
  - Komplex/Planung/Vault → Claude API

Workflow:
  1. Nachricht empfangen
  2. Absicht erkennen (Keyword + Ollama)
  3. Tool wählen
  4. Ausführen
  5. Backup wenn nötig
  6. "Erledigt — bitte freigeben" melden
"""

import requests
import paramiko
import json
import time
import subprocess
import os
import urllib3
from datetime import datetime

urllib3.disable_warnings()

# ══════════════════════════════════════════
#  KONFIGURATION
# ══════════════════════════════════════════
import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN  = os.getenv("JAMES_TOKEN", "")
CHAT_ID         = int(os.getenv("CHAT_ID", "8656887627"))
API_URL         = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

RASPI_HOST      = os.getenv("RASPI_HOST", "192.168.178.47")
RASPI_USER      = os.getenv("RASPI_USER", "jens")
RASPI_PASS      = os.getenv("RASPI_PASS", "")

PC_IP           = os.getenv("PC_IP", "192.168.178.80")
OBSIDIAN_URL    = f"https://{PC_IP}:27124"
OBSIDIAN_KEY    = os.getenv("OBSIDIAN_KEY", "")

OLLAMA_URL      = os.getenv("OLLAMA_URL", f"http://{PC_IP}:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "gemma3:4b")

CLAUDE_API_KEY  = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_MODEL    = "claude-sonnet-4-20250514"

BASE            = os.getenv("BASE_PATH", "/home/jens/JobAgent")
TODOS_PFAD      = f"{BASE}/daten/todos.json"
FOKUS_PFAD      = f"{BASE}/daten/fokus.json"
QUEUE_PFAD      = f"{BASE}/queue.json"
BACKUP_PFAD     = f"{BASE}/backups"

SERVICES        = ["lernbot", "jobbot", "dealbot", "pokedexbot"]
POLL_SEC        = 3

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
#  SSH
# ══════════════════════════════════════════
def ssh_befehl(befehl: str) -> tuple:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(RASPI_HOST, username=RASPI_USER, password=RASPI_PASS,
                       timeout=10, look_for_keys=False, allow_agent=False)
        stdin, stdout, stderr = client.exec_command(befehl, timeout=30)
        out  = stdout.read().decode("utf-8", errors="replace").strip()
        err  = stderr.read().decode("utf-8", errors="replace").strip()
        code = stdout.channel.recv_exit_status()
        return out, err, code
    finally:
        client.close()

def ssh_upload(lokal: str, remote: str) -> bool:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(RASPI_HOST, username=RASPI_USER, password=RASPI_PASS,
                       timeout=10, look_for_keys=False, allow_agent=False)
        sftp = client.open_sftp()
        sftp.put(lokal, remote)
        sftp.close()
        return True
    except:
        return False
    finally:
        client.close()

# ══════════════════════════════════════════
#  OBSIDIAN
# ══════════════════════════════════════════
def obs_read(path: str) -> str:
    try:
        r = requests.get(f"{OBSIDIAN_URL}/vault/{path}",
                         headers={"Authorization": f"Bearer {OBSIDIAN_KEY}",
                                  "Accept": "text/markdown"},
                         verify=False, timeout=10)
        return r.text if r.status_code == 200 else ""
    except:
        return ""

def obs_write(path: str, content: str) -> bool:
    try:
        r = requests.put(f"{OBSIDIAN_URL}/vault/{path}",
                         headers={"Authorization": f"Bearer {OBSIDIAN_KEY}",
                                  "Content-Type": "text/markdown"},
                         data=content.encode("utf-8"), verify=False, timeout=10)
        return r.status_code in [200, 201, 204]
    except:
        return False

def obs_lese_kontext() -> str:
    """Liest die wichtigsten Vault-Dateien als Kontext."""
    kontext = ""
    dateien = [
        "Wissen/JensHQ_System.md",
        "Wissen/Zertifizierungen.md",
        "Wissen/Azure_AZ900.md",
        "Tasks/Offene_Aufgaben.md",
    ]
    for d in dateien:
        inhalt = obs_read(d)
        if inhalt:
            kontext += f"\n\n--- {d} ---\n{inhalt[:1500]}"
    return kontext

# ══════════════════════════════════════════
#  OLLAMA
# ══════════════════════════════════════════
def ollama(prompt: str, system: str = "") -> str:
    try:
        messages = []
        if system:
            messages.append({"role": "user", "content": system})
            messages.append({"role": "assistant", "content": "Verstanden."})
        messages.append({"role": "user", "content": prompt})

        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        }, timeout=300)
        return r.json().get("message", {}).get("content", "")
    except Exception as e:
        return f"Ollama Fehler: {e}"

# ══════════════════════════════════════════
#  CLAUDE API
# ══════════════════════════════════════════
def claude_api(prompt: str, system: str = "") -> str:
    try:
        headers = {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        body = {
            "model": CLAUDE_MODEL,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            body["system"] = system

        r = requests.post("https://api.anthropic.com/v1/messages",
                          headers=headers, json=body, timeout=60)
        data = r.json()
        if "content" in data:
            return data["content"][0]["text"]
        return f"Claude API Fehler: {data}"
    except Exception as e:
        return f"Claude API Fehler: {e}"

# ══════════════════════════════════════════
#  BACKUP
# ══════════════════════════════════════════
def backup_datei(remote_pfad: str) -> str:
    """Erstellt Backup einer RasPi-Datei, gibt Backup-Pfad zurück."""
    datum    = datetime.now().strftime("%Y%m%d_%H%M%S")
    dateiname = remote_pfad.split("/")[-1]
    backup   = f"{BACKUP_PFAD}/{dateiname}.{datum}.bak"
    ssh_befehl(f"mkdir -p {BACKUP_PFAD} && cp {remote_pfad} {backup}")
    return backup

# ══════════════════════════════════════════
#  ABSICHT ERKENNEN
# ══════════════════════════════════════════
DIREKT_KEYWORDS = {
    "status":   ["status", "läuft", "services", "cpu", "ram"],
    "logs":     ["logs", "log", "fehler", "error"],
    "restart":  ["neustart", "restart", "neustarten"],
    "todo":     ["todo", "aufgabe", "erledigt", "prozent", "%"],
    "fokus":    ["fokus", "fokussiere", "konzentriere"],
    "pokemon":  ["ich habe", "habe ich", "basis ", "fossil ", "dschungel ", "pokemon sammlung", "wie weit bin ich", "sammlung status"],
}

OLLAMA_KEYWORDS = [
    "analysiere", "analyse", "code", "bug", "fehler", "fix",
    "schau", "prüfe", "überprüfe", "optimiere", "verbessere",
    "lernplan", "plan", "erkläre", "erklar", "lerne", "lernen",
    "zertifikat", "az-900", "az900", "notiz", "obsidian",
    "schreibe", "erstelle", "zusammenfassung", "idee", "vorschlag",
    "warum", "wie funktioniert", "was ist", "was sind",
    "grafana", "kubernetes", "docker", "terraform", "cloud"
]

# Claude API nur bei expliziter Anfrage
CLAUDE_KEYWORDS = [
    "frag claude",
    "claude api",
    "nutze claude",
]

def erkenne_absicht(text: str) -> str:
    """Erkennt ob direkt/ollama/claude zuständig ist."""
    t = text.lower()

    # Direkte Befehle
    for kategorie, keywords in DIREKT_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            return f"direkt:{kategorie}"

    # Ollama für Code/Analyse
    if any(kw in t for kw in OLLAMA_KEYWORDS):
        return "ollama"

    # Claude für komplexe/Vault Aufgaben
    if any(kw in t for kw in CLAUDE_KEYWORDS):
        return "claude"

    # Fallback: Ollama entscheiden lassen
    return "ollama_entscheiden"


# ══════════════════════════════════════════
#  POKEMON SAMMLUNG
# ══════════════════════════════════════════
POKEMON_MD_PFAD      = "/home/jens/JobAgent/daten/Pokemon_Sammlung.md"
POKEMON_WINDOWS_PFAD = r"C:\JobAgent\vault\SecondBrain\Pokemon_Sammlung.md"

SET_GESAMT = {"basis": 102, "fossil": 62, "dschungel": 64}
SET_ALIASES = {
    "basis": ["basis", "base", "base set", "basis-set"],
    "fossil": ["fossil"],
    "dschungel": ["dschungel", "jungle"],
}

def erkenne_set(text: str) -> str:
    t = text.lower()
    for set_name, aliases in SET_ALIASES.items():
        if any(a in t for a in aliases):
            return set_name
    return None

def erkenne_kartennummer(text: str):
    """Extrahiert Kartennummer wie 4/102 oder gibt None zurück."""
    import re
    match = re.search(r'(\d{1,3})/(\d{1,3})', text)
    if match:
        return match.group(0)
    return None

def erkenne_kartenname(text: str, set_name: str) -> str:
    """Extrahiert Pokémon-Name aus Text — alles nach Set-Name."""
    t = text.lower()
    for alias_list in SET_ALIASES.values():
        for alias in alias_list:
            if alias in t:
                # Alles nach dem Set-Alias ist der Name
                idx = t.find(alias) + len(alias)
                name = text[idx:].strip()
                # Zahl und "doch nicht" etc. entfernen
                name = re.sub(r'\d+/\d+', '', name).strip()
                name = re.sub(r'(doch nicht|nicht mehr|falsch|raus|entfernen)', '', name, flags=re.IGNORECASE).strip()
                if name:
                    return name
    # Kein Set-Name — ganzen Text als Name nehmen
    clean = re.sub(r'(ich habe|habe ich|doch nicht|nicht mehr|falsch|raus)', '', text, flags=re.IGNORECASE)
    clean = re.sub(r'\d+/\d+', '', clean).strip()
    return clean if len(clean) > 2 else None

def zaehle_vorhanden(md_inhalt: str, set_name: str) -> int:
    """Zählt abgehakte Karten in einem Set."""
    count = 0
    in_set = False
    set_header = {"basis": "Basis-Set", "fossil": "Fossil", "dschungel": "Dschungel"}
    header = set_header.get(set_name, "")
    
    for zeile in md_inhalt.splitlines():
        if header in zeile and "##" in zeile:
            in_set = True
        elif in_set and zeile.startswith("## ") and header not in zeile:
            in_set = False
        if in_set and zeile.strip().startswith("- [x]"):
            count += 1
    return count

def hake_karte_ab(md_inhalt: str, suchbegriff: str, rueckgaengig: bool = False) -> tuple:
    """Hakt eine Karte ab oder wieder raus. Suche nach Nummer oder Name."""
    zeilen = md_inhalt.splitlines()
    # Nummer normalisieren: "4/102" → "04", "04/102" → "04"
    suchbegriff_norm = suchbegriff.strip()
    if "/" in suchbegriff_norm:
        try:
            nr = int(suchbegriff_norm.split("/")[0])
            suchbegriff_norm = f"{nr:02d}"
        except:
            pass

    for i, zeile in enumerate(zeilen):
        zeile_lower = zeile.lower()
        # Treffer wenn Nummer oder Name in Zeile
        treffer = (
            f" {suchbegriff_norm} " in zeile or
            zeile.startswith(f"- [ ] {suchbegriff_norm} ") or
            zeile.startswith(f"- [x] {suchbegriff_norm} ") or
            suchbegriff.lower() in zeile_lower
        )
        if treffer:
            if not rueckgaengig and zeile.strip().startswith("- [ ]"):
                zeilen[i] = zeile.replace("- [ ]", "- [x]", 1)
                kartenname = zeile.strip()[6:].strip()
                return "\n".join(zeilen), True, kartenname
            elif rueckgaengig and zeile.strip().startswith("- [x]"):
                zeilen[i] = zeile.replace("- [x]", "- [ ]", 1)
                kartenname = zeile.strip()[6:].strip()
                return "\n".join(zeilen), True, kartenname
    return md_inhalt, False, ""

def pokemon_karte_eintragen(text: str):
    """Hakt eine Pokémon-Karte ab oder wieder raus und aktualisiert Fortschritt."""
    rueckgaengig = any(kw in text.lower() for kw in ["doch nicht", "nicht mehr", "falsch", "raus", "entfernen"])
    set_name  = erkenne_set(text)
    kartennr  = erkenne_kartennummer(text)

    # Wenn keine Nummer — versuche Name
    suchbegriff = kartennr
    if not kartennr:
        kartenname_suche = erkenne_kartenname(text, set_name)
        if kartenname_suche:
            suchbegriff = kartenname_suche
        else:
            send("❌ Karte nicht erkannt. Beispiel: 'Ich habe Basis 4/102' oder 'Ich habe Glurak'")
            return

    if not set_name:
        # Set aus Nummer erraten
        try:
            nr = int(kartennr.split("/")[0])
            total = int(kartennr.split("/")[1])
            if total == 102:
                set_name = "basis"
            elif total == 62:
                set_name = "fossil"
            elif total == 64:
                set_name = "dschungel"
        except:
            send("❌ Set nicht erkannt. Beispiel: 'Ich habe Basis 4/102'")
            return

    try:
        # Datei lokal lesen
        with open(POKEMON_MD_PFAD, "r", encoding="utf-8") as f:
            md_inhalt = f.read()

        # Karte abhaken
        neuer_inhalt, erfolg, kartenname = hake_karte_ab(md_inhalt, suchbegriff, rueckgaengig)

        if not erfolg:
            # Prüfen ob schon abgehakt
            for zeile in md_inhalt.splitlines():
                if suchbegriff.lower() in zeile.lower() and zeile.strip().startswith("- [x]"):
                    if not rueckgaengig:
                        send(f"ℹ️ Diese Karte ist bereits abgehakt!")
                    return
            send(f"❌ Karte nicht gefunden: {suchbegriff}")
            return

        # Fortschritt zählen
        vorhanden = zaehle_vorhanden(neuer_inhalt, set_name)
        gesamt    = SET_GESAMT.get(set_name, 0)
        prozent   = round(vorhanden / gesamt * 100) if gesamt > 0 else 0

        # Lokal speichern
        with open(POKEMON_MD_PFAD, "w", encoding="utf-8") as f:
            f.write(neuer_inhalt)
        # Sync nach Windows Vault
        ssh_upload(POKEMON_MD_PFAD, POKEMON_WINDOWS_PFAD)

        # Todo #11 updaten
        try:
            # Gesamtfortschritt berechnen
            basis_vor  = zaehle_vorhanden(neuer_inhalt, "basis")
            fossil_vor = zaehle_vorhanden(neuer_inhalt, "fossil")
            djung_vor  = zaehle_vorhanden(neuer_inhalt, "dschungel")
            gesamt_vor = basis_vor + fossil_vor + djung_vor
            gesamt_all = 102 + 62 + 64
            todo_proz  = round(gesamt_vor / gesamt_all * 100)

            with open(TODOS_PFAD, "r", encoding="utf-8") as f:
                data = json.load(f)
            for todo in data["todos"]:
                if todo["id"] == 11:
                    todo["prozent"] = todo_proz
                    todo["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                    break
            with open(TODOS_PFAD, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

        set_label = {"basis": "Basis-Set", "fossil": "Fossil", "dschungel": "Dschungel"}
        aktion = "wieder entfernt ❌" if rueckgaengig else "abgehakt ✅"
        emoji  = "❌" if rueckgaengig else "✅"
        send(
            f"{emoji} <b>Karte {aktion}!</b>\n\n"
            f"🃏 {kartenname}\n"
            f"📦 {set_label.get(set_name, set_name)}: {vorhanden}/{gesamt} ({prozent}%)\n"
            f"📊 Gesamt: {gesamt_vor}/228\n"
            f"💾 Pokemon_Sammlung.md aktualisiert"
        )

    except Exception as e:
        send(f"❌ Fehler: {e}")

def pokemon_status(text: str):
    """Zeigt Sammlungsfortschritt."""
    try:
        with open(POKEMON_MD_PFAD, "r", encoding="utf-8") as f:
            md_inhalt = f.read()

        basis_vor  = zaehle_vorhanden(md_inhalt, "basis")
        fossil_vor = zaehle_vorhanden(md_inhalt, "fossil")
        djung_vor  = zaehle_vorhanden(md_inhalt, "dschungel")
        gesamt_vor = basis_vor + fossil_vor + djung_vor

        send(
            f"🃏 <b>Pokémon Sammlung — 1. Edition</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔴 Basis-Set:   {basis_vor}/102 ({round(basis_vor/102*100)}%)\n"
            f"🦴 Fossil:      {fossil_vor}/62 ({round(fossil_vor/62*100)}%)\n"
            f"🌴 Dschungel:   {djung_vor}/64 ({round(djung_vor/64*100)}%)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Gesamt: {gesamt_vor}/228 ({round(gesamt_vor/228*100)}%)\n"
            f"🎯 Noch {228 - gesamt_vor} Karten übrig"
        )
    except Exception as e:
        send(f"❌ Fehler: {e}")

# ══════════════════════════════════════════
#  AUSFÜHRUNG
# ══════════════════════════════════════════
def fuehre_direkt_aus(kategorie: str, text: str):
    """Führt einfache Befehle direkt aus."""
    if kategorie == "status":
        service_lines = []
        for svc in SERVICES:
            out, _, _ = ssh_befehl(f"systemctl is-active {svc}")
            emoji = "🟢" if out == "active" else "🔴"
            service_lines.append(f"{emoji} {svc}: {out}")
        cpu, _, _  = ssh_befehl("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
        ram, _, _  = ssh_befehl("free -m | awk 'NR==2{printf \"%.0f%%\", $3*100/$2}'")
        disk, _, _ = ssh_befehl("df -h / | awk 'NR==2{print $5}'")
        pc = "🟢 Online" if pc_online() else "🔴 Offline"
        send(
            "📊 <b>JensHQ Status</b>\n"
            "────────────────────\n"
            + "\n".join(f"   {s}" for s in service_lines) + "\n"
            "────────────────────\n"
            f"💻 CPU: {cpu}% | RAM: {ram} | Disk: {disk}\n"
            f"🖥️ PC: {pc}"
        )

    elif kategorie == "logs":
        # Service aus Text extrahieren
        svc = next((s for s in SERVICES if s in text.lower()), SERVICES[0])
        out, _, _ = ssh_befehl(f"journalctl -u {svc} -n 15 --no-pager")
        if len(out) > 3000:
            out = "..." + out[-3000:]
        send(f"📋 <b>Logs: {svc}</b>\n<code>{out}</code>")

    elif kategorie == "restart":
        svc = next((s for s in SERVICES if s in text.lower()), None)
        if svc:
            ssh_befehl(f"sudo systemctl restart {svc}")
            time.sleep(2)
            status, _, _ = ssh_befehl(f"systemctl is-active {svc}")
            send(f"🔄 {svc} neugestartet: {status}")
        else:
            send("❌ Welchen Service neustarten? " + ", ".join(SERVICES))

    elif kategorie == "todo":
        import re
        try:
            with open(TODOS_PFAD, "r", encoding="utf-8") as f:
                data = json.load(f)

            t_lower = text.lower()

            # 1. add pruefen
            if "add" in t_lower:
                name = re.sub(r'(?:todo\s+)?add\s+', '', text, flags=re.IGNORECASE).strip()
                if name:
                    max_id = max(t["id"] for t in data["todos"]) if data["todos"] else 0
                    data["todos"].append({
                        "id": max_id + 1, "name": name, "prio": "\U0001f7e1",
                        "prozent": 0, "details": "",
                        "last_updated": datetime.now().strftime("%Y-%m-%d"), "aktiv": True
                    })
                    with open(TODOS_PFAD, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    send(f"\u2795 <b>Todo hinzugefuegt</b>\n\n\U0001f4cb {name}\n\U0001f194 ID: {max_id + 1}")
                else:
                    send("\u274c Nutzung: todo add [name]")
                return

            # 2. list pruefen
            if "list" in t_lower or "liste" in t_lower:
                offen = [t for t in data["todos"] if t["prozent"] < 100]
                msg = "\U0001f4cb <b>Offene Todos:</b>\n\n"
                for t in offen:
                    msg += f"{t['prio']} <b>#{t['id']}</b> {t['name']} \u2014 {t['prozent']}%\n"
                send(msg)
                return

            # 3. Update pruefen
            update_match = re.search(r'(?:todo\s+)?(\d+)\s+(\d+)', t_lower)
            if update_match:
                todo_id = int(update_match.group(1))
                prozent = int(update_match.group(2))
                if 0 <= prozent <= 100:
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
                                todo["prio"] = "\u2705"
                            gefunden = True
                            name = todo["name"]
                            break
                    if gefunden:
                        with open(TODOS_PFAD, "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        emoji = "\u2705" if prozent >= 100 else "\U0001f4dd"
                        send(f"{emoji} <b>Todo aktualisiert</b>\n\n\U0001f4cb {name}\n\U0001f4ca {alter_wert}% \u2192 {prozent}%")
                    else:
                        send(f"\u274c Todo #{todo_id} nicht gefunden")
                    return

            # 4. Fallback: Liste
            offen = [t for t in data["todos"] if t["prozent"] < 100]
            msg = "\U0001f4cb <b>Offene Todos:</b>\n\n"
            for t in offen:
                msg += f"{t['prio']} <b>#{t['id']}</b> {t['name']} \u2014 {t['prozent']}%\n"
            send(msg)
        except Exception as e:
            send(f"\u274c Fehler: {e}")

    elif kategorie == "fokus":
        try:
            with open(FOKUS_PFAD, "r", encoding="utf-8") as f:
                data = json.load(f)
            fokus_text = text
            data["fokus"].append(fokus_text)
            data["fokus"] = data["fokus"][-3:]
            with open(FOKUS_PFAD, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            send("🎯 <b>Fokus aktualisiert</b>\n\n" + "\n".join(f"» {p}" for p in data["fokus"]))
        except Exception as e:
            send(f"❌ Fehler: {e}")

    elif kategorie == "pokemon":
        t = text.lower()
        if any(kw in t for kw in ["wie weit", "status", "fortschritt", "übersicht"]):
            pokemon_status(text)
        else:
            pokemon_karte_eintragen(text)


def fuehre_ollama_aus(text: str):
    """Ollama analysiert und führt aus."""
    send("🧠 <i>Analysiere mit Ollama...</i>")

    # Datei aus Text extrahieren
    datei = None
    for wort in text.split():
        if wort.endswith(".py") or wort.endswith(".json"):
            datei = wort
            break

    if datei:
        pfad = f"{BASE}/{datei}"
        code_out, _, code_err = ssh_befehl(f"cat {pfad}")
        if code_out:
            code_inhalt = code_out[:5000]
            prompt = (
                f"Analysiere diesen Python-Code aus '{datei}'.\n"
                f"Aufgabe des Nutzers: {text}\n\n"
                f"Beantworte konkret auf Deutsch:\n"
                f"1. Was macht der Code?\n"
                f"2. Gibt es Probleme?\n"
                f"3. Was sollte geändert werden?\n\n"
                f"CODE:\n```python\n{code_inhalt}\n```"
            )
            antwort = ollama(prompt)

            # In Obsidian speichern
            datum = datetime.now().strftime("%Y-%m-%d_%H%M")
            obs_write(
                f"KI-Vorschlaege/Analyse_{datei}_{datum}.md",
                f"# Analyse: {datei}\n\nAufgabe: {text}\n\n{antwort}\n"
            )

            if len(antwort) > 3500:
                antwort = antwort[:3500] + "\n<i>... (vollständig in Obsidian)</i>"

            send(
                f"🧠 <b>Ollama Analyse: {datei}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{antwort}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Erledigt — Analyse in Obsidian gespeichert\n"
                f"📁 KI-Vorschlaege/Analyse_{datei}_{datum}.md"
            )
        else:
            send(f"❌ Datei nicht gefunden: {pfad}")
    else:
        # Allgemeine Ollama-Analyse
        antwort = ollama(text)
        if len(antwort) > 3500:
            antwort = antwort[:3500] + "..."
        send(f"🧠 <b>Ollama:</b>\n\n{antwort}")


def fuehre_claude_aus(text: str):
    """Claude API für komplexe Aufgaben mit Vault-Kontext."""
    send("✨ <i>Frage Claude API mit Vault-Kontext...</i>")

    kontext = obs_lese_kontext()

    system = (
        "Du bist James, ein autonomer KI-Assistent für Jens. "
        "Du hast Zugriff auf seinen Obsidian Vault mit seinen Notizen, Todos und Projekten. "
        "Antworte immer auf Deutsch, konkret und handlungsorientiert. "
        "Wenn du Dateien oder Notizen erstellst, sage explizit wo sie gespeichert werden."
    )

    prompt = (
        f"Aufgabe von Jens: {text}\n\n"
        f"Aktueller Vault-Kontext:\n{kontext}\n\n"
        f"Führe die Aufgabe aus oder erstelle einen konkreten Plan. "
        f"Wenn eine neue Notiz erstellt werden soll, gib den vollständigen Inhalt an."
    )

    antwort = claude_api(prompt, system)

    # Prüfen ob Claude eine Notiz erstellen soll
    if "```markdown" in antwort.lower() or "# " in antwort[:100]:
        datum = datetime.now().strftime("%Y-%m-%d_%H%M")
        obs_pfad = f"KI-Vorschlaege/James_Claude_{datum}.md"
        obs_write(obs_pfad, f"# James via Claude\n\nAufgabe: {text}\n\n{antwort}\n")
        backup_info = f"\n📁 Gespeichert: {obs_pfad}"
    else:
        backup_info = ""

    if len(antwort) > 3500:
        antwort = antwort[:3500] + "\n<i>... (vollständig in Obsidian)</i>"

    send(
        f"✨ <b>Claude Antwort:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{antwort}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Erledigt{backup_info}"
    )


def fuehre_ollama_entscheiden(text: str):
    """Ollama entscheidet was zu tun ist."""
    send("🤔 <i>Analysiere Absicht...</i>")

    prompt = (
        f"Jens schreibt: '{text}'\n\n"
        f"Du bist sein Assistent James. Beantworte NUR mit einem dieser Wörter:\n"
        f"DIREKT - wenn es eine einfache Aktion ist (Status, Todo, Neustart)\n"
        f"OLLAMA - wenn Code-Analyse oder technische Aufgabe\n"
        f"CLAUDE - wenn Planung, Lernplan, Erklärung oder Vault-Aufgabe\n"
        f"CHAT - wenn es eine normale Frage/Konversation ist\n\n"
        f"Antworte NUR mit dem einen Wort."
    )

    entscheidung = ollama(prompt).strip().upper()

    if "DIREKT" in entscheidung:
        fuehre_direkt_aus("status", text)
    elif "OLLAMA" in entscheidung:
        fuehre_ollama_aus(text)
    elif "CLAUDE" in entscheidung:
        fuehre_claude_aus(text)
    else:
        # Fallback: normale Antwort von Ollama
        antwort = ollama(text)
        if len(antwort) > 3000:
            antwort = antwort[:3000] + "..."
        send(f"🤖 <b>James:</b>\n\n{antwort}")


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


# ══════════════════════════════════════════
#  HAUPT-DISPATCHER
# ══════════════════════════════════════════
def verarbeite_nachricht(text: str):
    """Hauptfunktion — empfängt Text und dispatcht."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] Nachricht: '{text}'")

    # Legacy Befehle weiterhin unterstützen
    parts = text.strip().split()
    cmd   = parts[0].lower() if parts else ""

    if cmd in ["/hilfe", "/help", "/start"]:
        send(
            "🤖 <b>James Orchestrator</b>\n\n"
            "Schreib mir einfach was du brauchst!\n\n"
            "<b>Beispiele:</b>\n"
            "• 'Wie läuft der LernBot?'\n"
            "• 'Analysiere lernbot_service.py'\n"
            "• 'Ich möchte AZ-900 lernen'\n"
            "• 'Erstelle einen Lernplan für nächste Woche'\n"
            "• 'Was sind meine offenen Todos?'\n\n"
            "<i>Ich entscheide selbst ob ich das direkt, "
            "mit Ollama oder Claude erledige.</i>\n\n"
            f"<i>Services: {', '.join(SERVICES)}</i>"
        )
        return

    # Absicht erkennen und ausführen
    absicht = erkenne_absicht(text)
    print(f"[{ts}] Absicht: {absicht}")

    if absicht.startswith("direkt:"):
        kategorie = absicht.split(":")[1]
        fuehre_direkt_aus(kategorie, text)
    elif absicht == "ollama":
        fuehre_ollama_aus(text)
    elif absicht == "claude":
        fuehre_claude_aus(text)
    else:
        fuehre_ollama_entscheiden(text)


# ══════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════
def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] James Orchestrator gestartet.")
    pc = "🟢 Online" if pc_online() else "🔴 Offline"
    send(
        f"🤖 <b>James Orchestrator ist online!</b>\n\n"
        f"🖥️ Windows PC: {pc}\n"
        f"🧠 Ollama: gemma3:4b\n"
        f"✨ Claude API: aktiv\n\n"
        f"Schreib mir einfach was du brauchst!"
    )

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
                if text:
                    verarbeite_nachricht(text)

            time.sleep(POLL_SEC)

        except KeyboardInterrupt:
            print("\nJames gestoppt.")
            break
        except Exception as e:
            print(f"[FEHLER] {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
