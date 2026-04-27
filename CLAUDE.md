# JensHQ — Claude Session Start

## Wer bin ich?
Du arbeitest mit Jens Kreuz, Fachinformatiker SI aus Knüllwald (Nordhessen).
Jens baut JensHQ — ein selbst gehostetes KI-Automatisierungssystem.

## Beim Start jeder Session — in dieser Reihenfolge:
1. Lies `/home/jens/JobAgent/daten/todos.json` — offene Todos
2. Lies `C:\JobAgent\vault\SecondBrain\Soul.md` — James Charakter
3. Prüfe ob RasPi (192.168.178.47) und PC (192.168.178.80) erreichbar sind
4. Dann warte auf Aufgabe

## Stack
- **RasPi** (192.168.178.47, user: jens) — James Orchestrator, alle Bots, n8n
- **Windows PC** (192.168.178.80) — Ollama (Port 11434), Obsidian, Whisper (Port 5050)
- **Obsidian Vault** — C:\JobAgent\vault\SecondBrain\
- **Basis Pfad RasPi** — /home/jens/JobAgent/
- **Basis Pfad Windows** — C:\JobAgent\

## Wichtige Dateien
| Datei | Pfad |
|-------|------|
| James Orchestrator | /home/jens/JobAgent/james/james_orchestrator.py |
| James News | /home/jens/JobAgent/james/james_news.py |
| Weekly Bot | /home/jens/JobAgent/shared/weekly_news_bot.py |
| AZ-900 Quiz | /home/jens/JobAgent/shared/az900_quiz.py |
| AZ-900 Fragen | /home/jens/JobAgent/daten/az900_fragen.json |
| .env | /home/jens/JobAgent/.env |
| Backup Script | /home/jens/JobAgent/backup.sh |

## Deploy Workflow
1. Datei auf Windows bearbeiten
2. SCP nach RasPi: `scp C:\JobAgent\[ordner]\[datei].py jens@192.168.178.47:/home/jens/JobAgent/[ordner]/`
3. Service neustarten: `sudo systemctl restart james-orchestrator.service`

## Services auf RasPi (systemd)
- james-orchestrator.service
- lernbot.service
- jobbot.service
- dealbot.service
- pokedexbot.service

## Cronjobs RasPi
- 7 Uhr täglich — Morning Digest (daily)
- 8 Uhr täglich — DealBot
- 9,11,13,15,17 Uhr — James News/Gespräche
- 8,10,12,15,18 Uhr — AZ-900 Quiz (Runden 1-5)
- 20 Uhr Sonntag — AZ-900 Wochen-Score
- 12 Uhr Sonntag — Weekly Digest
- 3 Uhr täglich — Backup → Google Drive

## Coding Style
- Kein Markdown in Variablennamen
- Alles über .env, keine Hardcodes
- Keine deutschen Umlaute in Variablennamen
- SCP immer von Windows PowerShell, nie von RasPi Terminal

## Jens seine Ziele
- Cloud/KI Engineering Karriere (AZ-900 → AZ-104 → MD-102)
- JensHQ als YouTube/GitHub Portfolio
- Freelance KI-Automatisierung
- Sympathischer Elon Musk aus Knüllwald 😄
