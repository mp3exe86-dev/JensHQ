"""
jobfinder_agent.py – v6
══════════════════════════════════════════════════════════════
Kein Selenium mehr! Nur APIs und RSS-Feeds.
Geschätzte Laufzeit: unter 40 Sekunden

Quellen:
  1. Bundesagentur für Arbeit  → REST-API  (~5 Sek)
  2. service.bund.de           → RSS-Feed  (~3 Sek)
  3. Interamt                  → HTML-Suche mit requests (~5 Sek)
  4. IT-Jobs.de                → RSS-Feed  (~3 Sek)  [FIX: wird jetzt aufgerufen]
  5. Heise Jobs                → RSS-Feed  (~3 Sek)  [NEU]
  6. Golem Jobs                → HTTP      (~5 Sek)  [NEU]
══════════════════════════════════════════════════════════════
"""

import csv, time, random, logging, re, json, os
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, date
from dotenv import load_dotenv

import requests
import urllib3
urllib3.disable_warnings()

load_dotenv()

# ──────────────────────────────────────────────────────────
#  PFADE
# ──────────────────────────────────────────────────────────
BASE              = os.getenv("BASE_PATH", "/home/jens/JobAgent")
PROFIL_PFAD       = f"{BASE}/daten/skills_profile.json"
FIRMA_GEHALT_PFAD = f"{BASE}/daten/firma_gehalt.json"
CSV_PFAD          = f"{BASE}/jobs/jobs.csv"
SEEN_JOBS_PFAD    = f"{BASE}/daten/seen_jobs.json"

# ──────────────────────────────────────────────────────────
#  PROFIL LADEN
# ──────────────────────────────────────────────────────────
PROFIL_PFAD = "/home/jens/JobAgent/shared/daten/skills_profile.json"
with open(PROFIL_PFAD, encoding="utf-8") as f:
    P = json.load(f)

ERLAUBTE_ORTE  = [o.lower() for o in P["erlaubte_regionen"]]
GESPERRTE_ORTE = [o.lower() for o in P["gesperrte_regionen"]]
SKILLS_HOCH    = [s.lower() for s in P["skills"]["hoch"]]
SKILLS_MITTEL  = [s.lower() for s in P["skills"]["mittel"]]
JOBROLLEN_TOP  = [j.lower() for j in P["jobrollen"]["top"]]
JOBROLLEN_OK   = [j.lower() for j in P["jobrollen"]["okay"]]
JOBROLLEN_NEIN = [j.lower() for j in P["jobrollen"]["nicht_gewuenscht"]]
ARBEITGEBER_OK = [a.lower() for a in P["bevorzugte_arbeitgeber"]]
MIN_GEHALT     = P["gehalt"]["minimum"]

