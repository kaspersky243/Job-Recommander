import re
import string
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def nettoyage_text(texte):
    if not isinstance(texte, str):
        return ""
    texte = texte.lower()
    texte = texte.translate(str.maketrans("", "", string.punctuation))
    texte = re.sub(r"\s+", " ", texte)
    return texte


def prepare_model(df):

    df = df.dropna(subset=["titre"])
    df = df[df["titre"].astype(str).str.strip() != ""]
    df = df.reset_index(drop=True)

    df["clean_title"] = df["titre"].apply(nettoyage_text)

    vectorisation = TfidfVectorizer(stop_words="english", max_features=5000)
    x = vectorisation.fit_transform(df["clean_title"])
    return vectorisation, x


def recommandation_job(df, vectorisation, x, query, top_n):
    vec = vectorisation.transform([nettoyage_text(query)])
    scores = cosine_similarity(vec, x).flatten()
    idx = scores.argsort()[::-1][:top_n]
    recommendations = df.iloc[idx][["titre", "lien", "date_edition", "date_limite"]]
    recommendations["date_limite"] = pd.to_datetime(recommendations["date_limite"], errors="coerce")
    recommendations = recommendations.sort_values(by="date_limite", ascending=False)
    recommendations["date_limite"] = recommendations["date_limite"].dt.strftime('%d/%m/%Y')
    return recommendations


def charger_les_jobs():
    df1 = pd.read_csv("educarriere.csv")
    df2 = pd.read_csv("novojob.csv")

    # fusionner les deux
    df = pd.concat([df1, df2], ignore_index=True)

    # nettoyer
    df["titre"] = df["titre"].fillna("")
    df["lien"] = df["lien"].fillna("")

    # supprimer doublons par lien
    df = df.drop_duplicates(subset=["lien"], keep="first")

    # supprimer lignes sans titre ou sans lien
    df = df[df["titre"].str.strip() != ""]
    df = df[df["lien"].str.strip() != ""]

    return df.reset_index(drop=True)