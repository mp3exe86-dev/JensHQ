# -*- coding: utf-8 -*-
# patch_lernbot.py – einmalig ausfuehren um lernbot_service.py zu patchen

with open('/home/jens/JobAgent/lernbot_service.py', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Import hinzufuegen
old_import = "from lernbot_quiz import FRAGEN, THEMEN, get_fragen_by_thema, ist_mehrfachauswahl, ist_antwort_korrekt"
new_import = old_import + "\nfrom lernbot_lektion import get_lektion_by_id, get_alle_ids"

if "from lernbot_lektion" not in c:
    c = c.replace(old_import, new_import)
    print("Import OK")
else:
    print("Import bereits vorhanden")

# 2. Lektion-Funktion vor main() einfuegen
if "def lektion_senden" not in c:
    lektion_func = """
# ──────────────────────────────────────────
#  LEKTION SENDEN
# ──────────────────────────────────────────
def lektion_senden(tracker: dict) -> dict:
    alle_ids    = get_alle_ids()
    gesendete   = tracker.get("gesendete_lektionen", [])
    ausstehende = [lid for lid in alle_ids if lid not in gesendete]
    if not ausstehende:
        gesendete   = []
        ausstehende = alle_ids
        tracker["gesendete_lektionen"] = []
    lektion = get_lektion_by_id(ausstehende[0])
    if not lektion:
        return tracker
    nummer = len(gesendete) + 1
    total  = len(alle_ids)
    text = (
        "\\U0001f4da <b>Lektion: " + lektion['titel'] + "</b>\\n"
        "\\U0001f3f7\\ufe0f Thema: " + lektion['thema'] + "\\n"
        "\\u2500" * 20 + "\\n\\n"
        + lektion['inhalt'] + "\\n\\n"
        + "\\u2500" * 20 + "\\n"
        + "<i>Lektion " + str(nummer) + "/" + str(total) + " | /lektion fuer naechste</i>"
    )
    if send(text):
        tracker.setdefault("gesendete_lektionen", []).append(ausstehende[0])
        save_tracker(tracker)
        print("Lektion gesendet: " + ausstehende[0] + " - " + lektion['titel'])
    return tracker

"""
    c = c.replace("def main():", lektion_func + "def main():")
    print("Funktion OK")
else:
    print("Funktion bereits vorhanden")

# 3. /lektion Befehl in main loop
old_cmd = 'if text.lower() in ["/frage", "/quiz", "/next"]:'
new_cmd = 'if text.lower() in ["/lektion", "/learn"]:\n                    tracker = lektion_senden(tracker)\n                elif text.lower() in ["/frage", "/quiz", "/next"]:'

if '/lektion' not in c:
    c = c.replace(old_cmd, new_cmd)
    print("Befehl OK")
else:
    print("Befehl bereits vorhanden")

# 4. sys.argv support
old_main = 'if __name__ == "__main__":\n    main()'
new_main = 'if __name__ == "__main__":\n    import sys\n    if len(sys.argv) > 1 and sys.argv[1] == "--lektion":\n        t = load_tracker()\n        lektion_senden(t)\n    else:\n        main()'

if '--lektion' not in c:
    c = c.replace(old_main, new_main)
    print("argv OK")
else:
    print("argv bereits vorhanden")

with open('/home/jens/JobAgent/lernbot_service.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch abgeschlossen!")