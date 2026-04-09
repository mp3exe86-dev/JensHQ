import csv
import requests


def run_company_analyzer():

    input_file = "C:/JobAgent/jobagent/jobs/jobs_salary_scored.csv"
    output_file = "C:/JobAgent/jobagent/jobs/jobs_company_scored.csv"

    results = []

    with open(input_file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            title = row["Titel"]
            company = row["Firma"]
            location = row["Ort"]
            link = row["Link"]
            salary = row["Gehalt"]
            score = int(row["Score"])

            company_score = 0
            rating_hint = ""

            try:

                query = company + " kununu bewertung"

                search_url = "https://duckduckgo.com/html/?q=" + query.replace(" ", "+")

                r = requests.get(search_url)

                text = r.text.lower()

                if "kununu" in text:
                    company_score += 5
                    rating_hint = "Kununu gefunden"

                if "glassdoor" in text:
                    company_score += 5
                    rating_hint += " Glassdoor gefunden"

            except:
                pass

            score = score + company_score

            results.append([
                title,
                company,
                location,
                link,
                salary,
                rating_hint,
                score
            ])

    with open(output_file, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["Titel","Firma","Ort","Link","Gehalt","Bewertung","Score"])

        writer.writerows(results)

    print("Firmenanalyse abgeschlossen:", len(results))