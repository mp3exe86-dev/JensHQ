import csv

def run_duplicate_cleaner():

    input_file = "C:/JobAgent/jobagent/jobs/jobs_raw.csv"
    output_file = "C:/JobAgent/jobagent/jobs/jobs_clean.csv"

    seen_links = set()
    cleaned_jobs = []

    with open(input_file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            link = row["Link"]

            if link not in seen_links:

                seen_links.add(link)

                cleaned_jobs.append([
                    row["Titel"],
                    row["Firma"],
                    row["Ort"],
                    row["Link"]
                ])

    with open(output_file, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["Titel","Firma","Ort","Link"])

        writer.writerows(cleaned_jobs)

    print("Duplikate entfernt:", len(cleaned_jobs))