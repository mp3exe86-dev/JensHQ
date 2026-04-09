from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import time
import random


skills = [
    "azure",
    "microsoft 365",
    "intune",
    "endpoint",
    "active directory",
    "entra",
    "exchange",
    "teams",
    "windows server",
    "group policy"
]


def run_description_analyzer():

    service = Service("C:/JobAgent/shared/drivers/chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    input_file = "C:/JobAgent/jobagent/jobs/jobs_clean.csv"
    output_file = "C:/JobAgent/jobagent/jobs/jobs_scored.csv"

    results = []

    with open(input_file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            title = row["Titel"]
            company = row["Firma"]
            location = row["Ort"]
            link = row["Link"]

            score = 0

            # Titel Analyse
            title_lower = title.lower()

            if "administrator" in title_lower:
                score += 40

            if "system" in title_lower:
                score += 20

            if "cloud" in title_lower or "azure" in title_lower:
                score += 20

            # Jobbeschreibung öffnen
            try:

                driver.get(link)

                time.sleep(random.uniform(5,8))

                text = driver.find_element(By.TAG_NAME,"body").text.lower()

                for skill in skills:

                    if skill in text:
                        score += 5

            except:
                pass

            results.append([
                title,
                company,
                location,
                link,
                score
            ])

    driver.quit()

    with open(output_file,"w",newline="",encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["Titel","Firma","Ort","Link","Score"])

        writer.writerows(results)

    print("Jobbeschreibungen analysiert:",len(results))