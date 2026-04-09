import csv

def run_location_filter():

    file = "C:/JobAgent/jobagent/jobs/jobs.csv"

    allowed_locations = [
        "kassel",
        "fulda",
        "bad hersfeld",
        "schwalmstadt",
        "bad wildungen",
        "rotenburg",
        "bebra",
        "homberg"
    ]

    rows = []

    with open(file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            location = row["Ort"].lower()

            keep = False

            for city in allowed_locations:

                if city in location:
                    keep = True

            if keep:
                rows.append(row)

    with open(file, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=["Titel","Firma","Ort","Link","Gehalt","Score"]
        )

        writer.writeheader()

        for r in rows:
            writer.writerow(r)

    print("Location Filter fertig")