"""
pokedex_bot.py
JensHQ – JensPokedexBot
Vollständiger Pokédex Bot via Telegram
Datenquelle: PokeAPI (kostenlos, kein Key)

Features:
- Vollprofil mit Bild, Stats, Typ-Matchup, Moves, Shiny-Methoden
- Deutsche Namen aus lokaler DB
- /shiny <n> – nur Shiny-Infos
- /meta <n>  – Competitive Tier + beste Natur
- /formen <n> – Alola/Galar/Hisui Formen
- /gen1-/gen9    – Generationsliste
"""

import requests
import time
import json
import re
import threading
import os
from datetime import datetime

# ──────────────────────────────────────────
#  DEUTSCHE NAMEN DATENBANK
# ──────────────────────────────────────────
NAMEN_DB_PFAD = "/home/jens/JobAgent/daten/pokemon_names_de.json"

def load_namen_db() -> dict:
    if os.path.exists(NAMEN_DB_PFAD):
        try:
            with open(NAMEN_DB_PFAD, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

NAMEN_DB = load_namen_db()

def get_name_de(pokemon_id: int) -> str:
    entry = NAMEN_DB.get(str(pokemon_id), {})
    return entry.get("de", "") or entry.get("en", "")

# ──────────────────────────────────────────
#  KONFIGURATION
# ──────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

TOKEN    = os.getenv("POKEDEXBOT_TOKEN", "")
CHAT_ID  = int(os.getenv("CHAT_ID", "8656887627"))
API_URL  = f"https://api.telegram.org/bot{TOKEN}"
POKE_API = "https://pokeapi.co/api/v2"
POLL_SEC = 3

# ──────────────────────────────────────────
#  GENERATIONEN
# ──────────────────────────────────────────
GENERATIONEN = {
    "gen1": (1,   151,  "Kanto",   "🔴"),
    "gen2": (152, 251,  "Johto",   "⭐"),
    "gen3": (252, 386,  "Hoenn",   "🌿"),
    "gen4": (387, 493,  "Sinnoh",  "💎"),
    "gen5": (494, 649,  "Unova",   "⚫"),
    "gen6": (650, 721,  "Kalos",   "🗼"),
    "gen7": (722, 809,  "Alola",   "🌺"),
    "gen8": (810, 905,  "Galar",   "⚔️"),
    "gen9": (906, 1025, "Paldea",  "🌙"),
}

# ──────────────────────────────────────────
#  TYP-EFFEKTIVITÄT
# ──────────────────────────────────────────
TYP_CHART = {
    "normal":   {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire":     {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2},
    "water":    {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
    "electric": {"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2, "dragon": 0.5},
    "grass":    {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
    "ice":      {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5},
    "fighting": {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, "dark": 2, "steel": 2, "fairy": 0.5},
    "poison":   {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "fairy": 2},
    "ground":   {"fire": 2, "electric": 2, "grass": 0.5, "poison": 2, "flying": 0, "bug": 0.5, "rock": 2, "steel": 2},
    "flying":   {"electric": 0.5, "grass": 2, "fighting": 2, "bug": 2, "rock": 0.5, "steel": 0.5},
    "psychic":  {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
    "bug":      {"fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2, "steel": 0.5, "fairy": 0.5},
    "rock":     {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, "flying": 2, "bug": 2, "steel": 0.5},
    "ghost":    {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
    "dragon":   {"dragon": 2, "steel": 0.5, "fairy": 0},
    "dark":     {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5},
    "steel":    {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "rock": 2, "steel": 0.5, "fairy": 2},
    "fairy":    {"fire": 0.5, "fighting": 2, "poison": 0.5, "dragon": 2, "dark": 2, "steel": 0.5},
}

TYP_EMOJI = {
    "normal": "⬜", "fire": "🔥", "water": "💧", "electric": "⚡",
    "grass": "🌿", "ice": "🧊", "fighting": "🥊", "poison": "☠️",
    "ground": "🌍", "flying": "🌪️", "psychic": "🔮", "bug": "🐛",
    "rock": "🪨", "ghost": "👻", "dragon": "🐉", "dark": "🌑",
    "steel": "⚙️", "fairy": "🧚",
}

TYP_DE = {
    "normal": "Normal", "fire": "Feuer", "water": "Wasser", "electric": "Elektro",
    "grass": "Pflanze", "ice": "Eis", "fighting": "Kampf", "poison": "Gift",
    "ground": "Boden", "flying": "Flug", "psychic": "Psycho", "bug": "Käfer",
    "rock": "Gestein", "ghost": "Geist", "dragon": "Drache", "dark": "Unlicht",
    "steel": "Stahl", "fairy": "Fee",
}

STAT_NAMEN = {
    "hp": "❤️ KP", "attack": "⚔️ ANG", "defense": "🛡️ VER",
    "special-attack": "💫 SP.ANG", "special-defense": "🔰 SP.VER", "speed": "⚡ INIT"
}

# ──────────────────────────────────────────
#  COMPETITIVE TIER DATENBANK (Smogon)
# ──────────────────────────────────────────
SMOGON_TIER = {
    "charizard":    ("OU",   "Timid / Modest", "252 SP.ANG / 252 INIT / 4 KP"),
    "blastoise":    ("UU",   "Modest",         "252 SP.ANG / 252 INIT / 4 KP"),
    "venusaur":     ("UU",   "Modest",         "252 SP.ANG / 252 INIT / 4 KP"),
    "pikachu":      ("LC",   "Timid",          "252 SP.ANG / 252 INIT / 4 KP"),
    "raichu":       ("PU",   "Timid",          "252 SP.ANG / 252 INIT / 4 KP"),
    "mewtwo":       ("Uber", "Timid / Modest", "252 SP.ANG / 252 INIT / 4 KP"),
    "mew":          ("Uber", "Timid",          "252 SP.ANG / 252 INIT / 4 KP"),
    "gengar":       ("OU",   "Timid",          "252 SP.ANG / 252 INIT / 4 KP"),
    "alakazam":     ("OU",   "Timid",          "252 SP.ANG / 252 INIT / 4 KP"),
    "machamp":      ("UU",   "Adamant",        "252 ANG / 252 KP / 4 VER"),
    "garchomp":     ("OU",   "Jolly",          "252 ANG / 252 INIT / 4 KP"),
    "lucario":      ("OU",   "Jolly / Timid",  "252 ANG / 252 INIT / 4 KP"),
    "toxapex":      ("OU",   "Bold",           "252 KP / 252 VER / 4 SP.VER"),
    "dragapult":    ("OU",   "Timid",          "252 SP.ANG / 252 INIT / 4 KP"),
    "iron-valiant": ("OU",   "Timid",          "252 SP.ANG / 252 INIT / 4 KP"),
    "great-tusk":   ("OU",   "Jolly",          "252 ANG / 252 INIT / 4 KP"),
    "corviknight":  ("OU",   "Impish",         "252 KP / 252 VER / 4 SP.VER"),
    "hatterene":    ("OU",   "Quiet",          "252 SP.ANG / 252 KP / 4 SP.VER"),
    "kyogre":       ("Uber", "Modest",         "252 SP.ANG / 252 INIT / 4 KP"),
    "groudon":      ("Uber", "Adamant",        "252 ANG / 252 INIT / 4 KP"),
    "rayquaza":     ("Uber", "Adamant",        "252 ANG / 252 INIT / 4 KP"),
    "tyranitar":    ("OU",   "Adamant",        "252 ANG / 252 KP / 4 VER"),
    "scizor":       ("OU",   "Adamant",        "252 ANG / 252 KP / 4 VER"),
    "rotom-wash":   ("OU",   "Bold",           "252 KP / 252 VER / 4 SP.VER"),
    "weavile":      ("OU",   "Jolly",          "252 ANG / 252 INIT / 4 KP"),
    "dragonite":    ("OU",   "Adamant",        "252 ANG / 252 INIT / 4 KP"),
    "salamence":    ("UU",   "Jolly",          "252 ANG / 252 INIT / 4 KP"),
    "clefable":     ("OU",   "Calm",           "252 KP / 252 SP.VER / 4 VER"),
    "slowbro":      ("UU",   "Bold",           "252 KP / 252 VER / 4 SP.VER"),
    "talonflame":   ("UU",   "Jolly",          "252 ANG / 252 INIT / 4 KP"),
    "landorus-therian": ("OU", "Jolly",        "252 ANG / 252 INIT / 4 KP"),
}

TIER_ERKLAERUNG = {
    "Uber": "🔴 Uber – zu stark für OU, Ban-Tier",
    "OU":   "🟠 OU (Over Used) – Top-Tier Metagame",
    "UU":   "🟡 UU (Under Used) – Solide Wahl",
    "RU":   "🟢 RU (Rarely Used) – Nischen-Tier",
    "NU":   "🔵 NU (Never Used) – Schwaches Tier",
    "PU":   "⚪ PU – Schwächstes kompetitives Tier",
    "LC":   "🟣 LC (Little Cup) – Nur für Basis-Pokémon",
    "NFE":  "⬛ NFE – Nicht voll entwickelt",
}

def get_smogon_tier(name_en: str):
    key = name_en.lower().replace(" ", "-")
    return SMOGON_TIER.get(key, None)

# ──────────────────────────────────────────
#  ROM-HACK DATENBANK
# ──────────────────────────────────────────
ROMHACK_DB = {
    # ── Starters & Basis ──
    1:   [("Radical Red",     "Starter"), ("Unbound",          "Starter"), ("Renegade Platinum","Starter"), ("Blazing Emerald",  "Starter")],
    4:   [("Radical Red",     "Starter"), ("Unbound",          "Starter"), ("Renegade Platinum","Starter"), ("Blazing Emerald",  "Starter")],
    7:   [("Radical Red",     "Starter"), ("Unbound",          "Starter"), ("Renegade Platinum","Starter"), ("Blazing Emerald",  "Starter")],
    2:   [("Radical Red",     "Route 2"), ("Unbound",          "Wildnis")],
    3:   [("Radical Red",     "Route 12"), ("Unbound",         "Wildnis Wald"), ("Blazing Emerald",  "Wildnis")],
    5:   [("Radical Red",     "Route 2"), ("Unbound",          "Wildnis")],
    6:   [("Unbound",         "Wildnis + Starter-Event"), ("Radical Red",  "Route 3"), ("Blazing Emerald",  "Lavehügel"), ("Insurgence",       "Wildnis")],
    8:   [("Radical Red",     "Surf-Route"), ("Unbound",       "Küste")],
    9:   [("Unbound",         "Küstenregion"), ("Radical Red", "Surfroute"), ("Blazing Emerald",  "Wildnis")],
    # ── Gen 1 Legenden ──
    144: [("Radical Red",     "Seafoam Islands"), ("Unbound",   "Lavehügel"), ("Renegade Platinum","Wildnis")],
    145: [("Radical Red",     "Power Plant"), ("Unbound",       "Power Plant"), ("Renegade Platinum","Wildnis")],
    146: [("Radical Red",     "Mt. Ember"), ("Unbound",         "Lavehügel"), ("Renegade Platinum","Wildnis")],
    150: [("Unbound",         "Mewtu Höhle (Postgame)"), ("Radical Red",  "Cerulean Cave"), ("Glazed",           "Event"), ("Insurgence",       "Perfection Cult Base")],
    151: [("Unbound",         "Event"), ("Radical Red",         "Old Sea Chart"), ("Glazed",           "Event"), ("Renegade Platinum","Wildnis")],
    # ── Populäre Gen 1 ──
    25:  [("Unbound",         "Route 5"), ("Radical Red",       "Überall"), ("Blazing Emerald",  "Route 117"), ("Renegade Platinum","Route 201")],
    26:  [("Radical Red",     "Route 10"), ("Unbound",          "Route 8")],
    37:  [("Radical Red",     "Route 36"), ("Unbound",          "Wildnis")],
    38:  [("Radical Red",     "Route 36"), ("Unbound",          "Wildnis")],
    52:  [("Radical Red",     "Route 5"), ("Unbound",           "Route 3")],
    54:  [("Radical Red",     "Route 25"), ("Unbound",          "See")],
    58:  [("Radical Red",     "Route 7"), ("Unbound",           "Wildnis")],
    59:  [("Radical Red",     "Route 7"), ("Unbound",           "Wildnis")],
    63:  [("Radical Red",     "Route 24"), ("Unbound",          "Wildnis")],
    65:  [("Radical Red",     "Route 24"), ("Unbound",          "Wildnis")],
    92:  [("Radical Red",     "Lavender Town"), ("Unbound",     "Geisterturm")],
    130: [("Radical Red",     "Surf-Route"), ("Unbound",        "Küste")],
    131: [("Radical Red",     "Seafoam Islands"), ("Unbound",   "Event")],
    133: [("Radical Red",     "Celadon City"), ("Unbound",      "Route 6")],
    134: [("Radical Red",     "Wasser-Route"), ("Unbound",      "See")],
    135: [("Radical Red",     "Power Plant"), ("Unbound",       "Route 8")],
    136: [("Radical Red",     "Wildnis"), ("Unbound",           "Route 10")],
    143: [("Radical Red",     "Fuschia Safari"), ("Unbound",    "Höhle")],
    149: [("Unbound",         "Route 20"), ("Radical Red",      "Route 23")],
    # ── Gen 2 ──
    154: [("Radical Red",     "Starter"), ("Blazing Emerald",   "Starter"), ("Renegade Platinum","Starter")],
    157: [("Radical Red",     "Starter"), ("Blazing Emerald",   "Starter")],
    160: [("Radical Red",     "Starter"), ("Blazing Emerald",   "Starter")],
    175: [("Radical Red",     "Route 34 Ei"), ("Unbound",       "Ei-Event")],
    196: [("Radical Red",     "Celadon City"), ("Unbound",      "Route 9")],
    197: [("Radical Red",     "Celadon City"), ("Unbound",      "Route 9")],
    212: [("Radical Red",     "Route 14"), ("Unbound",          "Wildnis")],
    248: [("Radical Red",     "Mt. Silver"), ("Unbound",        "Gebirge"), ("Renegade Platinum","Gebirge")],
    249: [("Radical Red",     "Navel Rock"), ("Unbound",        "Event"), ("Glazed",           "Event")],
    250: [("Radical Red",     "Navel Rock"), ("Unbound",        "Event"), ("Glazed",           "Event")],
    251: [("Radical Red",     "Event"), ("Glazed",              "Event"), ("Insurgence",        "Event")],
    # ── Gen 3 ──
    252: [("Blazing Emerald",  "Starter"), ("Radical Red",      "Starter"), ("Renegade Platinum","Starter")],
    255: [("Blazing Emerald",  "Starter"), ("Radical Red",      "Starter")],
    258: [("Blazing Emerald",  "Starter"), ("Radical Red",      "Starter")],
    282: [("Radical Red",     "Route 14"), ("Unbound",          "Wildnis"), ("Blazing Emerald",  "Wildnis")],
    302: [("Blazing Emerald",  "Wildnis"), ("Radical Red",      "Route 14")],
    334: [("Blazing Emerald",  "Wildnis"), ("Radical Red",      "Wildnis")],
    350: [("Blazing Emerald",  "Route 118"), ("Radical Red",    "Wasser-Route")],
    359: [("Blazing Emerald",  "Wildnis"), ("Radical Red",      "Route 13")],
    373: [("Blazing Emerald",  "Wildnis"), ("Radical Red",      "Route 21"), ("Insurgence",       "Wildnis")],
    376: [("Blazing Emerald",  "Wildnis"), ("Radical Red",      "Route 23")],
    377: [("Blazing Emerald",  "Felsenberg"), ("Radical Red",   "Felsenberg"), ("Renegade Platinum","Wildnis")],
    378: [("Blazing Emerald",  "Inseleishöhle"), ("Radical Red","Inseleishöhle")],
    379: [("Blazing Emerald",  "Stahlinsel"), ("Radical Red",   "Stahlinsel")],
    380: [("Blazing Emerald",  "Himmelsturm"), ("Radical Red",  "Himmelsturm")],
    381: [("Blazing Emerald",  "Himmelsturm"), ("Radical Red",  "Himmelsturm")],
    382: [("Blazing Emerald",  "Meeresbodengrotte"), ("Radical Red","Meeresbodengrotte")],
    383: [("Blazing Emerald",  "Feuerhöhle"), ("Radical Red",   "Feuerhöhle")],
    384: [("Unbound",          "Dramaturga-Gipfel"), ("Blazing Emerald","Sky Pillar"), ("Radical Red",    "Sky Pillar")],
    385: [("Blazing Emerald",  "Event"), ("Radical Red",        "Event")],
    386: [("Blazing Emerald",  "Event"), ("Radical Red",        "Event")],
    # ── Gen 4 ──
    387: [("Renegade Platinum","Starter"), ("Radical Red",      "Starter")],
    390: [("Renegade Platinum","Starter"), ("Radical Red",      "Starter")],
    393: [("Renegade Platinum","Starter"), ("Radical Red",      "Starter")],
    395: [("Renegade Platinum","Route 213"), ("Radical Red",    "Wasser-Route")],
    403: [("Renegade Platinum","Route 202"), ("Radical Red",    "Route 2")],
    405: [("Renegade Platinum","Route 222"), ("Radical Red",    "Route 13")],
    409: [("Renegade Platinum","Mt. Coronet"), ("Radical Red",  "Gebirge")],
    430: [("Renegade Platinum","Route 216"), ("Radical Red",    "Route 17")],
    437: [("Renegade Platinum","Wildnis"), ("Radical Red",      "Wildnis")],
    445: [("Radical Red",      "Route 13"), ("Unbound",         "Wildnis"), ("Renegade Platinum","Route 210")],
    448: [("Radical Red",      "Route 8"), ("Unbound",          "Kampfzone"), ("Renegade Platinum","Route 209")],
    461: [("Renegade Platinum","Route 216"), ("Radical Red",    "Route 17")],
    466: [("Renegade Platinum","Wildnis"), ("Radical Red",      "Wildnis")],
    467: [("Renegade Platinum","Wildnis"), ("Radical Red",      "Wildnis")],
    468: [("Renegade Platinum","Event"), ("Radical Red",        "Event")],
    472: [("Renegade Platinum","Wildnis"), ("Radical Red",      "Wildnis")],
    473: [("Renegade Platinum","Route 217"), ("Radical Red",    "Route 17")],
    475: [("Renegade Platinum","Wildnis"), ("Radical Red",      "Wildnis")],
    478: [("Renegade Platinum","Route 217"), ("Radical Red",    "Route 17")],
    480: [("Renegade Platinum","Bekannter Turm"), ("Radical Red","Bekannter Turm")],
    481: [("Renegade Platinum","Seegarten See"), ("Radical Red","Seegarten See")],
    482: [("Renegade Platinum","Seegarten See"), ("Radical Red","Seegarten See")],
    483: [("Renegade Platinum","Spear Pillar"), ("Radical Red", "Spear Pillar")],
    484: [("Renegade Platinum","Spear Pillar"), ("Radical Red", "Spear Pillar")],
    485: [("Renegade Platinum","Stark Mountain"), ("Radical Red","Stark Mountain")],
    486: [("Renegade Platinum","Snowpoint Temple"), ("Radical Red","Snowpoint Temple")],
    487: [("Renegade Platinum","Distortion World"), ("Radical Red","Distortion World")],
    488: [("Renegade Platinum","Seegarten See"), ("Radical Red","Seegarten See")],
    491: [("Renegade Platinum","Newmoon Island"), ("Radical Red","Newmoon Island")],
    492: [("Renegade Platinum","Shaymin Route"), ("Radical Red","Event")],
    493: [("Renegade Platinum","Event"), ("Radical Red",        "Event")],
    # ── Gen 5 ──
    495: [("Radical Red",      "Starter"), ("Insurgence",       "Starter")],
    498: [("Radical Red",      "Starter"), ("Insurgence",       "Starter")],
    501: [("Radical Red",      "Starter"), ("Insurgence",       "Starter")],
    571: [("Radical Red",      "Route 14"), ("Unbound",         "Wildnis")],
    609: [("Radical Red",      "Wildnis"), ("Unbound",          "Geisterturm")],
    612: [("Radical Red",      "Route 21"), ("Unbound",         "Wildnis")],
    628: [("Radical Red",      "Route 21"), ("Renegade Platinum","Wildnis")],
    635: [("Radical Red",      "Route 21"), ("Unbound",         "Wildnis")],
    641: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    642: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    643: [("Radical Red",      "N's Castle"), ("Insurgence",    "Wildnis")],
    644: [("Radical Red",      "N's Castle"), ("Insurgence",    "Wildnis")],
    645: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    646: [("Radical Red",      "Giant Chasm"), ("Unbound",      "Event")],
    647: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    648: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    649: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    # ── Gen 6 ──
    650: [("Radical Red",      "Starter"), ("Insurgence",       "Starter")],
    653: [("Radical Red",      "Starter"), ("Insurgence",       "Starter")],
    656: [("Radical Red",      "Starter"), ("Insurgence",       "Starter")],
    700: [("Radical Red",      "Route 4"), ("Unbound",          "Wildnis")],
    716: [("Radical Red",      "Team Flare HQ"), ("Insurgence", "Wildnis")],
    717: [("Radical Red",      "Team Flare HQ"), ("Insurgence", "Wildnis")],
    718: [("Radical Red",      "Terminus Cave"), ("Insurgence", "Wildnis")],
    719: [("Radical Red",      "Event"), ("Insurgence",         "Event")],
    720: [("Radical Red",      "Event"), ("Insurgence",         "Event")],
    721: [("Radical Red",      "Event"), ("Insurgence",         "Event")],
    # ── Gen 7 ──
    722: [("Radical Red",      "Starter")],
    725: [("Radical Red",      "Starter")],
    728: [("Radical Red",      "Starter")],
    741: [("Radical Red",      "Route 4"), ("Unbound",          "Wildnis")],
    745: [("Radical Red",      "Route 21"), ("Unbound",         "Wildnis")],
    758: [("Radical Red",      "Route 8"), ("Unbound",          "Wildnis")],
    764: [("Radical Red",      "Route 14"), ("Unbound",         "Wildnis")],
    773: [("Radical Red",      "Wildnis"), ("Unbound",          "Wildnis")],
    785: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    786: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    787: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    788: [("Radical Red",      "Event"), ("Unbound",            "Event")],
    791: [("Radical Red",      "Alter of the Sunne"), ("Unbound","Event")],
    792: [("Radical Red",      "Alter of the Moone"), ("Unbound","Event")],
    793: [("Radical Red",      "Ultra Space"), ("Unbound",      "Event")],
    800: [("Radical Red",      "Ultra Space"), ("Unbound",      "Event")],
    # ── Gen 8 ──
    810: [("Radical Red",      "Starter")],
    813: [("Radical Red",      "Starter")],
    816: [("Radical Red",      "Starter")],
    884: [("Radical Red",      "Wildnis")],
    887: [("Radical Red",      "Wildnis")],
    888: [("Radical Red",      "Energie-Kraftwerk")],
    889: [("Radical Red",      "Energie-Kraftwerk")],
    890: [("Radical Red",      "Crown Tundra")],
    898: [("Radical Red",      "Crown Tundra")],
}

def get_romhack_info(pokemon_id: int) -> str:
    hacks = ROMHACK_DB.get(pokemon_id, [])
    if not hacks:
        return ""
    lines = ["🕹️ <b>ROM-Hack Verfügbarkeit:</b>"]
    for hack, hinweis in hacks:
        lines.append(f"   • {hack}: {hinweis}")
    return "\n".join(lines)

# ──────────────────────────────────────────
#  FORM-VARIANTEN DATENBANK
# ──────────────────────────────────────────
FORM_VARIANTEN = {
    "rattata":    [("rattata-alola",     "Alola-Form 🌺")],
    "raticate":   [("raticate-alola",    "Alola-Form 🌺")],
    "raichu":     [("raichu-alola",      "Alola-Form 🌺")],
    "sandshrew":  [("sandshrew-alola",   "Alola-Form 🌺")],
    "sandslash":  [("sandslash-alola",   "Alola-Form 🌺")],
    "vulpix":     [("vulpix-alola",      "Alola-Form 🌺")],
    "ninetales":  [("ninetales-alola",   "Alola-Form 🌺")],
    "diglett":    [("diglett-alola",     "Alola-Form 🌺")],
    "dugtrio":    [("dugtrio-alola",     "Alola-Form 🌺")],
    "meowth":     [("meowth-alola",      "Alola-Form 🌺"), ("meowth-galar", "Galar-Form ⚔️")],
    "persian":    [("persian-alola",     "Alola-Form 🌺")],
    "geodude":    [("geodude-alola",     "Alola-Form 🌺")],
    "graveler":   [("graveler-alola",    "Alola-Form 🌺")],
    "golem":      [("golem-alola",       "Alola-Form 🌺")],
    "grimer":     [("grimer-alola",      "Alola-Form 🌺")],
    "muk":        [("muk-alola",         "Alola-Form 🌺")],
    "exeggutor":  [("exeggutor-alola",   "Alola-Form 🌺")],
    "marowak":    [("marowak-alola",     "Alola-Form 🌺")],
    "ponyta":     [("ponyta-galar",      "Galar-Form ⚔️")],
    "rapidash":   [("rapidash-galar",    "Galar-Form ⚔️")],
    "slowpoke":   [("slowpoke-galar",    "Galar-Form ⚔️")],
    "slowbro":    [("slowbro-galar",     "Galar-Form ⚔️")],
    "slowking":   [("slowking-galar",    "Galar-Form ⚔️")],
    "farfetchd":  [("farfetchd-galar",   "Galar-Form ⚔️")],
    "weezing":    [("weezing-galar",     "Galar-Form ⚔️")],
    "mr-mime":    [("mr-mime-galar",     "Galar-Form ⚔️")],
    "articuno":   [("articuno-galar",    "Galar-Form ⚔️")],
    "zapdos":     [("zapdos-galar",      "Galar-Form ⚔️")],
    "moltres":    [("moltres-galar",     "Galar-Form ⚔️")],
    "corsola":    [("corsola-galar",     "Galar-Form ⚔️")],
    "zigzagoon":  [("zigzagoon-galar",   "Galar-Form ⚔️")],
    "linoone":    [("linoone-galar",     "Galar-Form ⚔️")],
    "darumaka":   [("darumaka-galar",    "Galar-Form ⚔️")],
    "darmanitan": [("darmanitan-galar",  "Galar-Form ⚔️"), ("darmanitan-galar-zen", "Galar Zen-Modus ⚔️")],
    "yamask":     [("yamask-galar",      "Galar-Form ⚔️")],
    "stunfisk":   [("stunfisk-galar",    "Galar-Form ⚔️")],
    # Hisui
    "growlithe":  [("growlithe-hisui",   "Hisui-Form 🏔️")],
    "arcanine":   [("arcanine-hisui",    "Hisui-Form 🏔️")],
    "voltorb":    [("voltorb-hisui",     "Hisui-Form 🏔️")],
    "electrode":  [("electrode-hisui",   "Hisui-Form 🏔️")],
    "typhlosion": [("typhlosion-hisui",  "Hisui-Form 🏔️")],
    "qwilfish":   [("qwilfish-hisui",    "Hisui-Form 🏔️")],
    "sneasel":    [("sneasel-hisui",     "Hisui-Form 🏔️")],
    "samurott":   [("samurott-hisui",    "Hisui-Form 🏔️")],
    "lilligant":  [("lilligant-hisui",   "Hisui-Form 🏔️")],
    "zorua":      [("zorua-hisui",       "Hisui-Form 🏔️")],
    "zoroark":    [("zoroark-hisui",     "Hisui-Form 🏔️")],
    "braviary":   [("braviary-hisui",    "Hisui-Form 🏔️")],
    "sliggoo":    [("sliggoo-hisui",     "Hisui-Form 🏔️")],
    "goodra":     [("goodra-hisui",      "Hisui-Form 🏔️")],
    "avalugg":    [("avalugg-hisui",     "Hisui-Form 🏔️")],
    "decidueye":  [("decidueye-hisui",   "Hisui-Form 🏔️")],
}

# ──────────────────────────────────────────
#  TELEGRAM FUNKTIONEN
# ──────────────────────────────────────────
def send_text(text: str, chat_id: int = CHAT_ID) -> bool:
    try:
        r = requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id, "text": text,
            "parse_mode": "HTML", "disable_web_page_preview": True
        }, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[FEHLER] send_text: {e}")
        return False

def send_photo(photo_url: str, caption: str, chat_id: int = CHAT_ID) -> bool:
    try:
        if len(caption) <= 1024:
            r = requests.post(f"{API_URL}/sendPhoto", json={
                "chat_id": chat_id, "photo": photo_url,
                "caption": caption, "parse_mode": "HTML"
            }, timeout=15)
            return r.json().get("ok", False)
        else:
            # Bild ohne Caption, dann Text separat
            r = requests.post(f"{API_URL}/sendPhoto", json={
                "chat_id": chat_id, "photo": photo_url
            }, timeout=15)
            ok = r.json().get("ok", False)
            send_text(caption, chat_id)
            return ok
    except Exception as e:
        print(f"[FEHLER] send_photo: {e}")
        return False

def send_text_with_button(text: str, button_label: str, callback_data: str, chat_id: int = CHAT_ID) -> bool:
    try:
        r = requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id, "text": text,
            "parse_mode": "HTML", "disable_web_page_preview": True,
            "reply_markup": {"inline_keyboard": [[{"text": button_label, "callback_data": callback_data}]]}
        }, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[FEHLER] send_text_with_button: {e}")
        return False

def send_photo_with_button(photo_url: str, caption: str, button_label: str, callback_data: str, chat_id: int = CHAT_ID) -> bool:
    try:
        markup = {"inline_keyboard": [[{"text": button_label, "callback_data": callback_data}]]}
        if len(caption) <= 1024:
            r = requests.post(f"{API_URL}/sendPhoto", json={
                "chat_id": chat_id, "photo": photo_url,
                "caption": caption, "parse_mode": "HTML",
                "reply_markup": markup
            }, timeout=15)
            return r.json().get("ok", False)
        else:
            requests.post(f"{API_URL}/sendPhoto", json={"chat_id": chat_id, "photo": photo_url}, timeout=15)
            r2 = requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id, "text": caption,
                "parse_mode": "HTML", "disable_web_page_preview": True,
                "reply_markup": markup
            }, timeout=10)
            return r2.json().get("ok", False)
    except Exception as e:
        print(f"[FEHLER] send_photo_with_button: {e}")
        return False

def answer_callback(callback_query_id: str) -> None:
    try:
        requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query_id}, timeout=5)
    except Exception:
        pass

# Cache: poke_id -> vollständige Fang-Liste als fertiger Text
FANG_CACHE: dict = {}

def get_updates(offset: int) -> list:
    try:
        r = requests.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 2}, timeout=10)
        data = r.json()
        return data.get("result", []) if data.get("ok") else []
    except Exception:
        return []

