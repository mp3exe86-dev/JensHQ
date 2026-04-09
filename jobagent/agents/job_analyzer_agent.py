import csv
import re

def run_tarif_analyzer():

    file = "C:/JobAgent/jobagent/jobs/jobs.csv"

    rows = []

    with open(file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            title = row["Titel"]
            company = row["Firma"]
            location = row["Ort"]
            link = row["Link"]

            text = title.lower()

            salary = ""
            score = 0

            if re.search(r"e10", text):

                salary = "50k"
                score = 50

            elif re.search(r"e11", text):

                salary = "60k"
                score = 70

            elif re.search(r"e12", text):

                salary = "70k"
                score = 90

            rows.append({
                "Titel": title,
                "Firma": company,
                "Ort": location,
                "Link": link,
                "Gehalt": salary,
                "Score": score
            })

    with open(file, "w", newline="", encoding="utf-8") as f:

        fieldnames = ["Titel","Firma","Ort","Link","Gehalt","Score"]

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for r in rows:
            writer.writerow(r)

    print("Tarif Analyse fertig")