# ──────────────────────────────────────────────────────────
#  LOGGING
# ──────────────────────────────────────────────────────────
Path("/home/jens/JobAgent/shared/logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/home/jens/JobAgent/shared/logs/jobfinder.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────
#  KONFIGURATION
# ──────────────────────────────────────────────────────────
SUCHBEGRIFFE = [
    # Kernrollen passend zum CV
    "IT Administrator",
    "Systemadministrator",
    "Modern Workplace Specialist",
    "Endpoint Administrator",
    "Microsoft 365",
    "IT Support Specialist",
    "Fachinformatiker Systemintegration",
    # Aus CV-Skills direkt abgeleitet
    "Intune Administrator",
    "IT Service Specialist",
    "Desktop Support",
    "Helpdesk",
    "IT Koordinator",
    "Field IT",
    "Workplace Engineer",
    # Wachstumsrichtung
    "Azure Administrator",
    "Cloud Engineer",
    "Netzwerkadministrator",
]

BLOCK_TEXTE = [
    "cookie", "datenschutz", "impressum", "newsletter",
    "anmelden", "registrieren", "aktuell und kompakt",
    "community", "forum", "werbung", "kategorien",
    "mehr laden", "startseite", "menü", "navigation",
]

BLOCK_JOBTITEL = [
    "einkäufer", "einkauf", "beschaffung", "vergabe",
    "operator", "whiteboard", "veranstaltung",
    "haustechniker", "elektrotechniker", "bautechniker",
    "projektassistenz", "labornetzwerk", "studiennetzwerk",
    "softwaretester", "softwaretest", "entwickler",
    "developer", "programmierer", "java", "python",
    "full-stack", "fullstack", "frontend", "backend",
    "devops", "platform engineer", "database engineer",
    "jvm", "postgresql", "software engineer",
    "principal engineer",
    "bürosachbearbeiter", "buchhalter", "rechnungswesen",
    "sozialhilfe", "jugend", "asyl", "ausländer",
    "bauwesen", "tiefbau", "hochbau", "straßenbau",
    "vermessung", "stadtplanung", "abwasser",
    "moodle", "bildungsportal", "bildungs-it",
    "hochschulnetzwerk", "studiengang", "lehrveranstaltung",
    "labornetwork", "refbio", "eulist",
    "senior", "lead ", "principal", "head of",
    "architekt", "architect",
    "linux", "unix", "debian", "ubuntu server",
    "bratislava", "slowakei", "auslandsmitarbeiter",
]

# ──────────────────────────────────────────────────────────
#  FIRMENDATENBANK LADEN
# ──────────────────────────────────────────────────────────
try:
    with open(FIRMA_GEHALT_PFAD, encoding="utf-8") as f:
        FIRMA_DB = json.load(f).get("firmen", {})
    log.debug(f"Firmendatenbank geladen: {len(FIRMA_DB)} Einträge")
except Exception:
    FIRMA_DB = {}
    log.warning("firma_gehalt.json nicht gefunden – Fallback auf Schätzung")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9",
    "Accept": "text/html,application/json,application/xml,*/*",
}

CSV_SEPARATOR = ";"


# ══════════════════════════════════════════════════════════
#  HILFSFUNKTIONEN
# ══════════════════════════════════════════════════════════

def ist_echter_job(titel: str) -> bool:
    if not titel or len(titel.strip()) < 5:
        return False
    t = titel.lower()
    if any(b in t for b in BLOCK_TEXTE):
        return False
    if any(b in t for b in BLOCK_JOBTITEL):
        return False
    if any(n in t for n in JOBROLLEN_NEIN):
        return False
    job_woerter = [
        "administrator", "engineer", "spezialist", "berater",
        "techniker", "support", "it-", " it ", "workplace",
        "netzwerk", "network", "security", "cyber",
        "fachinformatiker", "systemadmin", "informatiker",
        "cloud", "azure", "microsoft", "endpoint", "intune",
        "helpdesk", "servicedesk", "consultant",
    ]
    return any(w in t for w in job_woerter)


def ort_erlaubt(ort: str) -> bool:
    if not ort:
        return True
    o = ort.lower()
    if any(g in o for g in GESPERRTE_ORTE):
        return False
    if any(e in o for e in ERLAUBTE_ORTE):
        return True
    if re.search(r'\b(34|36)\d{3}\b', ort):
        return True
    return False


def gehalt_erkennen(text: str) -> str:
    if not text:
        return ""
    m = re.search(
        r'\b(E\s?\d{1,2}|EG\s?\d{1,2}|TVöD|TV-L|A\s?\d{1,2})\b',
        text, re.IGNORECASE
    )
    if m:
        gruppe = m.group(0).strip().upper().replace(" ", "")
        mapping = {
            "E9":  "ca. 43.000 €", "E10": "ca. 50.000 €",
            "E11": "ca. 60.000 €", "E12": "ca. 70.000 €",
            "E13": "ca. 75.000 €", "EG10":"ca. 50.000 €",
            "EG11":"ca. 60.000 €", "EG12":"ca. 70.000 €",
        }
        label = mapping.get(gruppe, "")
        return f"{gruppe} ({label})" if label else gruppe
    for muster in [
        r'\d{2,3}[.,]\d{3}\s*[-–]\s*\d{2,3}[.,]\d{3}\s*€?',
        r'\d{2,3}[.,]\d{3}\s*€',
        r'€\s*\d{2,3}[.,]\d{3}',
        r'\d{2,3}k\s*[-–]\s*\d{2,3}k',
    ]:
        treffer = re.search(muster, text, re.IGNORECASE)
        if treffer:
            return treffer.group(0).strip()
    return ""