# ──────────────────────────────────────────
#  POKEAPI FUNKTIONEN
# ──────────────────────────────────────────
def api_get(url: str) -> dict:
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 404:
                return {}
        except Exception:
            time.sleep(1)
    return {}

def get_pokemon(name_or_id: str) -> dict:
    return api_get(f"{POKE_API}/pokemon/{name_or_id.lower()}")

def get_pokemon_species(name_or_id: str) -> dict:
    return api_get(f"{POKE_API}/pokemon-species/{name_or_id.lower()}")

def get_de_name(species: dict) -> str:
    for n in species.get("names", []):
        if n["language"]["name"] == "de":
            return n["name"]
    return species.get("name", "").capitalize()

def get_de_text(species: dict) -> str:
    for entry in species.get("flavor_text_entries", []):
        if entry["language"]["name"] == "de":
            return entry["flavor_text"].replace("\n", " ").replace("\f", " ")
    for entry in species.get("flavor_text_entries", []):
        if entry["language"]["name"] == "en":
            text = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
            return "(EN) " + text
    return ""

def get_genus(species: dict) -> str:
    for g in species.get("genera", []):
        if g["language"]["name"] == "de":
            return g["genus"]
    return ""

MOVE_NAME_CACHE = {}

def get_move_name_de(move_name_en: str) -> str:
    """Holt deutschen Move-Namen von PokeAPI mit Cache."""
    key = move_name_en.lower()
    if key in MOVE_NAME_CACHE:
        return MOVE_NAME_CACHE[key]
    data = api_get(f"{POKE_API}/move/{key}")
    if data:
        for n in data.get("names", []):
            if n["language"]["name"] == "de":
                MOVE_NAME_CACHE[key] = n["name"]
                return n["name"]
    # Fallback: englisch formatiert
    fallback = move_name_en.replace("-", " ").title()
    MOVE_NAME_CACHE[key] = fallback
    return fallback


