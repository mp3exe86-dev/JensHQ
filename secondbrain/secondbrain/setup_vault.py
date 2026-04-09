# -*- coding: utf-8 -*-
"""
setup_vault.py
Befuellt den Obsidian-Vault mit Jens' aktuellen Projekten und Wissen
Einmalig ausfuehren: python setup_vault.py
"""

import requests
import urllib3
urllib3.disable_warnings()

OBSIDIAN_URL = "https://localhost:27124"
OBSIDIAN_KEY = "26b5285e80b76a9b8f309cea78853022399bf50ef468bbd6c9b75ac9a860f795"

def write(path: str, content: str):
    r = requests.put(
        f"{OBSIDIAN_URL}/vault/{path}",
        headers={
            "Authorization": f"Bearer {OBSIDIAN_KEY}",
            "Content-Type": "text/markdown",
        },
        data=content.encode("utf-8"),
        verify=False, timeout=10
    )
    ok = r.status_code in [200, 201, 204]
    print(f"  {'OK' if ok else 'FEHLER'} – {path}")
    return ok


NOTIZEN = {

"Projekte/PokedexBot.md": """# PokedexBot v2

## Status
🟢 Aktiv – läuft als systemd Service auf RasPi

## Beschreibung
Telegram Bot der vollständige Pokédex-Informationen liefert.
Läuft auf RasPi 192.168.178.47 unter /home/jens/JobAgent/

## Features
- Vollprofil mit Bild, Stats, Typ-Matchup
- /shiny – Shiny-Hunting Guide
- /meta – Competitive Tier + Natur (Smogon)
- /formen – Alola/Galar/Hisui Formen
- /odds – Shiny-Wahrscheinlichkeitsrechner
- /vergleich – zwei Pokémon vergleichen
- /team – Team-Analyse
- /romhack – ROM-Hack Verfügbarkeit
- Deutsche Moves und Abilities
- Cardmarket Preise via TCG API
- Fundort-Datenbank für Gen 9

## Offene Aufgaben
- [ ] ROM-Hack Datenbank vervollständigen (aktuell ~130 Pokémon, Ziel: 500+)

## Technisches
- Token: 8751582892:AAFJz2yaMjUCA5NnmyD25JQdf5Gymsmie54
- Service: pokedexbot
- Datei: /home/jens/JobAgent/pokedex_bot.py
""",

"Projekte/James_Ollama_Agent.md": """# James – Ollama Agent

## Status
🔴 Geplant – noch nicht gebaut

## Beschreibung
Autonomer KI-Agent der auf dem Windows PC läuft (RTX 3070, 32GB RAM).
Soll selbstständig Aufgaben ausführen, Code deployen und Fehler beheben.

## Ziel
- Telegram Bot als Interface
- Liest Aufgaben aus Obsidian
- Führt sie per SSH auf dem RasPi aus
- Testet Ergebnisse via Telegram API
- Liest journalctl Logs und korrigiert Fehler selbst
- Schreibt Ergebnisse zurück nach Obsidian

## Technisches
- Ollama 0.19.0 installiert auf Windows
- Modell: llama3.2 (2GB)
- nomic-embed-text für Embeddings
- Obsidian REST API für Wissensbasis

## Nächste Schritte
- [ ] SSH-Verbindung von Windows zu RasPi via Python (paramiko)
- [ ] Telegram Bot Interface bauen
- [ ] Erste Aufgabe: Log lesen und Fehler melden
- [ ] Selbst-Korrektur Schleife bauen

## Vision
James schreibt später auch Band 2 des Pokémon Buchs als Erstentwurf.
""",

"Projekte/ROM_Hack_Selbstbau.md": """# Pokémon ROM-Hack Selbstbau

## Status
⏸️ Pausiert

## Beschreibung
Eigener Pokémon FireRed ROM-Hack mit der Caelmor-Region.
Irisch inspirierte neue Region mit eigener Story und Lore.

## Tools
- XSE (Scripting Engine)
- AdvanceMap (Map Editor)
- HexManiac (Hex Editor)

## Aktueller Stand
- Route 3 / Vertania Forest in Bearbeitung
- Aeralith-Lore entwickelt
- Fix für greyed-out "Events ändern": Sichtweite togglen vor dem Speichern

## Nächste Schritte (wenn fortgesetzt)
- [ ] Route 3 Events fertigstellen
- [ ] Erste Stadt vollständig
- [ ] Starter-Auswahl scripten
""",

"Projekte/Pokemon_Buch.md": """# Pokémon Chroniken Band 2 – Was die Zeit bewahrt

## Status
⏸️ Pausiert – Kapitel 1 fertig

## Beschreibung
Pokémon Fan-Roman, Caelmor Region (irisch inspiriert).

## Charaktere
- **Vael** (19) – Protagonist
- **Seira** – Begleiterin
- **Daran** – Antagonist

## Stand
- 18-Kapitel Plan vollständig
- Kapitel 1 geschrieben (~16 Seiten)
- Letzter Satz festgelegt

## Idee für Zukunft
James (Ollama) schreibt Erstentwürfe der weiteren Kapitel
basierend auf dem Kapitel-Plan. Jens überarbeitet.
""",

"Projekte/SecondBrain_System.md": """# AI SecondBrain System

## Status
🟡 In Aufbau

## Beschreibung
Hybrides KI-System: Obsidian (Wissensbasis) + Ollama (lokal) + Claude (Cloud)

## Architektur
- **Obsidian**: Alle Notizen, Projekte, Wissen
- **Ollama (lokal)**: Schnelle lokale Verarbeitung, James Agent
- **Claude**: Komplexes Denken, Planung, Analyse
- **Python Bridge**: obsidian_ollama.py verbindet alles

## Installiert
- Obsidian Windows App ✅
- Ollama 0.19.0 Windows ✅
- llama3.2 (2GB) ✅
- nomic-embed-text (274MB) ✅
- Obsidian Plugins: Dataview, Templater, Local REST API ✅
- obsidian_ollama.py ✅

## Nächste Schritte
- [ ] Vault mit Inhalten befüllen (läuft gerade)
- [ ] James Agent bauen
- [ ] Automatische tägliche Analyse einrichten
- [ ] Claude Zugriff auf Obsidian via MCP einrichten
""",

"Wissen/Azure_AZ900.md": """# Azure & AZ-900 Vorbereitung

## Ziel
AZ-900 Zertifizierung bestehen + Cloud-Helden DQR-5 Prüfung

## Lernfortschritt (LernBot)
- LernBot läuft auf RasPi mit 52 AZ-900 Fragen
- /frage im Telegram für Quiz
- /status für Fortschritt

## Themen AZ-900
- Cloud-Konzepte (IaaS, PaaS, SaaS)
- Azure Architektur & Dienste
- Azure Pricing & SLA
- Identity & Security (Entra ID)
- Governance & Compliance

## Cloud-Helden DQR-5 Kurs
Themen: Kubernetes, CI/CD, Terraform, IaC, Docker, Git, Netzwerk
Kurslinks: Notion, Slack, Terraform Registry, GitHub

## LernBot Lektionen (neu)
21 Lektionen zu: Docker, Kubernetes, CI/CD, Terraform, Git, Netzwerk, Linux, Cloud
Automatisch alle 6h via Telegram (/lektion Befehl)
""",

"Wissen/JensHQ_System.md": """# JensHQ – Technische Übersicht

## RasPi
- IP: 192.168.178.47
- User: jens
- Ordner: /home/jens/JobAgent/

## Systemd Services (24/7)
| Service | Funktion |
|---------|---------|
| lernbot | AZ-900 Quiz + Lektionen |
| jobbot | Job-Suche on-demand |
| dealbot | Deal-Finder |
| pokedexbot | Pokédex Bot |

## Telegram Bots
- JensJobBot: 8714514322
- JensLernBot: 8765638573
- JensDealBot: 8667023203
- JensPokedexBot: 8751582892
- Chat-ID: 8656887627

## Windows PC
- RTX 3070 (8GB VRAM)
- 32GB RAM
- Python 3.14
- Ollama 0.19.0
- Obsidian (Vault: C:/JobAgent/vault/SecondBrain)

## Workflow
1. Code auf Windows schreiben (C:/JobAgent/)
2. Per scp auf RasPi hochladen
3. sudo systemctl restart [service]
""",

"Wissen/Zertifizierungen.md": """# Zertifizierungen & Karriere

## Aktuell
- Fachinformatiker Systemintegration (IHK 2020)
- AdA-Schein (2023)
- Neuer Job: MOTECS ab 01.04.2026

## Geplante Zertifizierungen
- [ ] AZ-900 (Azure Fundamentals)
- [ ] ITIL 4 Foundation
- [ ] MD-102 (Endpoint Administrator)
- [ ] SC-900
- [ ] AZ-104 (später)
- [ ] Cloud-Helden DQR-5 Kurs

## Expertise
- Microsoft Intune ⭐⭐⭐⭐
- Active Directory ⭐⭐⭐⭐
- Microsoft 365 ⭐⭐⭐⭐
- Freshdesk ⭐⭐⭐
- Meraki ⭐⭐⭐
- CheckMK ⭐⭐⭐
- Azure (in Ausbildung) ⭐⭐
""",

"Tasks/Offene_Aufgaben.md": """# Offene Aufgaben

## PokedexBot
- [ ] ROM-Hack Datenbank vervollständigen

## James Agent
- [ ] SSH-Verbindung (paramiko) aufbauen
- [ ] Telegram Interface bauen
- [ ] Erste Aufgabe automatisieren

## SecondBrain
- [ ] Tägliche automatische Analyse einrichten
- [ ] Claude MCP Zugriff auf Obsidian

## Lernen
- [ ] AZ-900 Prüfung anmelden
- [ ] Cloud-Helden Kurs abschließen
- [ ] ITIL 4 Foundation buchen

## Pokémon
- [ ] Glurak Base Set 4/102 kaufen (Zielpreis unter 75€)
""",

"Ideen/Ideen_Sammlung.md": """# Ideen Sammlung

## KI & Automatisierung
- James schreibt Band 2 des Pokémon Buchs (Erstentwürfe)
- Automatische Jobsuche mit KI-Bewerbungsschreiben
- Pokémon Karten Preisalert (Telegram)
- Voice-Input für Obsidian Notizen

## Projekte
- Pokémon ROM-Hack fertigstellen (Caelmor Region)
- JensHQ Dashboard (alle Bots auf einer Webseite)
- Kleinanzeigen TrendFinder reaktivieren (Playwright Fix)

## Lernen
- Kubernetes Cluster auf RasPi aufsetzen
- Eigene CI/CD Pipeline für JensHQ bauen
- Terraform für RasPi-Konfiguration nutzen
""",

}

if __name__ == "__main__":
    print("Befuelle Obsidian-Vault...")
    ok = 0
    for pfad, inhalt in NOTIZEN.items():
        if write(pfad, inhalt):
            ok += 1
    print(f"\nFertig! {ok}/{len(NOTIZEN)} Dateien erstellt.")