def score_berechnen(titel: str, beschr: str, gehalt: str, firma: str = "") -> int:
    score = 0
    text  = (titel + " " + beschr + " " + gehalt + " " + firma).lower()
    t     = titel.lower()

    perfekte_rollen = [
        "azure administrator", "cloud engineer",
        "endpoint administrator", "microsoft 365 administrator",
        "modern workplace", "workplace engineer",
        "m365", "intune administrator",
    ]
    gute_rollen = [
        "it-administrator", "it administrator",
        "systemadministrator", "it-systemadministrator",
        "netzwerkadministrator", "infrastructure engineer",
        "it system administrator",
    ]
    okay_rollen = [
        "it support", "it-support", "it spezialist",
        "fachinformatiker", "it service", "helpdesk",
        "servicedesk", "it-service", "2nd level",
        "it-projektmitarbeiter", "it mitarbeiter",
        "informatiker", "it-coordinator", "rollout",
    ]

    if any(r in t for r in perfekte_rollen):
        score += 50
    elif any(r in t for r in gute_rollen):
        score += 35
    elif any(r in t for r in okay_rollen):
        score += 20
    else:
        score += 5

    score += min(sum(5 for s in SKILLS_HOCH if s in text), 25)
    score += min(sum(2 for s in SKILLS_MITTEL if s in text), 10)

    tvod_punkte = {
        "e13": 35, "e12": 35, "eg12": 35,
        "e11": 30, "eg11": 30,
        "e10": 20, "eg10": 20,
        "e9":   5,
    }
    gehalt_gefunden = False
    for gruppe, pkt in tvod_punkte.items():
        if gruppe in text:
            score += pkt
            gehalt_gefunden = True
            break
    if not gehalt_gefunden:
        zahlen = re.findall(r'\d+', gehalt.replace(".", "").replace(",", ""))
        for z in zahlen:
            try:
                g = int(z)
                if   g >= 70000: score += 35
                elif g >= 65000: score += 30
                elif g >= 60000: score += 25
                elif g >= 55000: score += 20
                elif g >= 50000: score += 10
                break
            except ValueError:
                pass

    oed_text = (firma + " " + beschr + " " + titel).lower()
    if any(a in oed_text for a in ARBEITGEBER_OK):
        score += 10

    entwicklung = [
        "azure", "cloud", "intune", "endpoint",
        "microsoft 365", "entra", "autopilot",
        "modern workplace", "m365",
    ]
    if any(e in text for e in entwicklung):
        score += 10

    if any(s in t for s in ["senior", "lead", "principal", "head of", "architekt", "architect"]):
        score -= 15

    remote_keywords = [
        "remote", "homeoffice", "home office",
        "freie zeiteinteilung", "flexible arbeitszeit",
        "minijob", "freelance", "freiberuflich",
        "startup", "start-up", "nebenberuflich",
    ]
    if any(k in text for k in remote_keywords):
        score += 15

    return min(max(score, 0), 100)


def arbeitszeit_erkennen(titel: str, beschr: str) -> str:
    text = (titel + " " + beschr).lower()
    if any(k in text for k in ["minijob", "mini-job", "450", "520", "geringfügig"]):
        return "Minijob"
    if any(k in text for k in ["freelance", "freiberuflich", "selbstständig"]):
        return "Freelance"
    if any(k in text for k in ["teilzeit", "part-time", "part time"]):
        return "Teilzeit"
    if any(k in text for k in ["vollzeit", "full-time", "full time", "unbefristet"]):
        return "Vollzeit"
    return "Vollzeit"