ABILITY_CACHE: dict = {}

def get_ability_name_de(ability_name_en: str) -> str:
    """Holt deutschen Fähigkeits-Namen von PokeAPI mit Cache."""
    key = ability_name_en.lower()
    if key in ABILITY_CACHE:
        return ABILITY_CACHE[key]
    data = api_get(f"{POKE_API}/ability/{key}")
    if data:
        for n in data.get("names", []):
            if n["language"]["name"] == "de":
                ABILITY_CACHE[key] = n["name"]
                return n["name"]
    fallback = ability_name_en.replace("-", " ").title()
    ABILITY_CACHE[key] = fallback
    return fallback

def resolve_name_to_id(name_or_id: str) -> str:
    """Wandelt deutschen/englischen Namen oder Nummer (mit führenden Nullen) in API-kompatiblen String um."""
    if name_or_id.isdigit():
        return str(int(name_or_id))
    name_lower = name_or_id.lower()
    for poke_id, entry in NAMEN_DB.items():
        if entry.get("de", "").lower() == name_lower:
            return poke_id
        if entry.get("en", "").lower() == name_lower:
            return poke_id
    return name_or_id

# ──────────────────────────────────────────
#  TYP-EFFEKTIVITÄT
# ──────────────────────────────────────────
def berechne_effektivitaet(typen: list) -> dict:
    effekte = {}
    for angriff_typ, verteidigung_map in TYP_CHART.items():
        multiplikator = 1.0
        for verteidiger in typen:
            multiplikator *= verteidigung_map.get(verteidiger, 1.0)
        if multiplikator != 1.0:
            effekte[angriff_typ] = multiplikator
    return effekte

# ──────────────────────────────────────────
#  FANGMETHODE – alle Spiele
# ──────────────────────────────────────────
SPIEL_DE = {
    # Gen 1
    "red-japan": "Rot (JP)", "blue-japan": "Blau (JP)", "green-japan": "Grün (JP)",
    "red": "Rot", "blue": "Blau", "yellow": "Gelb",
    # Gen 2
    "gold": "Gold", "silver": "Silber", "crystal": "Kristall",
    # Gen 3
    "ruby": "Rubin", "sapphire": "Saphir", "emerald": "Smaragd",
    "firered": "Feuerrot", "leafgreen": "Blattgrün",
    # Gen 4
    "diamond": "Diamant", "pearl": "Perl", "platinum": "Platin",
    "heartgold": "Goldene Edition", "soulsilver": "Silberne Edition",
    # Gen 5
    "black": "Schwarz", "white": "Weiß",
    "black-2": "Schwarz 2", "white-2": "Weiß 2",
    # Gen 6
    "x": "X", "y": "Y",
    "omega-ruby": "Omega Rubin", "alpha-sapphire": "Alpha Saphir",
    # Gen 7
    "sun": "Sonne", "moon": "Mond",
    "ultra-sun": "Ultra Sonne/Mond", "ultra-moon": "Ultra Sonne/Mond",
    # Gen 8
    "sword": "Schwert", "shield": "Schild",
    "lets-go-pikachu": "Lets Go: Pikachu/Evoli", "lets-go-eevee": "Lets Go: Pikachu/Evoli",
    "brilliant-diamond": "Leuchtend Diamant/Perl", "shining-pearl": "Leuchtend Diamant/Perl",
    "legends-arceus": "Legenden: Arceus",
    # Gen 9
    "scarlet": "Karmesin/Purpur", "violet": "Karmesin/Purpur",
}

