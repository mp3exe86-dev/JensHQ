# C:\JobAgent\session_log.py
import json
import os
import subprocess
from datetime import date

VAULT_PATH = r"C:\JobAgent\vault\SecondBrain"
TODOS_FILE = os.path.join(VAULT_PATH, "todos.json")

def generiere_log():
    heute = date.today().strftime("%d.%m.%Y")
    datum_datei = date.today().strftime("%d%m%Y")

    # Todos laden
    with open(TODOS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    erledigt = [t for t in data["todos"] if t["prozent"] >= 100]
    offen    = [t for t in data["todos"] if t["prozent"] < 100]

    log  = f"# SESSION LOG — {heute}\n"
    log += f"\n## ✅ ERLEDIGT\n"
    for t in erledigt:
        log += f"- {t['name']} — {t['prozent']}%\n"

    log += f"\n## 🔧 NOCH OFFEN\n"
    for t in offen:
        log += f"- {t['prio']} {t['name']} — {t['prozent']}%\n"

    log += f"\n## 📝 NOTIZEN\n"
    log += f"*(hier manuell ergänzen)*\n"

    # In Obsidian speichern
    pfad = os.path.join(VAULT_PATH, f"SESSION_LOG_{datum_datei}.md")
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(log)

    print(f"✅ Session Log gespeichert: SESSION_LOG_{datum_datei}.md")

    # Obsidian Graph automatisch aktualisieren
    print("🔗 Aktualisiere Obsidian Graph...")
    subprocess.run(["python", r"C:\JobAgent\secondbrain\obsidian_graph.py"], check=False)

if __name__ == "__main__":
    generiere_log()