def gehalt_schaetzen(titel: str, firma: str) -> str:
    f_lower = firma.lower().strip()
    t_lower = titel.lower().strip()

    for firma_key, data in FIRMA_DB.items():
        if firma_key in f_lower or f_lower in firma_key:
            return f"{data['gehalt']} ({data['quelle']})"

    oed = any(a in f_lower for a in ARBEITGEBER_OK)
    if oed:
        if any(r in t_lower for r in ["azure", "cloud engineer", "endpoint", "microsoft 365", "modern workplace"]):
            return "E11 (ca. 60.000 € / Jahr) *"
        elif any(r in t_lower for r in ["systemadministrator", "it-administrator", "it administrator", "netzwerk"]):
            return "E10 (ca. 50.000 € / Jahr) *"
        elif any(r in t_lower for r in ["it support", "helpdesk", "fachinformatiker", "1st level", "2nd level"]):
            return "E9 (ca. 43.000 € / Jahr) *"
        else:
            return "TVöD E9-E11 (ca. 43.000–60.000 € / Jahr) *"

    if any(r in t_lower for r in ["azure administrator", "cloud engineer", "endpoint administrator", "microsoft 365"]):
        return "ca. 55.000–65.000 € / Jahr *"
    elif any(r in t_lower for r in ["systemadministrator", "it-administrator", "it administrator"]):
        return "ca. 45.000–58.000 € / Jahr *"
    elif any(r in t_lower for r in ["it support", "helpdesk", "1st level", "2nd level"]):
        return "ca. 35.000–45.000 € / Jahr *"
    else:
        return "ca. 40.000–55.000 € / Jahr *"


def gehalt_zu_euro(gehalt: str) -> str:
    if not gehalt:
        return ""
    g = gehalt.upper().replace(" ", "")

    tvod_tabelle = {
        "E9":  "ca. 43.000 € / Jahr",
        "E10": "ca. 50.000 € / Jahr",
        "E11": "ca. 60.000 € / Jahr",
        "E12": "ca. 70.000 € / Jahr",
        "E13": "ca. 75.000 € / Jahr",
        "EG9": "ca. 43.000 € / Jahr",
        "EG10":"ca. 50.000 € / Jahr",
        "EG11":"ca. 60.000 € / Jahr",
        "EG12":"ca. 70.000 € / Jahr",
        "A10": "ca. 48.000 € / Jahr",
        "A11": "ca. 55.000 € / Jahr",
        "A12": "ca. 62.000 € / Jahr",
        "A13": "ca. 70.000 € / Jahr",
    }
    for gruppe, betrag in tvod_tabelle.items():
        if gruppe in g:
            return betrag

    if "€" in gehalt or re.search(r'\d{5}', gehalt):
        return gehalt

    if "TVÖD" in g or "TV-L" in g or "BBESG" in g:
        return "TVöD (ca. 45.000–70.000 € / Jahr)"

    return gehalt


# ══════════════════════════════════════════════════════════
#  QUELLE 1: BUNDESAGENTUR FÜR ARBEIT (API)
# ══════════════════════════════════════════════════════════