SPIEL_GRUPPE = {
    "ultra-moon":    "ultra-sun",
    "lets-go-eevee": "lets-go-pikachu",
    "shining-pearl": "brilliant-diamond",
    "violet":        "scarlet",
}

METHODE_DE = {
    "walk": "Wildnis (Laufen)",
    "overworld": "Overworld (Sichtbar)",
    "old-rod": "Alte Angel",
    "good-rod": "Gute Angel",
    "super-rod": "Superangel",
    "surf": "Surfen",
    "rock-smash": "Zertrümmerer",
    "headbutt": "Kopfnuss (Baum)",
    "gift": "Geschenk / Event",
    "pokeradar": "Pokéradar",
    "dark-grass": "Hohes Gras",
    "cave": "Höhle",
    "grass": "Gras",
    "waterfall": "Wasserfall",
    "sos-encounter": "SOS-Kette",
    "only-one": "Einmalig",
    "special": "Special",
}

def beste_fangmethode(encounters: list, catch_rate: int) -> str:
    if not encounters:
        return "❓ Nur durch Tausch oder Event erhältlich", "❓ Nur durch Tausch oder Event erhältlich", 0

    spiele = {}
    for enc in encounters:
        ort = enc.get("location_area", {}).get("name", "")
        for version_detail in enc.get("version_details", []):
            spiel = version_detail.get("version", {}).get("name", "")
            if not spiel:
                continue
            spiel = SPIEL_GRUPPE.get(spiel, spiel)
            for ed in version_detail.get("encounter_details", []):
                chance  = ed.get("chance", 0)
                methode = ed.get("method", {}).get("name", "")
                lvl_min = ed.get("min_level", 0)
                lvl_max = ed.get("max_level", 0)
                if spiel not in spiele or chance > spiele[spiel]["chance"]:
                    spiele[spiel] = {
                        "chance":  chance,
                        "methode": methode,
                        "lvl_min": lvl_min,
                        "lvl_max": lvl_max,
                        "ort":     ort,
                    }

    if not spiele:
        return "❓ Keine Wildencounter-Daten verfügbar", "❓ Keine Wildencounter-Daten verfügbar", 0

    spiel_prio = list(SPIEL_DE.keys())
    def sort_key(s):
        try: return spiel_prio.index(s)
        except ValueError: return -1

    sortiert = sorted(spiele.keys(), key=sort_key, reverse=True)
    gesamt = len(sortiert)

    def zeile(spiel):
        d = spiele[spiel]
        spiel_str   = SPIEL_DE.get(spiel, spiel.replace("-", " ").title())
        methode_str = METHODE_DE.get(d["methode"], d["methode"].replace("-", " ").title())
        ort_str     = d["ort"].replace("-", " ").title()
        return "   🎮 " + spiel_str + ": " + ort_str + " | " + methode_str + " | Lvl " + str(d["lvl_min"]) + "-" + str(d["lvl_max"])

    header = "🎯 <b>Fangbar in:</b> (Fangrate: " + str(catch_rate) + "/255)"

    # Vollständige Liste für Cache
    alle_zeilen = [header] + [zeile(s) for s in sortiert]
    volle_liste = "\n".join(alle_zeilen)

    # Kurze Liste: nur 3 neueste
    kurz_zeilen = [header] + [zeile(s) for s in sortiert[:3]]
    if gesamt > 3:
        kurz_zeilen.append("   <i>+ " + str(gesamt - 3) + " weitere Spiele...</i>")

    return "\n".join(kurz_zeilen), volle_liste, gesamt

# ──────────────────────────────────────────
#  ENTWICKLUNGSLINIE
# ──────────────────────────────────────────
def get_evolution_chain(species: dict) -> str:
    chain_url = species.get("evolution_chain", {}).get("url", "")
    if not chain_url:
        return ""
    data = api_get(chain_url)
    if not data:
        return ""

    def parse_chain(chain):
        species_url = chain["species"]["url"]
        poke_id = int(species_url.rstrip("/").split("/")[-1])
        name_de = get_name_de(poke_id)
        name = name_de if name_de else chain["species"]["name"].capitalize()
        result = [name]
        for evo in chain.get("evolves_to", []):
            result.extend(parse_chain(evo))
        return result

    mons = parse_chain(data.get("chain", {}))
    return " → ".join(mons)

# ──────────────────────────────────────────
#  SHINY INFO
# ──────────────────────────────────────────
SHINY_METHODEN = {
    1: ("Gold/Silber (Gen 2)", [
        "Zufallsbegegnung (1/8192)",
        "Masuda-Methode (Gen 4+)",
        "Schillernder Charme (Gen 6+)"
    ]),
    2: ("Rubin/Saphir (Gen 3)", [
        "Zufallsbegegnung (1/8192)",
        "Masuda-Methode (Gen 4+)"
    ]),
    3: ("Diamant/Perl (Gen 4)", [
        "Masuda-Methode (1/1639)",
        "Pokéradar-Kettenmethode",
        "Schillernder Charme (Gen 6+)"
    ]),
    4: ("Schwarz/Weiß (Gen 5)", [
        "Masuda-Methode (1/1365)",
        "Schillernder Charme (1/1024)",
        "Soft Reset bei Legenden"
    ]),
    5: ("X/Y (Gen 6)", [
        "Masuda-Methode (1/683)",
        "Horden-Methode",
        "Pokéradar-Kette"
    ]),
    6: ("Sonne/Mond (Gen 7)", [
        "SOS-Ketten-Methode (1/315 bei Kette 70+)",
        "Masuda-Methode (1/512)",
        "Schillernder Charme"
    ]),
    7: ("Schwert/Schild (Gen 8)", [
        "Brillianter Glanz / Overworld (1/100 bei 500 Kämpfen)",
        "Masuda-Methode (1/512)",
        "Schillernder Charme"
    ]),
    8: ("Karmesin/Purpur (Gen 9)", [
        "Massenausbruch-Methode (1/100 bei 60 Besiegt)",
        "Masuda-Methode (1/512)",
        "Schillernder Charme"
    ]),
}

def get_shiny_info(pokemon_id: int) -> str:
    if pokemon_id > 905:
        gen = 8
    elif pokemon_id > 809:
        gen = 7
    elif pokemon_id > 721:
        gen = 6
    elif pokemon_id > 649:
        gen = 5
    elif pokemon_id > 493:
        gen = 4
    elif pokemon_id > 386:
        gen = 3
    elif pokemon_id > 251:
        gen = 2
    else:
        gen = 1

    info = SHINY_METHODEN.get(gen, SHINY_METHODEN[8])
    methoden_str = "\n   🎣 ".join(info[1][:3])
    return f"✨ <b>Shiny seit:</b> {info[0]}\n   🎣 {methoden_str}"

# ──────────────────────────────────────────
#  /shiny HANDLER
# ──────────────────────────────────────────
def handle_shiny(name_or_id: str) -> None:
    resolved = resolve_name_to_id(name_or_id)
    poke = get_pokemon(resolved) or get_pokemon(name_or_id)
    if not poke:
        send_text(f"❌ Pokémon <b>{name_or_id}</b> nicht gefunden.")
        return

    poke_id   = poke["id"]
    name_de   = get_name_de(poke_id) or poke["name"].capitalize()
    name_en   = poke["name"].capitalize()
    shiny_url = (poke["sprites"]["other"]["official-artwork"]["front_shiny"]
                 or poke["sprites"]["front_shiny"])

    shiny_info = get_shiny_info(poke_id)
    text = (
        f"✨ <b>Shiny-Guide: {name_de}</b>"
        f"{f' ({name_en})' if name_de != name_en else ''}\n"
        f"────────────────────\n"
        f"{shiny_info}\n"
        f"────────────────────\n"
        f"💡 <b>Tipps:</b>\n"
        f"   • Schillernder Charme halbiert die Rate\n"
        f"   • Masuda-Methode: Ausland-Pokémon züchten\n"
        f"   • Soft Reset für legendäre Pokémon\n"
        f"   • Synchronisieren für gewünschte Natur"
    )
    if shiny_url:
        send_photo(shiny_url, text)
    else:
        send_text(text)

# ──────────────────────────────────────────
#  /meta HANDLER
# ──────────────────────────────────────────
def handle_meta(name_or_id: str) -> None:
    resolved = resolve_name_to_id(name_or_id)
    poke = get_pokemon(resolved) or get_pokemon(name_or_id)
    if not poke:
        send_text(f"❌ Pokémon <b>{name_or_id}</b> nicht gefunden.")
        return

    poke_id = poke["id"]
    name_de = get_name_de(poke_id) or poke["name"].capitalize()
    name_en = poke["name"].capitalize()
    typen   = [t["type"]["name"] for t in poke["types"]]
    stats   = {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]}
    bst     = sum(stats.values())
    tier_info = get_smogon_tier(poke["name"])

    if tier_info:
        tier, natur, evs = tier_info
        tier_erk = TIER_ERKLAERUNG.get(tier, tier)
        text = (
            f"🏆 <b>Competitive: {name_de}</b>"
            f"{f' ({name_en})' if name_de != name_en else ''}\n"
            f"────────────────────\n"
            f"{tier_erk}\n"
            f"────────────────────\n"
            f"🌿 <b>Beste Natur:</b> {natur}\n"
            f"📈 <b>EV-Verteilung:</b> {evs}\n"
            f"────────────────────\n"
            f"📊 <b>BST: {bst}</b>\n"
            + "\n".join(f"   {STAT_NAMEN.get(k, k)}: <b>{v}</b>" for k, v in stats.items()) + "\n"
            + f"────────────────────\n"
            f"🏷️ Typ: " + " | ".join(f"{TYP_EMOJI.get(t,'')}{TYP_DE.get(t,t.capitalize())}" for t in typen) + "\n"
            f"🔗 smogon.com/dex/sv/pokemon/{poke['name']}"
        )
    else:
        text = (
            f"🏆 <b>Competitive: {name_de}</b>\n"
            f"────────────────────\n"
            f"ℹ️ Kein Smogon-Tier in der Datenbank.\n"
            f"────────────────────\n"
            f"🔗 smogon.com/dex/sv/pokemon/{poke['name']}"
        )
    send_text(text)

# ──────────────────────────────────────────
#  /formen HANDLER
# ──────────────────────────────────────────
def handle_formen(name_or_id: str) -> None:
    resolved = resolve_name_to_id(name_or_id)
    poke = get_pokemon(resolved) or get_pokemon(name_or_id)
    if not poke:
        send_text(f"❌ Pokémon <b>{name_or_id}</b> nicht gefunden.")
        return

    poke_id = poke["id"]
    name_de = get_name_de(poke_id) or poke["name"].capitalize()
    name_en = poke["name"].capitalize()
    form_key = poke["name"].lower()
    formen   = FORM_VARIANTEN.get(form_key, [])

    if not formen:
        send_text(f"ℹ️ <b>{name_de}</b> hat keine bekannten regionalen Formen (Alola/Galar/Hisui).")
        return

    send_text(f"🌍 <b>Regionale Formen: {name_de}</b>\nLade {len(formen)} Form(en)...")

    for form_key_api, form_name in formen:
        fp = get_pokemon(form_key_api)
        if not fp:
            send_text(f"❌ {form_name} konnte nicht geladen werden.")
            continue

        typen    = [t["type"]["name"] for t in fp["types"]]
        typ_str  = " | ".join(f"{TYP_EMOJI.get(t,'')}{TYP_DE.get(t,t.capitalize())}" for t in typen)
        stats    = {s["stat"]["name"]: s["base_stat"] for s in fp["stats"]}
        bst      = sum(stats.values())
        stat_str = " | ".join(f"{STAT_NAMEN.get(k,k)}: {v}" for k, v in stats.items())
        bild_url = (fp.get("sprites", {}).get("other", {})
                      .get("official-artwork", {}).get("front_default", "")
                    or fp.get("sprites", {}).get("front_default", ""))

        caption = (
            f"🌍 <b>{name_de} – {form_name}</b>\n"
            f"────────────────────\n"
            f"🏷️ <b>Typ:</b> {typ_str}\n"
            f"📊 <b>BST:</b> {bst}\n{stat_str}"
        )
        if bild_url:
            send_photo(bild_url, caption)
        else:
            send_text(caption)
        time.sleep(0.5)

