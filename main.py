import streamlit as st
from etl import load_clean_client, load_clean_commande, load_clean_meteo, load_clean_producteurs, load_clean_produits, load_clean_approvisionnement, load_base_analytique, etl_datalake

def run_etl_process():
    load_clean_client.main()
    load_clean_commande.main()
    load_clean_meteo.main()
    load_clean_producteurs.main()
    load_clean_produits.main()
    load_clean_approvisionnement.main()
    print("Le processus ETL est terminé.")

def populate_analytical_db():
    load_base_analytique.main()
    print("La base analytique est remplie avec succès.")

def populate_datalake():
    # Appel de la fonction pour remplir le datalake
    etl_datalake.main()
    print("Le datalake est rempli avec succès.")

if (__name__) == "__main__":

    st.button("Lancer le processus ETL", on_click=run_etl_process)

    st.button("Remplir la base analytique", on_click=populate_analytical_db)

    st.button("Remplir le datalake", on_click=populate_datalake)