def scrape_arbeitsagentur() -> list:
    jobs = []
    url  = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
    hdrs = {**HEADERS, "X-API-Key": "jobboerse-jobsuche", "Accept": "application/json"}

    for begriff in SUCHBEGRIFFE:
        try:
            params = {
                "was": begriff,
                "wo": "Knüllwald",
                "umkreis": 40,  # Max 40km laut Jens' Vorgabe
                "size": 25,
                "page": 1,
                "angebotsart": 1,
            }
            log.info(f"  BA: {begriff}")
            resp = requests.get(url, params=params, headers=hdrs, timeout=15, verify=False)
            if resp.status_code != 200:
                log.warning(f"  BA HTTP {resp.status_code}")
                continue

            for s in resp.json().get("stellenangebote", []):
                titel  = s.get("titel", "").strip()
                firma  = s.get("arbeitgeber", "").strip()
                ort    = s.get("arbeitsort", {}).get("ort", "")
                plz    = s.get("arbeitsort", {}).get("plz", "")
                ref    = s.get("refnr", "")
                link   = f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{ref}" if ref else "https://www.arbeitsagentur.de"
                beschr = s.get("stellenbeschreibung", "") or ""
                ort_voll = f"{plz} {ort}".strip()

                if not ist_echter_job(titel): continue
                if not ort_erlaubt(ort_voll): continue

                beschr_detail = beschr
                if ref and not beschr:
                    try:
                        detail_url = f"https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobdetails/{ref}"
                        det = requests.get(detail_url, headers=hdrs, timeout=8, verify=False)
                        if det.status_code == 200:
                            d = det.json()
                            beschr_detail = (
                                d.get("stellenbeschreibung", "") or
                                d.get("aufgaben", "") or
                                d.get("beschreibung", "") or ""
                            )
                    except:
                        pass

                gehalt = gehalt_erkennen(beschr_detail + " " + titel)
                if not gehalt:
                    gehalt = gehalt_schaetzen(titel, firma)

                gehalt_euro = gehalt_zu_euro(gehalt)
                arbeitszeit = arbeitszeit_erkennen(titel, beschr_detail)
                score  = score_berechnen(titel, beschr_detail, gehalt, firma)
                job_datum = s.get("aktuelleVeroeffentlichungsdatum", date.today().isoformat())
                if job_datum and len(job_datum) >= 10:
                    job_datum = job_datum[:10]
                else:
                    job_datum = date.today().isoformat()
                jobs.append([titel, firma, ort_voll, link, gehalt_euro, score, "Arbeitsagentur", arbeitszeit, job_datum])
                log.info(f"  ✔ {titel} | {ort_voll} | {gehalt_euro or '–'} | {arbeitszeit} | Score {score}")

            time.sleep(0.5)
        except Exception as e:
            log.error(f"  BA Fehler ({begriff}): {e}")

    log.info(f"Arbeitsagentur: {len(jobs)} Jobs")
    return jobs


# ══════════════════════════════════════════════════════════
#  QUELLE 2: SERVICE.BUND.DE (RSS)
# ══════════════════════════════════════════════════════════