# ──────────────────────────────────────────
#  KARTENWERT (Pokemon TCG API – Cardmarket Preise)
# ──────────────────────────────────────────
KARTEN_CACHE: dict = {}

def get_karten_preise(name_de: str, name_en: str) -> str:
    """Holt die teuersten 5 Karten via Pokemon TCG API (Cardmarket-Preise)."""
    cache_key = name_en.lower()
    if cache_key in KARTEN_CACHE:
        return KARTEN_CACHE[cache_key]

    try:
        url = (
            f"https://api.pokemontcg.io/v2/cards"
            f"?q=name:{requests.utils.quote(name_en)}"
            f"&orderBy=-cardmarket.prices.trendPrice"
            f"&pageSize=5"
        )
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            KARTEN_CACHE[cache_key] = ""
            return ""

        data = r.json().get("data", [])
        if not data:
            KARTEN_CACHE[cache_key] = ""
            return ""

        zeilen = [f"💰 <b>Teuerste {name_de}-Karten (Cardmarket, EN, Trendpreis):</b>"]
        for card in data:
            kname    = card.get("name", "")
            nummer   = card.get("number", "?")
            gesamt   = card.get("set", {}).get("printedTotal", "?")
            set_name = card.get("set", {}).get("name", "?")
            preise   = card.get("cardmarket", {}).get("prices", {})
            preis    = preise.get("trendPrice") or preise.get("averageSellPrice")
            if preis is None:
                continue
            cm_search_name = name_de if name_de else kname
            cm_url = (
                "https://www.cardmarket.com/de/Pokemon/Products/Singles"
                "?searchString=" + requests.utils.quote(cm_search_name)
            )
            link_str = f' <a href="{cm_url}">🔗</a>'
            zeilen.append(f"   💎 {kname} {nummer}/{gesamt} [{set_name}] (EN): <b>{preis:.2f}€</b>{link_str}")

        if len(zeilen) == 1:
            KARTEN_CACHE[cache_key] = ""
            return ""

        result = "\n".join(zeilen)
        KARTEN_CACHE[cache_key] = result
        return result

    except Exception as e:
        print(f"[FEHLER] Kartenwert: {e}")
        return ""


def get_gen_debut(poke_id: int) -> str:
    if poke_id <= 151:   return "Generation I (Rot/Blau/Gelb)"
    elif poke_id <= 251: return "Generation II (Gold/Silber/Kristall)"
    elif poke_id <= 386: return "Generation III (Rubin/Saphir/Smaragd)"
    elif poke_id <= 493: return "Generation IV (Diamant/Perl/Platin)"
    elif poke_id <= 649: return "Generation V (Schwarz/Weiß)"
    elif poke_id <= 721: return "Generation VI (X/Y)"
    elif poke_id <= 809: return "Generation VII (Sonne/Mond)"
    elif poke_id <= 905: return "Generation VIII (Schwert/Schild)"
    else:                return "Generation IX (Karmesin/Purpur)"


# ──────────────────────────────────────────
#  MANUELLE FUNDORT-DB (kein PokeAPI Encounter)
# ──────────────────────────────────────────
FUNDORT_DB = {
    # Gen 9 – Paradox Pokémon (Area Zero)
    984:  "🎮 Karmesin: Area Zero (Paradox-Pokémon)",
    985:  "🎮 Purpur: Area Zero (Paradox-Pokémon)",
    986:  "🎮 Karmesin: Area Zero (Paradox-Pokémon)",
    987:  "🎮 Purpur: Area Zero (Paradox-Pokémon)",
    988:  "🎮 Karmesin: Area Zero (Paradox-Pokémon)",
    989:  "🎮 Purpur: Area Zero (Paradox-Pokémon)",
    990:  "🎮 Karmesin: Area Zero (Paradox-Pokémon)",
    991:  "🎮 Purpur: Area Zero (Paradox-Pokémon)",
    992:  "🎮 Karmesin: Area Zero (Paradox-Pokémon)",
    993:  "🎮 Purpur: Area Zero (Paradox-Pokémon)",
    994:  "🎮 Karmesin: Area Zero (Paradox-Pokémon)",
    995:  "🎮 Purpur: Area Zero (Paradox-Pokémon)",
    1005: "🎮 Karmesin: Area Zero (Paradox-Pokémon)",
    1006: "🎮 Purpur: Area Zero (Paradox-Pokémon)",
    1007: "🎮 Karmesin/Purpur: Area Zero – Koraidon/Miraidon (Starter)",
    1008: "🎮 Karmesin/Purpur: Area Zero – Koraidon/Miraidon (Starter)",
    1009: "🎮 Karmesin/Purpur: Teal Mask DLC – Ogrepon",
    1010: "🎮 Karmesin/Purpur: Indigo Disk DLC – Terapagos",
    1017: "🎮 Karmesin/Purpur: Indigo Disk DLC – Ogerpon",
    1020: "🎮 Karmesin: Area Zero (Paradox-Pokémon)",
    1021: "🎮 Purpur: Area Zero (Paradox-Pokémon)",
    1022: "🎮 Karmesin: Area Zero (Paradox-Pokémon)",
    1023: "🎮 Purpur: Area Zero (Paradox-Pokémon)",
    1024: "🎮 Karmesin: Area Zero – Gouging Fire",
    1025: "🎮 Purpur: Area Zero – Raging Bolt",
    # Legenden ohne Encounter
    144:  "🎮 Feuerrot/Blattgrün: Seafoam Islands (Arktos)",
    145:  "🎮 Feuerrot/Blattgrün: Power Plant (Zapdos)",
    146:  "🎮 Feuerrot/Blattgrün: Mt. Ember (Lavados)",
    243:  "🎮 Gold/Silber: Wildnis (Raikou – flüchtig)",
    244:  "🎮 Gold/Silber: Wildnis (Entei – flüchtig)",
    245:  "🎮 Gold/Silber: Wildnis (Suicune – flüchtig)",
    377:  "🎮 Rubin/Saphir: Felsenberg (Regirock)",
    378:  "🎮 Rubin/Saphir: Inseleishöhle (Regice)",
    379:  "🎮 Rubin/Saphir: Stahlinsel (Registeel)",
    380:  "🎮 Saphir: Himmelsturm (Latias)",
    381:  "🎮 Rubin: Himmelsturm (Latios)",
    382:  "🎮 Saphir: Meeresbodengrotte (Kyogre)",
    383:  "🎮 Rubin: Feuerhöhle (Groudon)",
    480:  "🎮 Diamant/Perl: Bekannter Turm (Uxie)",
    481:  "🎮 Diamant/Perl: Seegarten See (Mesprit – flüchtig)",
    482:  "🎮 Diamant/Perl: Seegarten See (Azelf)",
    483:  "🎮 Diamant: Orburgh Gate (Dialga)",
    484:  "🎮 Perl: Orburgh Gate (Palkia)",
    485:  "🎮 Diamant/Perl: Newmoon Island (Heatran)",
    486:  "🎮 Diamant/Perl: Einheit Turm (Regigigas)",
    487:  "🎮 Diamant/Perl: Distortion World (Giratina)",
    488:  "🎮 Diamant/Perl: Seegarten See (Cresselia – flüchtig)",
    643:  "🎮 Schwarz: N's Castle (Reshiram)",
    644:  "🎮 Weiß: N's Castle (Zekrom)",
    716:  "🎮 X: Team Flare HQ (Xerneas)",
    717:  "🎮 Y: Team Flare HQ (Yveltal)",
    718:  "🎮 X/Y: Terminus Cave (Zygarde)",
    800:  "🎮 Sonne/Mond: Altar of the Sunne/Moone (Necrozma)",
    888:  "🎮 Schwert: Energie-Kraftwerk (Zacian)",
    889:  "🎮 Schild: Energie-Kraftwerk (Zamazenta)",
    890:  "🎮 Schwert/Schild: Crown Tundra (Eternatus)",
    896:  "🎮 Schwert: Crown Tundra (Glastrier)",
    897:  "🎮 Schild: Crown Tundra (Spectrier)",
    898:  "🎮 Schwert/Schild: Crown Tundra (Calyrex)",
}

def get_fundort_manuell(poke_id: int) -> str:
    return FUNDORT_DB.get(poke_id, "")


