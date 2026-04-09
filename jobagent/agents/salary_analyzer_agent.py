import csv
import re


def run_salary_analyzer():

    input_file = "C:/JobAgent/jobagent/jobs/jobs_scored.csv"
    output_file = "C:/JobAgent/jobagent/jobs/jobs_salary_scored.csv"

    results = []

    with open(input_file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            title = row["Titel"]
            company = row["Firma"]
            location = row["Ort"]
            link = row["Link"]
            score = int(row["Score"])

            salary_bonus = 0
            salary_text = ""

            try:

                text = title.lower()

                salary_matches = re.findall(r"\d{2,3}\.?000", text)

                if salary_matches:

                    salary_value = int(salary_matches[0].replace(".",""))

                    salary_text = salary_matches[0]

                    if salary_value >= 65000:
                        salary_bonus = 20

                    elif salary_value >= 55000:
                        salary_bonus = 10

            except:
                pass

            score = score + salary_bonus

            results.append([
                title,
                company,
                location,
                link,
                salary_text,
                score
            ])

    with open(output_file,"w",newline="",encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["Titel","Firma","Ort","Link","Gehalt","Score"])

        writer.writerows(results)

    print("Gehaltsanalyse abgeschlossen:",len(results))