def scrape_bund_rss() -> list:
    jobs = []
    rss_urls = [
        "https://www.service.bund.de/Content/Globals/Functions/RSSFeed/RSSGenerator_Stellen.xml",
    ]

    for rss_url in rss_urls:
        try:
            log.info(f"  Bund RSS: abrufen...")
            resp = requests.get(rss_url, headers=HEADERS, timeout=15, verify=False)
            if resp.status_code != 200:
                log.warning(f"  Bund RSS HTTP {resp.status_code}")
                continue

            root = ET.fromstring(resp.content)
            items = root.findall(".//item")
            log.info(f"  Bund RSS: {len(items)} Einträge gefunden")

            for item in items:
                titel  = (item.findtext("title") or "").strip()
                link   = (item.findtext("link") or "https://www.service.bund.de").strip()
                beschr = (item.findtext("description") or "").strip()
                beschr_clean = re.sub(r'<[^>]+>', ' ', beschr).strip()

                if not ist_echter_job(titel):
                    continue

                it_keywords = [
                    "it-", "it ", "administrator", "systemadmin", "informatik",
                    "netzwerk", "cloud", "azure", "microsoft", "endpoint",
                    "workplace", "support", "helpdesk", "fachinformatiker",
                    "cyber", "security", "daten", "software", "anwendung",
                ]
                if not any(k in titel.lower() for k in it_keywords):
                    continue

                ort = ""
                for region in ERLAUBTE_ORTE:
                    if region in (titel + " " + beschr_clean).lower():
                        ort = region.title()
                        break

                if not ort_erlaubt(ort if ort else ""):
                    continue

                gehalt = gehalt_erkennen(beschr_clean + " " + titel)
                if not gehalt:
                    gehalt = "TVöD/BBesG"
                firma = "Bundesbehörde"

                firma_match = re.search(r'(?:beim?|der|die|das)\s+([A-ZÄÖÜ][^.,:]+(?:amt|behörde|ministerium|bundesamt|dienst))',
                                        beschr_clean, re.IGNORECASE)
                if firma_match:
                    firma = firma_match.group(1).strip()

                score = score_berechnen(titel, beschr_clean, gehalt, firma)
                gehalt_euro = gehalt_zu_euro(gehalt)
                arbeitszeit = arbeitszeit_erkennen(titel, beschr_clean)
                ort_anzeige = ort if ort else "Bundesweit/Hessen"
                jobs.append([titel, firma, ort_anzeige, link, gehalt_euro, score, "Bund/Interamt", arbeitszeit, date.today().isoformat()])
                log.info(f"  ✔ {titel} | {ort_anzeige} | {gehalt_euro} | Score {score}")

            if jobs:
                break

        except ET.ParseError:
            log.warning("  Bund RSS: XML-Parse Fehler")
        except Exception as e:
            log.error(f"  Bund RSS Fehler: {e}")

    log.info(f"Bund RSS: {len(jobs)} Jobs")
    return jobs


# ══════════════════════════════════════════════════════════
#  QUELLE 3: ARBEITSAGENTUR REMOTE
# ══════════════════════════════════════════════════════════

def scrape_arbeitsagentur_remote() -> list:
    jobs = []
    url  = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
    hdrs = {**HEADERS, "X-API-Key": "jobboerse-jobsuche", "Accept": "application/json"}

    remote_begriffe = [
        "IT Administrator Remote",
        "Systemadministrator Homeoffice",
        "IT Support Remote",
        "Microsoft 365 Remote",
        "Cloud Engineer Remote",
    ]

    for begriff in remote_begriffe:
        try:
            params = {
                "was": begriff,
                "umkreis": 200,
                "size": 10,
                "page": 1,
                "angebotsart": 1,
            }
            log.info(f"  BA Remote: {begriff}")
            resp = requests.get(url, params=params, headers=hdrs, timeout=15, verify=False)
            if resp.status_code != 200:
                continue

            for s in resp.json().get("stellenangebote", []):
                titel  = s.get("titel", "").strip()
                firma  = s.get("arbeitgeber", "").strip()
                ort    = s.get("arbeitsort", {}).get("ort", "")
                plz    = s.get("arbeitsort", {}).get("plz", "")
                ref    = s.get("refnr", "")
                link   = f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{ref}" if ref else "https://www.arbeitsagentur.de"
                beschr = s.get("stellenbeschreibung", "") or ""
                ort_voll = f"{plz} {ort}".strip()

                if not ist_echter_job(titel): continue

                text_gesamt = (titel + " " + beschr).lower()
                ist_remote = any(k in text_gesamt for k in [
                    "remote", "homeoffice", "home office",
                    "bundesweit", "freie zeiteinteilung",
                    "minijob", "freelance", "startup",
                ])
                if not ist_remote:
                    continue

                gehalt = gehalt_erkennen(beschr + " " + titel)
                gehalt_euro = gehalt_zu_euro(gehalt)
                arbeitszeit = arbeitszeit_erkennen(titel, beschr)
                score = score_berechnen(titel, beschr, gehalt, firma)
                job_datum = s.get("aktuelleVeroeffentlichungsdatum", date.today().isoformat())
                job_datum = job_datum[:10] if job_datum and len(job_datum) >= 10 else date.today().isoformat()
                jobs.append([titel, firma, f"Remote ({ort_voll})", link, gehalt_euro, score, "Remote/Startup", arbeitszeit, job_datum])
                log.info(f"  ✔ {titel} | Remote | {gehalt_euro or '–'} | Score {score}")

            time.sleep(0.5)
        except Exception as e:
            log.error(f"  BA Remote Fehler ({begriff}): {e}")

    log.info(f"Remote/Startup: {len(jobs)} Jobs")
    return jobs


