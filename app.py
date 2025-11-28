import streamlit as st
import pandas as pd
from scraping.scraping_educariere import scrapping_educariere, charge_donnee, csv_file_educariere
from scraping.scraping_novojob import scrapping_novojob, charge_donnee, csv_file_novojob
from model.model import prepare_model, recommandation_job, charger_les_jobs

st.set_page_config(page_title="Job Recommander", layout="wide")
st.title("Plateforme de recommandation d'offres")

mode = st.sidebar.selectbox("Mode", ["Utilisateur", "Admin"])

if mode == "Admin":
    st.subheader("Espace Administrateur")
    pwd = st.text_input("Mot de passe", type="password")

    if pwd != "admin123":
        st.warning("Mot de passe incorrect.")
        st.stop()

    st.success("Connecté")

    if st.button("Scrape les offres"):
        df, count = scrapping_novojob()
        if count:
            st.success(f"{count} nouvelles offres ajoutées.")
        else:
            st.info("Aucune offre ajoutée.")

    df = charger_les_jobs()
    st.subheader("Toutes les offres")
    st.dataframe(df)
    # st.write(df.tail(20))


else:
    st.subheader("Trouver une offre")

    df = charger_les_jobs()
    if df.empty:
        st.error("Le scraping doit être exécuté par l'admin")
        st.stop()

    vectorisation, x = prepare_model(df)

    titre = st.text_input("Titre recherché", "data analyst")
    competence = st.text_input("Compétences", "python sql power bi")
    decsription = st.text_area("Description", "Je recherche une offre dans les données")
    top_n = st.slider("Nombre de résultats", 3, 10, 5)

    if st.button("Recherche"):
        query = f"{titre} {competence} {decsription}"
        resultat = recommandation_job(df, vectorisation, x, query, top_n)

        resultat["lien"] = resultat["lien"].apply(lambda x: f"[Voir l'offre]({x})")
        st.markdown(resultat.to_markdown(index=False), unsafe_allow_html=True)