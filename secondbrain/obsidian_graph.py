# -*- coding: utf-8 -*-
"""
obsidian_graph.py
JensHQ — Obsidian Graph Verknüpfungen
Fügt automatisch [[Links]] in Vault-Dateien ein.
Aufruf: python obsidian_graph.py
"""

import os
import re
from datetime import datetime

VAULT = r"C:\JobAgent\vault\SecondBrain"

# ══════════════════════════════════════════
#  VERKNÜPFUNGSREGELN
#  Format: { "Dateiname_ohne_.md": ["Link1", "Link2", ...] }
# ══════════════════════════════════════════
VERKNUEPFUNGEN = {
    # Wissen
    "Azure_AZ900": [
        "Zertifizierungen", "CloudHelden_Kurs", "JensHQ_System"
    ],
    "Zertifizierungen": [
        "Azure_AZ900", "CloudHelden_Kurs", "JensHQ_System"
    ],
    "CloudHelden_Kurs": [
        "Zertifizierungen", "Azure_AZ900"
    ],
    "JensHQ_Dateien": [
        "JensHQ_System", "James_Ollama_Agent", "Offene_Aufgaben"
    ],
    "JensHQ_System": [
        "James_Ollama_Agent", "PokedexBot", "Offene_Aufgaben", "Zertifizierungen"
    ],
    "AI_SecondBrain_Konzept": [
        "JensHQ_System", "James_Ollama_Agent"
    ],

    # Projekte
    "James_Ollama_Agent": [
        "JensHQ_System", "Offene_Aufgaben", "AI_SecondBrain_Konzept"
    ],
    "PokedexBot": [
        "JensHQ_System", "ROM_Hack_Selbstbau", "Pokemon_Buch", "Offene_Aufgaben"
    ],
    "ROM_Hack_Selbstbau": [
        "Pokemon_Buch", "PokedexBot"
    ],
    "Pokemon_Buch": [
        "ROM_Hack_Selbstbau", "PokedexBot"
    ],
    "SecondBrain_System": [
        "JensHQ_System", "AI_SecondBrain_Konzept", "Offene_Aufgaben"
    ],

    # Ideen
    "Ideen_Sammlung": [
        "JensHQ_System", "Offene_Aufgaben"
    ],
    "MiniPC_Hardware_Plan": [
        "JensHQ_System", "Ideen_Sammlung"
    ],

    # Tasks
    "Offene_Aufgaben": [
        "JensHQ_System", "Zertifizierungen", "James_Ollama_Agent"
    ],

    # Root
    "Willkommen": [
        "JensHQ_System", "Zertifizierungen", "Offene_Aufgaben",
        "James_Ollama_Agent", "PokedexBot", "Ideen_Sammlung"
    ],
}

# Session Logs und WeeklyDigests dynamisch verknüpfen
SESSION_LINKS = ["JensHQ_System", "Zertifizierungen", "Offene_Aufgaben"]
WEEKLY_LINKS  = ["Offene_Aufgaben", "Zertifizierungen", "JensHQ_System"]


def lade_datei(pfad: str) -> str:
    with open(pfad, "r", encoding="utf-8") as f:
        return f.read()


def speichere_datei(pfad: str, inhalt: str):
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(inhalt)


def link_existiert(inhalt: str, link: str) -> bool:
    return f"[[{link}]]" in inhalt


def fuege_links_ein(inhalt: str, links: list) -> tuple[str, list]:
    """Fügt Links am Ende der Datei ein wenn noch nicht vorhanden."""
    neu = []
    for link in links:
        if not link_existiert(inhalt, link):
            neu.append(link)

    if not neu:
        return inhalt, []

    # Links-Block am Ende einfügen
    link_block = "\n\n---\n🔗 **Verknüpft mit:** " + " | ".join(f"[[{l}]]" for l in neu)

    # Wenn bereits ein Verknüpfungs-Block vorhanden, erweitern
    if "🔗 **Verknüpft mit:**" in inhalt:
        # Bestehende Links herauslesen und neue hinzufügen
        bestehend = re.search(r"🔗 \*\*Verknüpft mit:\*\* (.+)", inhalt)
        if bestehend:
            alle_links = bestehend.group(1)
            for link in neu:
                alle_links += f" | [[{link}]]"
            inhalt = re.sub(
                r"🔗 \*\*Verknüpft mit:\*\* .+",
                "🔗 **Verknüpft mit:** " + alle_links,
                inhalt
            )
        return inhalt, neu
    else:
        inhalt = inhalt.rstrip() + link_block + "\n"
        return inhalt, neu


def verarbeite_vault():
    print(f"\n{'='*50}")
    print(f"Obsidian Graph — {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(f"{'='*50}\n")

    gesamt_neu = 0

    for root, dirs, files in os.walk(VAULT):
        # .obsidian überspringen
        dirs[:] = [d for d in dirs if d != ".obsidian"]

        for dateiname in files:
            if not dateiname.endswith(".md"):
                continue

            pfad = os.path.join(root, dateiname)
            name = dateiname.replace(".md", "")

            # Links bestimmen
            if name in VERKNUEPFUNGEN:
                links = VERKNUEPFUNGEN[name]
            elif name.startswith("SESSION_LOG"):
                links = SESSION_LINKS
            elif name.startswith("WeeklyDigest"):
                links = WEEKLY_LINKS
            else:
                continue

            # Datei laden und Links einfügen
            try:
                inhalt = lade_datei(pfad)
                neuer_inhalt, neu = fuege_links_ein(inhalt, links)

                if neu:
                    speichere_datei(pfad, neuer_inhalt)
                    print(f"✅ {name}")
                    for l in neu:
                        print(f"   + [[{l}]]")
                    gesamt_neu += len(neu)
                else:
                    print(f"⏭️  {name} — alle Links bereits vorhanden")

            except Exception as e:
                print(f"❌ {name}: {e}")

    print(f"\n{'='*50}")
    print(f"Fertig! {gesamt_neu} neue Verknüpfungen hinzugefügt.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    verarbeite_vault()