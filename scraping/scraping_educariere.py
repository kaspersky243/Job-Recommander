import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import string
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity


url = "https://emploi.educarriere.ci/emploi/page/emploi"

pages = 5

csv_file_educariere = "educarriere.csv"

admin = "admin123"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def charge_donnee(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=['titre', 'lien', 'date_edition', 'date_limite'])

def scrapping_educariere():

    existe_df = charge_donnee(csv_file_educariere)
    existe_lien = set(existe_df["lien"].tolist())

    new_jobs = []

    for page in range(1, pages + 1):
        page_url = f"{url}/{page}"
        response = requests.get(page_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.find_all("div", class_="post-content")

        for job in jobs:
            title_element = job.find("h4", class_="post-title")
            if title_element:
                title = title_element.find("a", href=True)
                if title:
                    titre = title.text.strip()
                    lien = title["href"]
            
            date = job.find("span", class_="rt-meta")
            if date:
                date_items = date.find_all("li")

                if len(date_items) > 1:
                    span_edition = date_items[1].find("span")
                    if span_edition:
                        date_edition = span_edition.text.strip()

                if len(date_items) > 2:
                    span_limite = date_items[2].find("span")
                    if span_limite:
                        date_limite = span_limite.text.strip()

            if lien not in existe_lien:
                new_jobs.append({
                    "titre": titre,
                    "lien": lien,
                    "date_edition": date_edition,
                    "date_limite": date_limite
                })
                existe_lien.add(lien)

    new_jobs_df = pd.DataFrame(new_jobs)

    if not new_jobs_df.empty:
        mise_a_jour = pd.concat([existe_df, new_jobs_df], ignore_index=True)
        mise_a_jour.to_csv(csv_file_educariere, index=False, encoding="utf-8")
        return mise_a_jour, len(new_jobs_df)
    

    return existe_df, 0


