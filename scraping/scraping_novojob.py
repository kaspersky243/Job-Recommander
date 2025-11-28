import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import string
from datetime import datetime


url = "https://www.novojob.com/cote-d-ivoire/offres-d-emploi"

csv_file_novojob = "novojob.csv"

admin = "admin123"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def charge_donnee(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=['titre', 'lien', 'date_edition', 'date_limite'])

def parse_date(date_text):
    date_text = date_text.strip()
    
    try:
        return datetime.strptime(date_text, "%d %B %Y").strftime("%d/%m/%Y")
    except ValueError:
        pass
    try:
        current_year = datetime.now().year
        new_date = f"{date_text} {current_year}"
        return datetime.strptime(new_date, "%d %B %Y").strftime("%d/%m/%Y")
    except ValueError:
        return None

def scrapping_novojob():

    existe_df = charge_donnee(csv_file_novojob)
    existe_lien = set(existe_df["lien"].tolist())

    new_jobs = []

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    jobs = soup.find_all("div", class_="row-fluid")

    months_fr_to_en = {
        "Janvier": "January", "Février": "February", "Mars": "March", "Avril": "April",
        "Mai": "May", "Juin": "June", "Juillet": "July", "Août": "August",
        "Septembre": "September", "Octobre": "October", "Novembre": "November", "Décembre": "December"
    }

    current_year = datetime.now().year

    for job in jobs:

        titre = ""
        link = ""
        date_publication = ""
        date_expiration = ""

        lien = job.find("a", href=True)
        if not lien:
            continue

        link = lien["href"]

        h2_tag = lien.find("h2", class_="ellipsis row-fluid")
        if h2_tag:
            titre = h2_tag.text.strip()

        clock_icon = job.find("i", class_="fa fa-clock-o icon-left")
        if clock_icon and clock_icon.parent:

            date_text = clock_icon.parent.get_text(strip=True)

            if len(date_text.split()) == 2:
                date_text = f"{date_text} {current_year}"

            for fr, en in months_fr_to_en.items():
                date_text = date_text.replace(fr, en)

            date_publication = datetime.strptime(date_text, "%d %B %Y").strftime("%d/%m/%Y")

        if link in existe_lien:
            continue 

        detail = requests.get(link, headers=headers, timeout=15)
        detail_soup = BeautifulSoup(detail.text, "html.parser")


        expiration_lbl = detail_soup.find(
            "span", class_="text-bold",
            string=lambda x: x and "expiration" in x.lower()
        )

        if expiration_lbl:
            expiration_span = expiration_lbl.find_parent("li").find("span", class_="span8")
            date_expiration = expiration_span.get_text(strip=True)

            for fr, en in months_fr_to_en.items():
                date_expiration = date_expiration.replace(fr, en)
            date_expiration = parse_date(date_expiration)


        new_jobs.append({
            "titre": titre,
            "lien": link,
            "date_edition": date_publication,
            "date_limite": date_expiration,
        })

        existe_lien.add(link)


    new_jobs_df = pd.DataFrame(new_jobs)

    if not new_jobs_df.empty:
        mise_a_jour = pd.concat([existe_df, new_jobs_df], ignore_index=True)
        mise_a_jour.to_csv(csv_file_novojob, index=False, encoding="utf-8")
        return mise_a_jour, len(new_jobs_df)

    return existe_df, 0