# ══════════════════════════════════════════════════════════
#  QUELLE 4: INTERAMT (HTML)
# ══════════════════════════════════════════════════════════

def scrape_interamt_html() -> list:
    jobs = []
    basis = "https://www.interamt.de/koop/app/trefferliste"

    for begriff in SUCHBEGRIFFE[:4]:
        try:
            params = {
                "suchtext": begriff,
                "bundesland": "HE",
                "start": 0,
                "anzahl": 20,
            }
            log.info(f"  Interamt: {begriff}")
            resp = requests.get(
                basis, params=params, headers=HEADERS,
                timeout=20, verify=False, allow_redirects=True
            )

            if resp.status_code != 200:
                log.warning(f"  Interamt HTTP {resp.status_code}")
                continue

            html = resp.text
            alle_links = re.findall(r'href="(/koop/app/stelle[^"]{3,80})"', html)

            gefunden = 0
            seen_lokal = set()

            for rel_link in alle_links:
                pattern = re.escape(rel_link) + r'"[^>]*>\s*([^\n<]{8,120})'
                match = re.search(pattern, html)
                if not match:
                    continue
                titel = re.sub(r'\s+', ' ', match.group(1)).strip()
                titel = re.sub(r'<[^>]+>', '', titel).strip()

                if titel.lower() in seen_lokal:
                    continue
                seen_lokal.add(titel.lower())

                if not ist_echter_job(titel):
                    continue
                if len(titel) < 8 or len(titel) > 100:
                    continue

                link   = f"https://www.interamt.de{rel_link}"
                gehalt = "TVöD (öff. Dienst)"
                score  = score_berechnen(titel, "", gehalt, "Öffentlicher Dienst Hessen")
                jobs.append([titel, "Öffentlicher Dienst Hessen", "Hessen", link, gehalt, score, "Interamt", "Vollzeit", date.today().isoformat()])
                log.info(f"  ✔ {titel} | Hessen | {gehalt} | Score {score}")
                gefunden += 1

            if gefunden == 0:
                log.info(f"  Interamt '{begriff}': {len(alle_links)} Links gefunden, 0 als Job erkannt")

            time.sleep(1)

        except Exception as e:
            log.error(f"  Interamt Fehler ({begriff}): {e}")

    log.info(f"Interamt: {len(jobs)} Jobs")
    return jobs


# ══════════════════════════════════════════════════════════
#  QUELLE 5: IT-JOBS.DE (RSS)  [WAR SCHON DRIN, ABER NICHT AUFGERUFEN – FIXED]
# ══════════════════════════════════════════════════════════

def scrape_itjobs_rss() -> list:
    """Deaktiviert."""
    log.info("Jobware/IT-Jobs: deaktiviert")
    return []

# ══════════════════════════════════════════════════════════
#  QUELLE 6: HEISE JOBS (HTTP-Suche)  [FIXED – kein /rss/jobs.rss]
# ══════════════════════════════════════════════════════════





# ══════════════════════════════════════════════════════════
#  QUELLE 6: HEISE JOBS (HTTP + JSON-LD)  [NEU]
# ══════════════════════════════════════════════════════════

def scrape_heise_jobs_rss() -> list:
    """Deaktiviert."""
    log.info("Heise Jobs: deaktiviert")
    return []

# ══════════════════════════════════════════════════════════
#  QUELLE 7: GOLEM JOBS (HTTP)  [NEU]
# ══════════════════════════════════════════════════════════

