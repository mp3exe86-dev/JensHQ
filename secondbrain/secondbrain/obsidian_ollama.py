# -*- coding: utf-8 -*-
"""
obsidian_ollama.py
JensHQ – SecondBrain Bridge
Verbindet Obsidian (via Local REST API) mit Ollama (llama3.2)
Liest Notizen, analysiert sie, schreibt KI-Vorschlaege zurueck

Aufruf:
  python obsidian_ollama.py --analyse     # Alle Notizen analysieren
  python obsidian_ollama.py --frage "Was sind meine offenen Projekte?"
  python obsidian_ollama.py --vorschlag   # Naechste Schritte vorschlagen
"""

import requests
import json
import argparse
import urllib3
from datetime import datetime
from pathlib import Path

urllib3.disable_warnings()

# ──────────────────────────────────────────
#  KONFIGURATION
# ──────────────────────────────────────────
OBSIDIAN_URL  = "https://localhost:27124"
OBSIDIAN_KEY  = "26b5285e80b76a9b8f309cea78853022399bf50ef468bbd6c9b75ac9a860f795"
OLLAMA_URL    = "http://localhost:11434"
OLLAMA_MODEL  = "llama3.1:8b"

HEADERS_OBS = {
    "Authorization": f"Bearer {OBSIDIAN_KEY}",
    "Content-Type": "application/json",
}


# ──────────────────────────────────────────
#  OBSIDIAN FUNKTIONEN
# ──────────────────────────────────────────
def obs_get_files() -> list:
    """Gibt alle Dateien im Vault rekursiv zurueck."""
    def list_dir(path=""):
        url = f"{OBSIDIAN_URL}/vault/{path}" if path else f"{OBSIDIAN_URL}/vault/"
        r = requests.get(url, headers=HEADERS_OBS, verify=False, timeout=10)
        items = r.json().get("files", [])
        alle = []
        for item in items:
            full = f"{path}{item}" if path else item
            if item.endswith("/"):
                # Ordner rekursiv durchsuchen
                alle.extend(list_dir(full))
            else:
                alle.append(full)
        return alle
    return list_dir()


def obs_read_file(path: str) -> str:
    """Liest eine Datei aus dem Vault."""
    r = requests.get(f"{OBSIDIAN_URL}/vault/{path}", headers={
        "Authorization": f"Bearer {OBSIDIAN_KEY}",
        "Accept": "text/markdown",
    }, verify=False, timeout=10)
    if r.status_code == 200:
        return r.text
    return ""


def obs_write_file(path: str, content: str) -> bool:
    """Schreibt eine Datei in den Vault."""
    r = requests.put(
        f"{OBSIDIAN_URL}/vault/{path}",
        headers={
            "Authorization": f"Bearer {OBSIDIAN_KEY}",
            "Content-Type": "text/markdown",
        },
        data=content.encode("utf-8"),
        verify=False,
        timeout=10
    )
    return r.status_code in [200, 201, 204]


def obs_get_all_content() -> str:
    """Liest alle Markdown-Dateien und gibt sie als einen Text zurueck."""
    files = obs_get_files()
    md_files = [f for f in files if f.endswith(".md")]
    alle_texte = []
    for f in md_files:
        inhalt = obs_read_file(f)
        if inhalt.strip():
            alle_texte.append(f"=== {f} ===\n{inhalt}\n")
    return "\n".join(alle_texte)


# ──────────────────────────────────────────
#  OLLAMA FUNKTIONEN
# ──────────────────────────────────────────
def ollama_frage(prompt: str, kontext: str = "") -> str:
    """Schickt eine Frage an Ollama und gibt die Antwort zurueck."""
    system = (
        "Du bist Jens' persoenlicher KI-Assistent fuer sein SecondBrain in Obsidian. "
        "Du analysierst seine Notizen, Projekte und Ideen und gibst hilfreiche, "
        "konkrete Vorschlaege auf Deutsch. Sei praezise und strukturiert."
    )

    if kontext:
        user_content = f"Hier sind meine Obsidian-Notizen:\n\n{kontext}\n\nFrage: {prompt}\n\nAntworte nur basierend auf den Notizen oben."
    else:
        user_content = prompt

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": user_content}],
        "system": system,
        "stream": False,
    }

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=120
        )
        if r.status_code == 200:
            return r.json().get("message", {}).get("content", "Keine Antwort")
        return f"Fehler: {r.status_code}"
    except Exception as e:
        return f"Verbindungsfehler: {e}"


