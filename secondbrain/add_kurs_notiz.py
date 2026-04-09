# -*- coding: utf-8 -*-
"""
add_kurs_notiz.py – einmalig ausfuehren
Fuegt Cloud-Helden Kurs Notiz zum Obsidian-Vault hinzu
"""
import requests, urllib3
urllib3.disable_warnings()

KEY = "26b5285e80b76a9b8f309cea78853022399bf50ef468bbd6c9b75ac9a860f795"
URL = "https://localhost:27124"
HDR = {"Authorization": f"Bearer {KEY}", "Content-Type": "text/markdown"}

def write(path, content):
    r = requests.put(f"{URL}/vault/{path}", headers=HDR,
                     data=content.encode("utf-8"), verify=False, timeout=10)
    ok = r.status_code in [200, 201, 204]
    print(f"  {'OK' if ok else 'FEHLER'} – {path}")

write("Wissen/CloudHelden_Kurs.md", """# Cloud-Helden DQR-5 Kurs

## Ziel
Berufsspezialist Systemintegration & Vernetzung (DQR-5)

## Kurs-Links
- Kursseite: https://cloudhelden.org/pages/berufsspezialist-systemintegration-vernetzung
- Skripte: https://deluxe-utahraptor-24a.notion.site/Skripte-284965089da680a699cfc59797a6f77a
- Slack: https://app.slack.com/client/T0AG3AP5UFR/C0AGCCCANRH
- Terraform Registry: https://registry.terraform.io/namespaces/hashicorp
- GitHub Demo 1: https://github.com/Die-Unfassbaren-IT-Spezis/terraform-aws-provider-demo
- GitHub Demo 2: https://github.com/Die-Unfassbaren-IT-Spezis/terraform-github-provider-demo
- Terraform Uebungen: https://github.com/helsoc7/terraform-simple-exercises/blob/main/README.md
- Tactiq Transkript: https://app.tactiq.io/#/transcripts/RlBZyc4EKjShXoksNHIC
- Tool: Visual Studio Code

## Hauptthemen
- [ ] Docker – Container Grundlagen
- [ ] Kubernetes – Container Orchestrierung
- [ ] CI/CD Pipelines – GitHub Actions
- [ ] Terraform – Infrastructure as Code
- [ ] Git & GitHub – Versionsverwaltung
- [ ] Netzwerk – IP, DNS, TCP/IP
- [ ] Linux – Grundbefehle, systemd
- [ ] Cloud – IaaS/PaaS/SaaS, Azure

## LernBot
21 Lektionen automatisch taeglich 3x via Telegram – /lektion Befehl

## Status
In Bearbeitung
""")

write("Wissen/AI_SecondBrain_Konzept.md", """# AI SecondBrain – Konzept & Architektur

## Vision
Ein hybrides KI-System das mitdenkt, Wissen organisiert und proaktiv Vorschlaege macht.
Kein autonomes Gehirn – ein intelligenter Co-Pilot.

## Architektur
- Obsidian (Windows) = Wissensbasis (Markdown-Notizen)
- Ollama lokal (llama3.1:8b) = schnelle lokale Verarbeitung, James Agent
- Claude (Cloud) = komplexes Denken, Strategie, Analyse
- Python Bridge (obsidian_ollama.py) = verbindet alles

## Installiert
- Obsidian Windows App mit Plugins: Dataview, Templater, Local REST API
- Ollama 0.19.0 mit llama3.1:8b + nomic-embed-text
- obsidian_ollama.py in C:/JobAgent/

## Befehle
- python obsidian_ollama.py --test        = Verbindung testen
- python obsidian_ollama.py --frage "..."  = Frage stellen
- python obsidian_ollama.py --analyse      = Vault analysieren
- python obsidian_ollama.py --vorschlag    = Vorschlaege generieren

## Naechste Schritte
- [ ] Taeglich automatische Analyse (Task Scheduler)
- [ ] James Agent als Telegram Bot bauen
- [ ] Claude MCP Zugriff auf Obsidian einrichten
- [ ] Embeddings mit nomic-embed-text fuer bessere Suche
""")

print("Fertig!")