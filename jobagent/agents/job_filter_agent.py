import csv


def run_filter():

    input_file = "C:/JobAgent/jobagent/jobs/jobs_scored.csv"
    output_file = "C:/JobAgent/jobagent/jobs/jobs_top.csv"

    results = []

    with open(input_file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            score = int(row["Score"])

            if score >= 75:

                results.append([
                    row["Titel"],
                    row["Firma"],
                    row["Ort"],
                    row["Link"],
                    score
                ])

    with open(output_file, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["Titel", "Firma", "Ort", "Link", "Score"])

        writer.writerows(results)

    print("Top Jobs gespeichert:", len(results))