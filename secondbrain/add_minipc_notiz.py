# -*- coding: utf-8 -*-
"""
add_minipc_notiz.py – einmalig ausfuehren
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
    print(f"  {'OK' if ok else 'FEHLER'} - {path}")

write("Ideen/MiniPC_Hardware_Plan.md", """# Mini PC Hardware Plan

## Ziel
Zwei autarke Mini-PCs die miteinander kommunizieren:
- PC 1 (Windows) – James Agent, Obsidian, Ollama
- PC 2 (Linux) – alle Telegram Bots, systemd Services

## Aktueller Stand
- Gaming PC (RTX 3070, 32GB RAM) = James/Ollama/Obsidian (temporaer)
- RasPi (192.168.178.47) = Linux Server, alle Bots

## Empfehlungen

### Budget Linux-Server (~150-170 EUR)
**Beelink EQ12** – Intel N100
- 6W TDP, sehr leise, ideal fuer 24/7
- Ersetzt oder ergaenzt RasPi
- Amazon ~150-170 EUR

### Windows Mini-PC fuer James/Ollama (~280 EUR)
**Beelink SER5 Pro** – AMD Ryzen 5 5560U
- 16GB RAM (Pflicht fuer llama3.1:8b!)
- Leise, kompakt, Windows 11 Pro
- ~280 EUR

## Wichtige Anforderungen
- Windows PC: mindestens 16GB RAM (wegen Ollama/LLM)
- N100 reicht NICHT fuer LLM-Inferenz
- Linux-Server: N100 reicht perfekt fuer Telegram Bots

## Naechste Schritte
- [ ] Beelink SER5 Pro kaufen (~280 EUR)
- [ ] James Agent auf Mini-PC umziehen
- [ ] RasPi bleibt als Linux-Server
""")

print("Fertig!")