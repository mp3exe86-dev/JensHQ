import csv

skills = [
"administrator",
"system",
"microsoft",
"azure",
"intune",
"endpoint"
]

def run_match():

    input_file = "C:/JobAgent/jobagent/jobs/jobs.csv"
    output_file = "C:/JobAgent/jobagent/jobs/jobs_scored.csv"

    results = []

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:

            title = row[0].lower()

            score = 0

            for skill in skills:
                if skill in title:
                    score += 20

            results.append([row[0], score])

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Titel","Match"])
        writer.writerows(results)

    print("Job Match Analyse fertig.")