# ──────────────────────────────────────────
#  HAUPTFUNKTION: POKÉMON INFO
# ──────────────────────────────────────────
def get_pokemon_info(name_or_id: str) -> None:
    resolved = resolve_name_to_id(name_or_id)
    send_text(f"🔍 Suche <b>{name_or_id}</b>...")

    poke = get_pokemon(resolved)
    if not poke:
        poke = get_pokemon(name_or_id)
    if not poke:
        send_text(f"❌ Pokémon <b>{name_or_id}</b> nicht gefunden.\nTipp: Englischen oder deutschen Namen verwenden.")
        return

    species = get_pokemon_species(str(poke["id"]))

    poke_id      = poke["id"]
    name_de_db   = get_name_de(poke_id)
    name_de      = name_de_db if name_de_db else (get_de_name(species) if species else poke["name"].capitalize())
    name_en      = poke["name"].capitalize()
    genus        = get_genus(species) if species else ""
    typen        = [t["type"]["name"] for t in poke["types"]]
    gewicht      = poke["weight"] / 10
    groesse      = poke["height"] / 10
    bild_url     = (poke["sprites"]["other"]["official-artwork"]["front_default"]
                    or poke["sprites"]["front_default"])
    shiny_url    = (poke["sprites"]["other"]["official-artwork"]["front_shiny"]
                    or poke["sprites"]["front_shiny"])
    catch_rate   = species.get("capture_rate", 0) if species else 0
    is_legendary = species.get("is_legendary", False) if species else False
    is_mythical  = species.get("is_mythical", False) if species else False

    stats = {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]}
    bst   = sum(stats.values())

    abilities = []
    for a in poke["abilities"]:
        name_a = get_ability_name_de(a["ability"]["name"])
        abilities.append(f"{name_a} (HA)" if a["is_hidden"] else name_a)

    effekte   = berechne_effektivitaet(typen)
    schwach   = {t: m for t, m in effekte.items() if m > 1}
    resistent = {t: m for t, m in effekte.items() if 0 < m < 1}
    immun     = {t: m for t, m in effekte.items() if m == 0}

    evo_chain  = get_evolution_chain(species) if species else ""
    poke_text  = get_de_text(species) if species else ""
    shiny_info = get_shiny_info(poke_id)

    # Level-Up Moves (erste 10, deutsche Namen)
    # Moves: niedrigsten Level pro Move nehmen (vermeidet Duplikate durch verschiedene Spielversionen)
    moves_dict = {}
    for m in poke.get("moves", []):
        move_name = m["move"]["name"]
        for vd in m.get("version_group_details", []):
            if vd.get("move_learn_method", {}).get("name") == "level-up":
                lvl = vd.get("level_learned_at", 0)
                if move_name not in moves_dict or lvl < moves_dict[move_name]:
                    moves_dict[move_name] = lvl
    moves_levelup = sorted(moves_dict.items(), key=lambda x: x[1])[:10]
    moves_levelup = [(lvl, name) for name, lvl in moves_levelup]
    # Deutsche Namen holen (mit Cache)
    moves_levelup_de = [(lvl, get_move_name_de(name)) for lvl, name in moves_levelup]

    enc_data = api_get(f"{POKE_API}/pokemon/{poke_id}/encounters")
    fang_kurz, fang_voll, fang_anzahl = beste_fangmethode(enc_data, catch_rate)
    # Fallback: manuelle Fundort-DB
    if fang_anzahl == 0:
        manuell = get_fundort_manuell(poke_id)
        if manuell:
            fang_kurz = "🎯 <b>Fundort:</b>\n   " + manuell
            fang_voll = fang_kurz
    FANG_CACHE[str(poke_id)] = fang_voll

    # Competitive
    tier_info = get_smogon_tier(poke["name"])
    if tier_info:
        tier, natur, evs = tier_info
        tier_str = f"🏆 {TIER_ERKLAERUNG.get(tier, tier)}\n   🌿 {natur} | 📈 {evs}"
    else:
        tier_str = ""

    # Generations-Debüt
    gen_debut = get_gen_debut(poke_id)

    # ROM-Hack
    romhack_str = get_romhack_info(poke_id)

    # Kartenwert
    karten_str = get_karten_preise(name_de, poke["name"])

    # Formen-Hinweis
    hat_formen = poke["name"].lower() in FORM_VARIANTEN
    formen_hinweis = f"\n🌍 Regionale Formen → /formen {name_de}" if hat_formen else ""

    flag = ""
    if is_legendary: flag = "⭐ Legendär"
    if is_mythical:  flag = "✨ Mysteriös"

    typ_str  = " | ".join(f"{TYP_EMOJI.get(t,'')}{TYP_DE.get(t,t.capitalize())}" for t in typen)
    stat_str = "\n".join(f"   {STAT_NAMEN.get(k,k)}: <b>{v}</b>" for k, v in stats.items())

    def fmt_typen(typ_dict, mult):
        return " ".join(
            f"{TYP_EMOJI.get(t,'')}{TYP_DE.get(t,t)}(×{int(m) if m==int(m) else m})"
            for t, m in sorted(typ_dict.items(), key=lambda x: -x[1]) if m == mult
        )

    schwach_4x  = fmt_typen({t: m for t, m in schwach.items() if m >= 4}, 4)
    schwach_2x  = fmt_typen({t: m for t, m in schwach.items() if m == 2}, 2)
    resist_half = fmt_typen({t: m for t, m in resistent.items() if m == 0.5}, 0.5)
    resist_qrt  = fmt_typen({t: m for t, m in resistent.items() if m == 0.25}, 0.25)
    immun_str   = " ".join(f"{TYP_EMOJI.get(t,'')}{TYP_DE.get(t,t)}" for t in immun)

    caption = (
        f"{'⭐ ' if is_legendary else '✨ ' if is_mythical else ''}#{poke_id:03d} <b>{name_de}</b>"
        f"{f' ({name_en})' if name_de != name_en else ''}\n"
        f"{f'📖 {genus}' if genus else ''}{f' | {flag}' if flag else ''}\n"
        f"────────────────────\n"
        f"🏷️ <b>Typ:</b> {typ_str}\n"
        f"📏 {groesse}m | ⚖️ {gewicht}kg | 🎯 Fangrate: {catch_rate}/255\n"
        f"────────────────────\n"
        f"<b>📊 Stats</b> (BST: {bst})\n{stat_str}\n"
        f"────────────────────\n"
        f"<b>⚔️ Typ-Matchup</b>\n"
        + (f"🔴 ×4: {schwach_4x}\n" if schwach_4x else "")
        + (f"🟠 ×2: {schwach_2x}\n" if schwach_2x else "")
        + (f"🟢 ×½: {resist_half}\n" if resist_half else "")
        + (f"🔵 ×¼: {resist_qrt}\n" if resist_qrt else "")
        + (f"⚪ Immun: {immun_str}\n" if immun_str else "")
        + f"────────────────────\n"
        f"💪 <b>Fähigkeiten:</b> {' | '.join(abilities)}\n"
        + (f"🔗 <b>Entwicklung:</b> {evo_chain}\n" if evo_chain else "")
        + f"🌍 <b>Debüt:</b> {gen_debut}\n"
        + f"{shiny_info}\n"
        + (f"────────────────────\n{tier_str}\n" if tier_str else "")
        + f"────────────────────\n"
        f"{fang_kurz}\n"
        + (f"────────────────────\n{romhack_str}\n" if romhack_str else "")
        + (f"────────────────────\n{karten_str}\n" if karten_str else "")
        + (f"────────────────────\n⚡ <b>Attacken (Level-Up):</b>\n"
           + "\n".join(f"   Lvl {lvl}: {name}" for lvl, name in moves_levelup_de) + "\n"
           if moves_levelup_de else "")
        + (f"────────────────────\n📖 <i>{poke_text[:250]}</i>" if poke_text else "")
        + formen_hinweis
    )

    if fang_anzahl > 3:
        btn_label = f"📋 Alle {fang_anzahl} Spiele anzeigen"
        cb_data   = f"fang_{poke_id}"
        if bild_url:
            send_photo_with_button(bild_url, caption, btn_label, cb_data)
        else:
            send_text_with_button(caption, btn_label, cb_data)
    else:
        if bild_url:
            send_photo(bild_url, caption)
        else:
            send_text(caption)


# ──────────────────────────────────────────
#  /odds – SHINY WAHRSCHEINLICHKEITS-RECHNER
# ──────────────────────────────────────────
def handle_odds(args: str) -> None:
    import math
    parts = args.strip().split()
    try:
        encounters = int(parts[0])
    except (ValueError, IndexError):
        send_text("❌ Nutzung: /odds 500\nBeispiel: /odds 1000")
        return

    def prob(rate, n):
        return (1 - (1 - 1/rate) ** n) * 100

    methoden = [
        ("Zufallsbegegnung (Gen 1-5)", 8192),
        ("Masuda-Methode (Gen 4)",      1639),
        ("Masuda-Methode (Gen 5)",      1365),
        ("Masuda + Charme (Gen 6+)",     512),
        ("SOS-Kette 70+ (Gen 7)",        315),
        ("Massenausbruch 60+ (Gen 9)",   100),
        ("Overworld 500 Kämpfe (Gen 8)", 100),
    ]

    zeilen = ["🎲 <b>Shiny-Chancen nach " + str(encounters) + " Encounters:</b>\n"]
    for name, rate in methoden:
        p = prob(rate, encounters)
        bar_filled = int(p / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        zeilen.append("<b>" + name + "</b>\n   Rate: 1/" + str(rate) + " | Chance: " + f"{p:.1f}" + "%\n   [" + bar + "]\n")

    zeilen.append("────────────────────")
    zeilen.append("📊 <b>Encounters für Wahrscheinlichkeit:</b>")
    for name, rate in [("Zuffall (1/8192)", 8192), ("Masuda+Charme (1/512)", 512), ("Ausbruch (1/100)", 100)]:
        n50 = math.ceil(math.log(0.5)  / math.log(1 - 1/rate))
        n90 = math.ceil(math.log(0.1)  / math.log(1 - 1/rate))
        n99 = math.ceil(math.log(0.01) / math.log(1 - 1/rate))
        zeilen.append("<b>" + name + ":</b> 50%=" + f"{n50:,}" + " | 90%=" + f"{n90:,}" + " | 99%=" + f"{n99:,}")

    send_text("\n".join(zeilen))


# ──────────────────────────────────────────
#  /vergleich – POKÉMON VERGLEICH
# ──────────────────────────────────────────
def handle_vergleich(args: str) -> None:
    parts = [p.strip() for p in args.strip().split(",") if p.strip()]
    if len(parts) < 2:
        send_text("❌ Nutzung: /vergleich Glurak,Nachtara")
        return
    if len(parts) > 2:
        send_text("❌ /vergleich erwartet genau 2 Pokémon. Beispiel: /vergleich Glurak,Bisaflor")
        return

    name1, name2 = parts[0], parts[1]
    poke1 = get_pokemon(resolve_name_to_id(name1)) or get_pokemon(name1)
    poke2 = get_pokemon(resolve_name_to_id(name2)) or get_pokemon(name2)

    if not poke1:
        send_text("❌ Pokémon <b>" + name1 + "</b> nicht gefunden.")
        return
    if not poke2:
        send_text("❌ Pokémon <b>" + name2 + "</b> nicht gefunden.")
        return

    id1  = poke1["id"]
    id2  = poke2["id"]
    nde1 = get_name_de(id1) or poke1["name"].capitalize()
    nde2 = get_name_de(id2) or poke2["name"].capitalize()

    stats1 = {s["stat"]["name"]: s["base_stat"] for s in poke1["stats"]}
    stats2 = {s["stat"]["name"]: s["base_stat"] for s in poke2["stats"]}
    bst1   = sum(stats1.values())
    bst2   = sum(stats2.values())

    typen1 = [t["type"]["name"] for t in poke1["types"]]
    typen2 = [t["type"]["name"] for t in poke2["types"]]
    typ1   = " ".join(TYP_EMOJI.get(t, "") + TYP_DE.get(t, t) for t in typen1)
    typ2   = " ".join(TYP_EMOJI.get(t, "") + TYP_DE.get(t, t) for t in typen2)

    tier1  = get_smogon_tier(poke1["name"])
    tier2  = get_smogon_tier(poke2["name"])
    tier1s = tier1[0] if tier1 else "?"
    tier2s = tier2[0] if tier2 else "?"

    def w(v1, v2):
        if v1 > v2: return "⬅️"
        if v2 > v1: return "➡️"
        return "🟰"

    stat_keys = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]

    zeilen = [
        "⚔️ <b>Vergleich: " + nde1 + " vs " + nde2 + "</b>\n",
        "🏷️ Typ:    " + typ1 + "  vs  " + typ2,
        "🏆 Tier:   " + tier1s + "  vs  " + tier2s,
        "📊 BST:    " + str(bst1) + "  vs  " + str(bst2) + "  " + w(bst1, bst2),
        "────────────────────",
    ]

    for key in stat_keys:
        v1 = stats1.get(key, 0)
        v2 = stats2.get(key, 0)
        label = STAT_NAMEN.get(key, key)
        zeilen.append(label + ": " + str(v1) + "  vs  " + str(v2) + "  " + w(v1, v2))

    wins1 = sum(1 for k in stat_keys if stats1.get(k, 0) > stats2.get(k, 0))
    wins2 = sum(1 for k in stat_keys if stats2.get(k, 0) > stats1.get(k, 0))
    zeilen.append("────────────────────")
    if wins1 > wins2:
        zeilen.append("🏆 <b>" + nde1 + "</b> gewinnt " + str(wins1) + " von " + str(len(stat_keys)) + " Stats!")
    elif wins2 > wins1:
        zeilen.append("🏆 <b>" + nde2 + "</b> gewinnt " + str(wins2) + " von " + str(len(stat_keys)) + " Stats!")
    else:
        zeilen.append("🟰 Unentschieden! (" + str(wins1) + " Stats je)")

    send_text("\n".join(zeilen))


