# 🤖 JensHQ — Personal AI Automation Ecosystem

> Built by a sysadmin who got tired of doing things manually.

[![GitHub](https://img.shields.io/badge/GitHub-mp3exe86--dev-blue)](https://github.com/mp3exe86-dev/JensHQ)

JensHQ is a fully self-hosted AI automation system running on a Raspberry Pi + Windows PC. It uses Telegram as the interface, Ollama for local AI, Obsidian as the knowledge base, and Claude as the orchestrator.

---

## 🏗️ Architecture

```
You (Telegram)
      │
      ▼
James Orchestrator (RasPi 24/7)
      │
      ├── Simple tasks → James handles directly
      ├── Code/Analysis → Ollama (gemma3:4b, local)
      └── Complex/Vault → Claude API
            │
            ▼
      Obsidian Vault (Windows, via MCP)
```

**Infrastructure:**
- **Raspberry Pi** — 24/7 server, runs all systemd services
- **Windows PC** — Ollama, Obsidian, Claude Desktop
- **Telegram** — single interface for everything

---

## 🤖 Bots & Services

| Service | Description | Runs on |
|---------|-------------|---------|
| **James Orchestrator** | Autonomous AI agent — decides what to do and how | RasPi |
| **LernBot** | AZ-900 + DevOps quiz with adaptive learning | RasPi |
| **JobBot** | Daily job search via BA-API, RSS, Interamt | RasPi |
| **DealBot** | Pokémon TCG + console deals scanner | RasPi |
| **PokedexBot** | Full Pokédex with ROM-hack database | RasPi |
| **FokusBot** | Weekly digest — todos, contracts, IT trends | RasPi |

---

## ✨ Features

- **James** understands natural language and decides autonomously:
  - `todo list` → show todos
  - `todo add [name]` → add todo
  - `todo 1 50` → update progress
  - `Analysiere lernbot.py` → Ollama code review
  - `Ich möchte AZ-900 lernen` → learning plan
  - `Ich habe Basis 4/102` → Pokémon collection tracker
  - `Ich habe Basis 4/102 doch nicht` → undo
- **LernBot** — 52 AZ-900 questions + Git, Docker, K8s, Terraform lessons
- **DealBot** — monitors Quoka.de + Cardmarket for deals below market price
- **Obsidian MCP** — Claude Desktop reads/writes vault directly
- **Pokémon Collection Tracker** — track 1st edition cards via Telegram

---

## 🚀 Quick Start

```bash
git clone https://github.com/mp3exe86-dev/JensHQ
cd JensHQ
cp .env.example .env
# Fill in your tokens and settings
pip install -r requirements.txt --break-system-packages
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in:

```env
JAMES_TOKEN=your_token_here
LERNBOT_TOKEN=your_token_here
JOBBOT_TOKEN=your_token_here
DEALBOT_TOKEN=your_token_here
POKEDEXBOT_TOKEN=your_token_here
FOKUSBOT_TOKEN=your_token_here
CHAT_ID=your_chat_id
OLLAMA_URL=http://your_pc_ip:11434
CLAUDE_API_KEY=sk-ant-...
OBSIDIAN_KEY=your_key_here
RASPI_HOST=192.168.x.x
RASPI_USER=your_user
RASPI_PASS=your_password
BASE_PATH=/home/user/JensHQ
```

---

## 📁 Project Structure

```
JensHQ/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── james/               ← James Orchestrator
├── lernbot/             ← LernBot + Lektionen
├── dealfinder/          ← DealBot
├── jobagent/            ← JobBot + agents/
├── pokedex/             ← PokedexBot
├── secondbrain/         ← Obsidian Graph + Session Log
└── shared/              ← Telegram Notifier, FokusBot, daten/
```

---

## 🗺️ Roadmap

- [x] Multi-bot Telegram system
- [x] James autonomous orchestrator (Ollama + Claude)
- [x] Pokémon collection tracker
- [x] Obsidian MCP integration (Claude Desktop)
- [x] Environment variables (no hardcodes)
- [x] GitHub v1.0
- [ ] Docker Compose for all services (v2.0)
- [ ] GitHub Actions CI/CD
- [ ] **Paperclip integration** — James as CEO of an AI company (v3.0)
- [ ] K3s deployment on RasPi

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Interface | Telegram Bot API |
| Local AI | Ollama (gemma3:4b) |
| Cloud AI | Claude API (Anthropic) |
| Knowledge Base | Obsidian + Local REST API |
| Server | Raspberry Pi (systemd) |
| Dev Machine | Windows 11 + Python |
| Orchestration (planned) | Paperclip |
| Containers (planned) | Docker + K3s |

---

## 👤 Author

Built by Jens — Fachinformatiker Systemintegration, Field IT / Modern Workplace Specialist.
Currently pursuing AZ-900 and building toward AI Solutions Engineering.

> "I built this because I wanted to automate my life. Now it automates itself."

---

## 📄 License

MIT — do whatever you want with it.
