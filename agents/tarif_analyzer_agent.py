import csv
import re

def run_tarif_analyzer():

    file = "/home/jens/JobAgent/jobs/jobs.csv"
    rows = []

    # utf-8-sig liest BOM automatisch weg → Titel wird korrekt erkannt
    with open(file, newline="", encoding="utf-8-sig") as f:

        reader = csv.DictReader(f, delimiter=";")

        for row in reader:

            titel    = row.get("Titel", "").strip()
            firma    = row.get("Firma", "").strip()
            ort      = row.get("Ort", "").strip()
            link     = row.get("Link", "").strip()
            gehalt   = row.get("Gehalt", "").strip()
            score    = row.get("Score", "0").strip()

            quelle     = row.get("Quelle", "").strip()
            arbeitszeit = row.get("Arbeitszeit", "Vollzeit").strip()

            # Score vom Jobfinder übernehmen wenn vorhanden
            try:
                score = int(score)
            except ValueError:
                score = 0

            text = (titel + " " + firma + " " + gehalt).lower()

            # TVöD nachschärfen falls Jobfinder kein Gehalt erkannt hat
            if not gehalt:
                if "e12" in text or "eg12" in text:
                    gehalt = "E12 (ca. 70.000 €)"
                    score = max(score, 70)
                elif "e11" in text or "eg11" in text:
                    gehalt = "E11 (ca. 60.000 €)"
                    score = max(score, 60)
                elif "e10" in text or "eg10" in text:
                    gehalt = "E10 (ca. 50.000 €)"
                    score = max(score, 45)
                else:
                    # Zahl im Text suchen
                    match = re.search(r'(\d{2,3}\.?000)', text)
                    if match:
                        value = int(match.group(1).replace(".", ""))
                        gehalt = f"{value:,} €".replace(",", ".")
                        if value >= 70000:
                            score = max(score, 70)
                        elif value >= 60000:
                            score = max(score, 60)
                        elif value >= 55000:
                            score = max(score, 50)

            rows.append({
                "Titel":      titel,
                "Firma":      firma,
                "Ort":        ort,
                "Link":       link,
                "Gehalt":     gehalt,
                "Score":      score,
                "Quelle":     quelle,
                "Arbeitszeit": arbeitszeit,
            })

    with open(file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["Titel","Firma","Ort","Link","Gehalt","Score","Quelle","Arbeitszeit"], delimiter=";")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print("Gehaltsanalyse fertig")