# ──────────────────────────────────────────
#  /romhack – UMGEKEHRTE SUCHE + INFO
# ──────────────────────────────────────────
HACK_INFO_DB = {
    "radical red": {
        "name":        "🔥 Pokémon Radical Red",
        "base":        "FireRed",
        "region":      "Kanto",
        "pokemon":     "1023+",
        "besonderheiten": [
            "Hard Mode & Competitive-fokussiert",
            "Verbesserte KI & Trainer-Teams",
            "Physical/Special Split",
            "Mega Evolution, Dynamax",
            "Alle Gen 1–9 Pokémon fangbar",
        ],
        "empfehlung":  "Erfahrene Spieler / Nuzlocke",
    },
    "unbound": {
        "name":        "🌍 Pokémon Unbound",
        "base":        "FireRed",
        "region":      "Borrius (custom)",
        "pokemon":     "905",
        "besonderheiten": [
            "Tiefe Story & Missionen-System",
            "Schwierigkeitsgrade wählbar",
            "Mega Evolution, Gen 1–7+",
            "Eigene Region mit Lore",
            "Post-Game & Side-Quests",
        ],
        "empfehlung":  "Alle Spieler – Story + Action",
    },
    "glazed": {
        "name":        "🌿 Pokémon Glazed",
        "base":        "Emerald",
        "region":      "Tunod + Johto + Rankor",
        "pokemon":     "~390",
        "besonderheiten": [
            "3 Regionen in einem Spiel",
            "Fairy Type & Physical/Special Split",
            "Dream World Pokémon",
            "Trainer Rematches & Legendäre",
            "Riesiges Post-Game",
        ],
        "empfehlung":  "Alle Spieler – Umfang & Story",
    },
    "gaia": {
        "name":        "🗿 Pokémon Gaia",
        "base":        "FireRed",
        "region":      "Orbtus (custom)",
        "pokemon":     "~500",
        "besonderheiten": [
            "Starke Story – antike Zivilisation",
            "Physical/Special Split",
            "Mega Evolution bis Gen 6",
            "Neue Moves & Fähigkeiten",
            "Sehr poliertes Spielgefühl",
        ],
        "empfehlung":  "Alle Spieler – Story-fokussiert",
    },
    "vega": {
        "name":        "👾 Pokémon Vega",
        "base":        "FireRed",
        "region":      "Hoenn-ähnlich",
        "pokemon":     "Fakemon (custom)",
        "besonderheiten": [
            "Eigene Fakemon – keine Original-Pokémon",
            "Extreme Schwierigkeit",
            "Riesiges Post-Game",
            "Einzigartiges Spielerlebnis",
        ],
        "empfehlung":  "Erfahrene Spieler – Herausforderung",
    },
    "clover": {
        "name":        "🤡 Pokémon Clover",
        "base":        "FireRed",
        "region":      "Fochun (custom)",
        "pokemon":     "386 Fakemon",
        "besonderheiten": [
            "386 komplett eigene Fakemon",
            "Internet-Kultur & Meme-Humor",
            "Komplett eigene Story",
            "Überraschend hohe Qualität",
        ],
        "empfehlung":  "Humor-Liebhaber & Fakemon-Fans",
    },
    "snakewood": {
        "name":        "🧟 Pokémon Snakewood",
        "base":        "Ruby",
        "region":      "Hoenn (Zombie-Apokalypse)",
        "pokemon":     "~80",
        "besonderheiten": [
            "Zombie-Horror Setting in Hoenn",
            "Sehr dunkle & ungewöhnliche Story",
            "Cult Classic – einmalig",
            "Wenige Pokémon verfügbar",
        ],
        "empfehlung":  "Horror/Story-Fans – kurzes Abenteuer",
    },
    "liquid crystal": {
        "name":        "💎 Pokémon Liquid Crystal",
        "base":        "FireRed",
        "region":      "Johto + Kanto",
        "pokemon":     "Alle Johto + Kanto",
        "besonderheiten": [
            "GBA Remake von Pokémon Crystal",
            "Alle Johto + Kanto Events",
            "Animé-inspirierte Szenen",
            "Sehr originalgetreue Umsetzung",
        ],
        "empfehlung":  "Nostalgie-Fans & Johto-Liebhaber",
    },
    "dark rising": {
        "name":        "🌑 Pokémon Dark Rising",
        "base":        "FireRed",
        "region":      "Core (custom)",
        "pokemon":     "386",
        "besonderheiten": [
            "Schwere Schwierigkeit + Story",
            "Drachen-fokussierte Handlung",
            "Pokémon bis Gen 5",
            "Intensives Story-Erlebnis",
        ],
        "empfehlung":  "Drachen-Fans & Story-Spieler",
    },
    "emerald crest": {
        "name":        "🌈 Pokémon Emerald Crest",
        "base":        "Emerald",
        "region":      "Hoenn",
        "pokemon":     "Alle 1025",
        "besonderheiten": [
            "ALLE 1025 Pokémon fangbar",
            "27 Starter zur Auswahl",
            "Open World",
            "Gen 9 Pokémon integriert",
            "Maximale Freiheit",
        ],
        "empfehlung":  "Sammler & Komplettisten",
    },
    "crown": {
        "name":        "🃏 Pokémon Crown",
        "base":        "FireRed",
        "region":      "Medieval custom",
        "pokemon":     "~210",
        "besonderheiten": [
            "Mittelalterliches Setting",
            "Auto-Battler Kampfsystem",
            "Quests & Boss-Kämpfe",
            "Komplett eigene Mechaniken",
        ],
        "empfehlung":  "Experimentierfreudige Spieler",
    },
    "phoenix rising": {
        "name":        "🦅 Pokémon Phoenix Rising",
        "base":        "RPG Maker",
        "region":      "Hawthorne (custom)",
        "pokemon":     "200+",
        "besonderheiten": [
            "Choices & Consequences System",
            "Mega & Relic Evolution",
            "Episodisches Storytelling",
            "Noch in Entwicklung (unfertig)",
            "Sehr cineastische Präsentation",
        ],
        "empfehlung":  "Story-Fans – beachte: unfertig",
    },
    "reborn": {
        "name":        "🌊 Pokémon Reborn",
        "base":        "RPG Maker",
        "region":      "Reborn City",
        "pokemon":     "800+",
        "besonderheiten": [
            "18 Gyms – einer pro Typ",
            "Dunkle Story, Erwachsenenthemen",
            "Feldeffekte verändern Kämpfe",
            "800+ Pokémon verfügbar",
            "Sehr umfangreich & schwer",
        ],
        "empfehlung":  "Erfahrene Spieler – episches Spiel",
    },
    "prism": {
        "name":        "💠 Pokémon Prism",
        "base":        "Gold (Game Boy Color)",
        "region":      "Naljo + Rijon",
        "pokemon":     "253",
        "besonderheiten": [
            "Neue Typen: Gas, Sound, Crystal",
            "Mining Minispiel",
            "Zwei eigene Regionen",
            "Auf dem Game Boy Color!",
        ],
        "empfehlung":  "Retro-Fans & Entdecker",
    },
    "storm silver": {
        "name":        "⚔️ Pokémon Storm Silver / Sacred Gold",
        "base":        "Soul Silver / Heart Gold",
        "region":      "Johto + Kanto",
        "pokemon":     "493",
        "besonderheiten": [
            "ALLE 493 Pokémon ohne Trading fangbar",
            "Schwerere Trainer-Teams",
            "Distributiondaten integriert",
            "Perfekte Johto-Erfahrung",
        ],
        "empfehlung":  "Johto-Fans & Perfektionisten",
    },
    "sacred gold": {
        "name":        "⚔️ Pokémon Storm Silver / Sacred Gold",
        "base":        "Soul Silver / Heart Gold",
        "region":      "Johto + Kanto",
        "pokemon":     "493",
        "besonderheiten": [
            "ALLE 493 Pokémon ohne Trading fangbar",
            "Schwerere Trainer-Teams",
            "Distributiondaten integriert",
            "Perfekte Johto-Erfahrung",
        ],
        "empfehlung":  "Johto-Fans & Perfektionisten",
    },
    "emerald kaizo": {
        "name":        "🌋 Pokémon Emerald Kaizo",
        "base":        "Emerald",
        "region":      "Hoenn",
        "pokemon":     "~350",
        "besonderheiten": [
            "Extreme Nuzlocke-Challenge",
            "Kaum Items nutzbar",
            "Boss-Kämpfe extrem schwer",
            "Für Hardcore-Spieler",
        ],
        "empfehlung":  "Hardcore-Nuzlocker",
    },
    "emerald rogue": {
        "name":        "🌿 Pokémon Emerald Rogue",
        "base":        "Emerald",
        "region":      "Hoenn",
        "pokemon":     "~400",
        "besonderheiten": [
            "Roguelike – jeder Run anders",
            "Zufällige Routen & Items",
            "Endlos-Replayvalue",
            "Permanenter Tod möglich",
        ],
        "empfehlung":  "Roguelike-Fans & Wiederspielwert",
    },
}

# Cache für romhack vollständige Listen
ROMHACK_CACHE: dict = {}

def handle_romhack(args: str) -> None:
    hack_suche = args.strip().lower()
    if not hack_suche:
        verfuegbar = (
            "Radical Red, Unbound, Glazed, Gaia, Vega, Clover,\n"
            "Snakewood, Liquid Crystal, Dark Rising, Emerald Crest,\n"
            "Crown, Phoenix Rising, Reborn, Prism,\n"
            "Storm Silver, Sacred Gold, Emerald Kaizo, Emerald Rogue"
        )
        send_text("❌ Nutzung: /romhack Unbound\n\n🕹️ <b>Verfügbare Hacks:</b>\n" + verfuegbar)
        return

    # Info-Karte aus HACK_INFO_DB suchen
    info = None
    for key, val in HACK_INFO_DB.items():
        if hack_suche in key or key in hack_suche:
            info = val
            break

    # Pokémon-Treffer aus ROMHACK_DB
    treffer = []
    hack_name_display = args.strip()
    for poke_id, hacks in ROMHACK_DB.items():
        for hack_name, hinweis in hacks:
            if hack_suche in hack_name.lower():
                hack_name_display = hack_name
                name_de = get_name_de(poke_id)
                treffer.append((poke_id, name_de or str(poke_id), hinweis))

    # Info-Karte senden wenn gefunden
    if info:
        zeilen = [
            info["name"] + "\n",
            "━━━━━━━━━━━━━━━━━━━━",
            "🎮 <b>Base:</b> " + info["base"],
            "🗺️ <b>Region:</b> " + info["region"],
            "📊 <b>Pokémon:</b> " + info["pokemon"],
            "━━━━━━━━━━━━━━━━━━━━",
            "⭐ <b>Besonderheiten:</b>",
        ]
        for b in info["besonderheiten"]:
            zeilen.append("   • " + b)
        zeilen.append("━━━━━━━━━━━━━━━━━━━━")
        zeilen.append("👤 <b>Empfehlung:</b> " + info["empfehlung"])
        send_text("\n".join(zeilen))

    if not treffer:
        if not info:
            verfuegbar = (
                "Radical Red, Unbound, Glazed, Gaia, Vega, Clover,\n"
                "Snakewood, Liquid Crystal, Dark Rising, Emerald Crest,\n"
                "Crown, Phoenix Rising, Reborn, Prism,\n"
                "Storm Silver, Sacred Gold, Emerald Kaizo, Emerald Rogue"
            )
            send_text("❌ <b>" + args.strip() + "</b> nicht gefunden.\n\n🕹️ <b>Verfügbare Hacks:</b>\n" + verfuegbar)
        return

    treffer = sorted(treffer, key=lambda x: x[0])
    gesamt = len(treffer)

    # Generationen zählen
    def gen_von_id(pid):
        if pid <= 151:   return 1
        elif pid <= 251: return 2
        elif pid <= 386: return 3
        elif pid <= 493: return 4
        elif pid <= 649: return 5
        elif pid <= 721: return 6
        elif pid <= 809: return 7
        elif pid <= 905: return 8
        else:            return 9

    gens = sorted(set(gen_von_id(p) for p, _, _ in treffer))
    gen_str = "Gen " + "/".join(str(g) for g in gens)

    # Vollständige Liste für Cache
    alle_zeilen = ["🕹️ <b>Alle " + str(gesamt) + " Pokémon in " + hack_name_display + ":</b>\n"]
    for poke_id, name, hinweis in treffer:
        alle_zeilen.append("   #" + f"{poke_id:03d}" + " " + name + ": " + hinweis)
    voll_text = "\n".join(alle_zeilen)
    cache_key = "romhack_" + hack_suche
    ROMHACK_CACHE[cache_key] = voll_text

    # Beispiele: erste 3
    beispiele = ", ".join(n for _, n, _ in treffer[:3])
    if gesamt > 3:
        beispiele += "..."

    # Pokémon-Button nur wenn Info-Karte vorhanden, sonst kurze Zusammenfassung
    if info:
        if gesamt > 0:
            send_text_with_button(
                "🔍 <b>Beispiele:</b> " + beispiele,
                "📋 Alle " + str(gesamt) + " Pokémon in DB anzeigen",
                cache_key
            )
    else:
        kurz = (
            "🕹️ <b>Pokémon in " + hack_name_display + ":</b>\n"
            "📊 " + str(gesamt) + " Einträge in DB (" + gen_str + ")\n"
            "🔍 Beispiele: " + beispiele
        )
        if gesamt > 3:
            send_text_with_button(kurz, "📋 Alle " + str(gesamt) + " Pokémon anzeigen", cache_key)
        else:
            send_text(kurz)