def scrape_golem_jobs() -> list:
    """Deaktiviert."""
    log.info("Kimeta/Golem: deaktiviert")
    return []

# ══════════════════════════════════════════════════════════
#  DUPLIKATE ENTFERNEN
# ══════════════════════════════════════════════════════════

def duplikate_entfernen(jobs: list) -> list:
    seen = set()
    unique = []
    for job in jobs:
        key = (job[0].lower().strip(), job[1].lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique


# ══════════════════════════════════════════════════════════
#  HAUPT-FUNKTION
# ══════════════════════════════════════════════════════════

def lade_seen_jobs() -> set:
    try:
        with open(SEEN_JOBS_PFAD, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def speichere_seen_jobs(seen: set):
    with open(SEEN_JOBS_PFAD, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False)

def ist_job_neu(job: list, seen: set) -> bool:
    key = f"{job[0].lower().strip()}|{job[1].lower().strip()}"
    return key not in seen

def ist_job_aktuell(job: list, tage: int = 3) -> bool:
    try:
        job_datum = date.fromisoformat(job[8])
        delta = (date.today() - job_datum).days
        return delta <= tage
    except:
        return True

def run_jobfinder():
    start = datetime.now()
    log.info("=" * 55)
    log.info(f"JobFinder v6 | {start.strftime('%d.%m.%Y %H:%M')}")
    log.info(f"Profil: {P['name']} | Umkreis: 40km | Min: {MIN_GEHALT:,}EUR")
    log.info("Modus: Nur API/RSS - kein Selenium")
    log.info("Quellen: BA + Bund + Remote + Interamt + IT-Jobs + Heise + Golem")
    log.info("=" * 55)

    alle_jobs = []
    alle_jobs += scrape_arbeitsagentur()
    alle_jobs += scrape_bund_rss()
    alle_jobs += scrape_arbeitsagentur_remote()
    alle_jobs += scrape_interamt_html()
    alle_jobs += scrape_itjobs_rss()
    alle_jobs += scrape_heise_jobs_rss()
    alle_jobs += scrape_golem_jobs()

    # Duplikate entfernen
    jobs = duplikate_entfernen(alle_jobs)

    # Score < 25 rausfiltern
    jobs = [j for j in jobs if int(j[5]) >= 25]

    # Nur Jobs der letzten 3 Tage
    jobs_aktuell = [j for j in jobs if ist_job_aktuell(j, tage=3)]
    log.info(f"Nach 3-Tage-Filter: {len(jobs_aktuell)} von {len(jobs)} Jobs")

    # Seen Jobs laden
    seen = lade_seen_jobs()
    jobs_neu = [j for j in jobs_aktuell if ist_job_neu(j, seen)]
    log.info(f"Neue Jobs: {len(jobs_neu)}")

    # Seen Jobs updaten
    for j in jobs_aktuell:
        key = f"{j[0].lower().strip()}|{j[1].lower().strip()}"
        seen.add(key)
    speichere_seen_jobs(seen)

    # Sortieren
    jobs_neu.sort(key=lambda x: int(x[5]) if str(x[5]).isdigit() else 0, reverse=True)

    # CSV schreiben
    Path("/home/jens/JobAgent/jobagent/jobs").mkdir(parents=True, exist_ok=True)
    with open(CSV_PFAD, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=CSV_SEPARATOR)
        writer.writerow(["Titel", "Firma", "Ort", "Link", "Gehalt", "Score", "Quelle", "Arbeitszeit", "datum"])
        writer.writerows(jobs_neu)

    dauer = (datetime.now() - start).seconds
    log.info("=" * 55)
    log.info(f"Fertig! {len(jobs_neu)} neue Jobs | {dauer}s | {CSV_PFAD}")
    log.info("=" * 55)
    return jobs_neu


if __name__ == "__main__":
    run_jobfinder()