# ──────────────────────────────────────────
#  HAUPTFUNKTIONEN
# ──────────────────────────────────────────
def analysiere_vault():
    """Analysiert alle Notizen und schreibt KI-Zusammenfassung."""
    print("Lese Vault...")
    kontext = obs_get_all_content()

    if not kontext.strip():
        print("Vault ist leer – keine Notizen zum Analysieren.")
        return

    print(f"Analysiere {len(kontext)} Zeichen mit {OLLAMA_MODEL}...")

    prompt = (
        "Analysiere meine Notizen und erstelle eine strukturierte Zusammenfassung:\n"
        "1. Aktive Projekte\n"
        "2. Offene Tasks\n"
        "3. Wiederkehrende Themen/Interessen\n"
        "4. Vorgeschlagene naechste Schritte\n"
        "Formatiere die Ausgabe als Markdown."
    )

    antwort = ollama_frage(prompt, kontext)

    # In Obsidian speichern
    datum = datetime.now().strftime("%Y-%m-%d %H:%M")
    inhalt = f"# KI-Analyse – {datum}\n\n{antwort}\n"
    pfad = f"KI-Vorschlaege/Analyse_{datetime.now().strftime('%Y-%m-%d')}.md"

    if obs_write_file(pfad, inhalt):
        print(f"Analyse gespeichert: {pfad}")
    else:
        print("Fehler beim Speichern – Ausgabe hier:")
        print(antwort)


def stelle_frage(frage: str):
    """Stellt eine Frage ueber den Vault-Inhalt."""
    print("Lese Vault...")
    kontext = obs_get_all_content()
    print(f"Frage an {OLLAMA_MODEL}: {frage}")
    erweiterter_prompt = "Beantworte folgende Frage direkt basierend auf den Notizen aus meinem Obsidian-Vault. Beziehe dich auf konkrete Inhalte: " + frage
    antwort = ollama_frage(erweiterter_prompt, kontext)
    print("\n" + "="*50)
    print(antwort)
    print("="*50)

    # Optional in Obsidian speichern
    datum = datetime.now().strftime("%Y-%m-%d %H:%M")
    inhalt = f"# Frage – {datum}\n\n**Frage:** {frage}\n\n**Antwort:**\n{antwort}\n"
    pfad = f"KI-Vorschlaege/Frage_{datetime.now().strftime('%Y-%m-%d_%H%M')}.md"
    obs_write_file(pfad, inhalt)


def erstelle_vorschlag():
    """Erstellt proaktive Vorschlaege basierend auf dem Vault."""
    print("Erstelle Vorschlaege...")
    kontext = obs_get_all_content()

    prompt = (
        "Basierend auf meinen Notizen: Was sollte ich als naechstes tun? "
        "Gib mir 3-5 konkrete, priorisierte Vorschlaege. "
        "Beruecksichtige meine Projekte, Lernziele und offenen Tasks. "
        "Formatiere als Markdown-Liste."
    )

    antwort = ollama_frage(prompt, kontext)

    datum = datetime.now().strftime("%Y-%m-%d %H:%M")
    inhalt = f"# KI-Vorschlaege – {datum}\n\n{antwort}\n"
    pfad = f"KI-Vorschlaege/Vorschlaege_{datetime.now().strftime('%Y-%m-%d')}.md"

    if obs_write_file(pfad, inhalt):
        print(f"Vorschlaege gespeichert: {pfad}")
    print(antwort)


def teste_verbindung():
    """Testet Obsidian und Ollama Verbindung."""
    print("Teste Obsidian API...")
    try:
        files = obs_get_files()
        print(f"  OK – {len(files)} Dateien im Vault")
    except Exception as e:
        print(f"  FEHLER: {e}")

    print("Teste Ollama...")
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        modelle = [m["name"] for m in r.json().get("models", [])]
        print(f"  OK – Modelle: {', '.join(modelle)}")
    except Exception as e:
        print(f"  FEHLER: {e}")


# ──────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obsidian + Ollama Bridge")
    parser.add_argument("--test",      action="store_true", help="Verbindung testen")
    parser.add_argument("--analyse",   action="store_true", help="Vault analysieren")
    parser.add_argument("--vorschlag", action="store_true", help="Vorschlaege erstellen")
    parser.add_argument("--frage",     type=str,            help="Frage stellen")
    args = parser.parse_args()

    if args.test:
        teste_verbindung()
    elif args.analyse:
        analysiere_vault()
    elif args.vorschlag:
        erstelle_vorschlag()
    elif args.frage:
        stelle_frage(args.frage)
    else:
        print("Obsidian + Ollama Bridge")
        print("Optionen: --test | --analyse | --vorschlag | --frage 'Deine Frage'")
        teste_verbindung()