# ──────────────────────────────────────────
#  /team – TEAM-ANALYSE
# ──────────────────────────────────────────
def handle_team(args: str) -> None:
    namen = [n.strip() for n in args.strip().split(",") if n.strip()]
    if len(namen) < 2:
        send_text("❌ Nutzung: /team Glurak,Nachtara,Mewtu\nMin. 2, max. 6 Pokémon")
        return
    if len(namen) > 6:
        namen = namen[:6]

    send_text("🔍 Analysiere Team...")

    team = []
    for name in namen:
        resolved = resolve_name_to_id(name)
        poke = get_pokemon(resolved) or get_pokemon(name)
        if not poke:
            send_text("❌ <b>" + name + "</b> nicht gefunden, wird übersprungen.")
            continue
        pid   = poke["id"]
        nde   = get_name_de(pid) or poke["name"].capitalize()
        typen = [t["type"]["name"] for t in poke["types"]]
        stats = {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]}
        tier  = get_smogon_tier(poke["name"])
        team.append({"name": nde, "typen": typen, "stats": stats, "tier": tier})

    if not team:
        send_text("❌ Kein gültiges Pokémon gefunden.")
        return

    # Team-Schwächen berechnen
    team_schwaechen = {}
    team_resistenzen = {}
    for mitglied in team:
        effekte = berechne_effektivitaet(mitglied["typen"])
        for typ, mult in effekte.items():
            if mult > 1:
                team_schwaechen[typ] = team_schwaechen.get(typ, 0) + 1
            elif mult < 1:
                team_resistenzen[typ] = team_resistenzen.get(typ, 0) + 1

    # Stärkste Schwächen (3+ Mitglieder betroffen)
    kritisch = {t: n for t, n in team_schwaechen.items() if n >= 2}
    gut_gedeckt = {t: n for t, n in team_resistenzen.items() if n >= 2}

    # Bestes Stat je Kategorie
    bester_speed  = max(team, key=lambda x: x["stats"].get("speed", 0))
    bester_angriff = max(team, key=lambda x: x["stats"].get("attack", 0) + x["stats"].get("special-attack", 0))
    bester_tank   = max(team, key=lambda x: x["stats"].get("hp", 0) + x["stats"].get("defense", 0) + x["stats"].get("special-defense", 0))

    # Ausgabe bauen
    zeilen = ["⚔️ <b>Team-Analyse</b>\n"]

    # Mitglieder
    zeilen.append("👥 <b>Team:</b>")
    for m in team:
        typ_str = " ".join(TYP_EMOJI.get(t, "") + TYP_DE.get(t, t) for t in m["typen"])
        tier_str = " [" + m["tier"][0] + "]" if m["tier"] else ""
        zeilen.append("   • " + m["name"] + tier_str + " – " + typ_str)

    zeilen.append("\n────────────────────")

    # Schwächen
    if kritisch:
        schwach_str = " ".join(
            TYP_EMOJI.get(t, "") + TYP_DE.get(t, t) + "(" + str(n) + "x)"
            for t, n in sorted(kritisch.items(), key=lambda x: -x[1])
        )
        zeilen.append("⚠️ <b>Teamweite Schwächen:</b>\n   " + schwach_str)
    else:
        zeilen.append("✅ Keine kritischen Teamschwächen!")

    # Resistenzen
    if gut_gedeckt:
        resist_str = " ".join(
            TYP_EMOJI.get(t, "") + TYP_DE.get(t, t)
            for t in sorted(gut_gedeckt.keys())
        )
        zeilen.append("🛡️ <b>Gut gedeckt gegen:</b>\n   " + resist_str)

    zeilen.append("\n────────────────────")

    # Rollen
    zeilen.append("🎯 <b>Rollen im Team:</b>")
    zeilen.append("   ⚡ Schnellstes: " + bester_speed["name"] + " (" + str(bester_speed["stats"].get("speed", 0)) + " INIT)")
    zeilen.append("   ⚔️ Stärkster Angreifer: " + bester_angriff["name"])
    zeilen.append("   🛡️ Bester Tank: " + bester_tank["name"])

    # Tier-Übersicht
    tier_uebersicht = [m["name"] + " [" + m["tier"][0] + "]" for m in team if m["tier"]]
    if tier_uebersicht:
        zeilen.append("\n🏆 <b>Competitive Tier:</b>\n   " + " | ".join(tier_uebersicht))

    send_text("\n".join(zeilen))


# ──────────────────────────────────────────
#  GENERATIONS-LISTE
# ──────────────────────────────────────────
def get_gen_liste(gen: str) -> None:
    if gen not in GENERATIONEN:
        send_text("❌ Unbekannte Generation. Verfügbar: /gen1 bis /gen9")
        return

    start, end, region, emoji = GENERATIONEN[gen]
    send_text(f"{emoji} <b>Generation {gen[-1]} – {region}</b>\nLade {end - start + 1} Pokémon...")

    data = api_get(f"{POKE_API}/pokemon?limit={end - start + 1}&offset={start - 1}")
    if not data:
        send_text("❌ Fehler beim Laden der Liste.")
        return

    lines = []
    for i, p in enumerate(data.get("results", []), start):
        name_de = get_name_de(i)
        lines.append(f"#{i:03d} {name_de if name_de else p['name'].capitalize()}")

    chunk = 50
    for i in range(0, len(lines), chunk):
        block = "\n".join(lines[i:i+chunk])
        send_text(f"{emoji} <b>{region} #{i+start:03d}–#{min(i+start+chunk-1, end):03d}</b>\n{block}")
        time.sleep(0.5)


# ──────────────────────────────────────────
#  HAUPTSCHLEIFE
# ──────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] JensPokedexBot gestartet.")
    send_text(
        "🎮 <b>JensPokedexBot v2 – Online!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📖 <b>Suche:</b>\n"
        "   Name: <code>Glurak</code> oder <code>Charizard</code>\n"
        "   Nummer: <code>6</code> oder <code>#006</code>\n"
        "   Generation: <code>/gen1</code> bis <code>/gen9</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ <b>Spezial-Befehle:</b>\n"
        "   /shiny Glurak – Shiny-Hunting Guide\n"
        "   /meta Glurak – Competitive Tier + EVs\n"
        "   /formen Glurak – Alola/Galar/Hisui Formen\n"
        "   /odds 500 – Shiny-Wahrscheinlichkeit\n"
        "   /vergleich Glurak,Nachtara – Vergleich\n"
        "   /team Glurak,Mewtu,Nachtara – Team-Analyse\n"
        "   /romhack Unbound – ROM-Hack Pokémon\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Tipp: Deutsche + englische Namen funktionieren!</i>"
    )

    last_update_id = 0

    while True:
        try:
            updates = get_updates(last_update_id + 1)

            for update in updates:
                last_update_id = update["update_id"]

                # Callback Query (Inline-Button geklickt)
                cb = update.get("callback_query", {})
                if cb:
                    answer_callback(cb["id"])
                    cb_data = cb.get("data", "")
                    if cb_data.startswith("fang_"):
                        poke_id_str = cb_data[5:]
                        if poke_id_str in FANG_CACHE:
                            send_text(FANG_CACHE[poke_id_str])
                        else:
                            send_text("❌ Daten nicht mehr im Cache. Bitte Pokémon erneut suchen.")
                    elif cb_data.startswith("romhack_"):
                        if cb_data in ROMHACK_CACHE:
                            send_text(ROMHACK_CACHE[cb_data])
                        else:
                            send_text("❌ Cache abgelaufen. Bitte /romhack erneut eingeben.")
                    continue

                msg = update.get("message", {})
                if not msg:
                    continue
                if msg.get("chat", {}).get("id") != CHAT_ID:
                    continue

                text     = msg.get("text", "").strip()
                text_low = text.lower()
                ts       = datetime.now().strftime("%H:%M:%S")
                print(f"[{ts}] Empfangen: '{text}'")

                # Generations-Befehle (/gen1 oder gen1)
                if text_low.lstrip("/") in GENERATIONEN:
                    threading.Thread(target=get_gen_liste, args=(text_low.lstrip("/"),), daemon=True).start()

                # /shiny <name>
                elif text_low.startswith("/shiny "):
                    arg = text[7:].strip()
                    threading.Thread(target=handle_shiny, args=(arg,), daemon=True).start()

                # /meta <name>
                elif text_low.startswith("/meta "):
                    arg = text[6:].strip()
                    threading.Thread(target=handle_meta, args=(arg,), daemon=True).start()

                # /formen <name>
                elif text_low.startswith("/formen "):
                    arg = text[8:].strip()
                    threading.Thread(target=handle_formen, args=(arg,), daemon=True).start()

                # /romhack <hack>
                elif text_low.startswith("/romhack "):
                    arg = text[9:].strip()
                    threading.Thread(target=handle_romhack, args=(arg,), daemon=True).start()

                # /team <n1> <n2> ...
                elif text_low.startswith("/team "):
                    arg = text[6:].strip()
                    threading.Thread(target=handle_team, args=(arg,), daemon=True).start()

                # /odds <n>
                elif text_low.startswith("/odds"):
                    arg = text[5:].strip()
                    threading.Thread(target=handle_odds, args=(arg,), daemon=True).start()

                # /vergleich <n1> <n2>
                elif text_low.startswith("/vergleich "):
                    arg = text[11:].strip()
                    threading.Thread(target=handle_vergleich, args=(arg,), daemon=True).start()

                # Hilfe
                elif text_low in ["/hilfe", "/help", "/start"]:
                    send_text(
                        "🎮 <b>JensPokedexBot – Befehle</b>\n\n"
                        "📋 <b>Generationen:</b>\n"
                        "/gen1 – Kanto (1-151)\n"
                        "/gen2 – Johto (152-251)\n"
                        "/gen3 – Hoenn (252-386)\n"
                        "/gen4 – Sinnoh (387-493)\n"
                        "/gen5 – Unova (494-649)\n"
                        "/gen6 – Kalos (650-721)\n"
                        "/gen7 – Alola (722-809)\n"
                        "/gen8 – Galar (810-905)\n"
                        "/gen9 – Paldea (906-1025)\n\n"
                        "🔍 <b>Pokémon suchen:</b>\n"
                        "Name: <code>Glurak</code> oder <code>Charizard</code>\n"
                        "Nummer: <code>#006</code> oder <code>6</code>\n\n"
                        "⚙️ <b>Spezial-Befehle:</b>\n"
                        "/shiny Glurak – Shiny-Hunting Guide\n"
                        "/meta Glurak – Competitive Tier + Natur\n"
                        "/formen Glurak – Alola/Galar/Hisui Formen\n"
                        "/odds 500 – Shiny-Wahrscheinlichkeit\n"
                        "/vergleich Glurak,Nachtara – Pokémon vergleichen\n"
                        "/team Glurak,Mewtu,Nachtara – Team-Analyse\n"
                        "/romhack Unbound – Pokémon im ROM-Hack"
                    )

                # Nummer mit #
                elif text.startswith("#") and text[1:].isdigit():
                    threading.Thread(target=get_pokemon_info, args=(text[1:],), daemon=True).start()

                # Reine Zahl
                elif text.isdigit():
                    threading.Thread(target=get_pokemon_info, args=(text,), daemon=True).start()

                # Pokémon Name (kein / Befehl)
                elif not text.startswith("/") and len(text) >= 3:
                    threading.Thread(target=get_pokemon_info, args=(text,), daemon=True).start()

            time.sleep(POLL_SEC)

        except KeyboardInterrupt:
            print("\nService gestoppt.")
            break
        except Exception as e:
            print(f"[FEHLER] {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()