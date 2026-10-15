import streamlit as st
from etl import load_clean_client, load_clean_commande, load_clean_meteo, load_clean_producteurs, load_clean_produits, load_clean_approvisionnement, load_base_analytique


def run_etl_process():
    load_clean_client.main()
    load_clean_commande.main()
    load_clean_meteo.main()
    load_clean_producteurs.main()
    load_clean_produits.main()
    load_clean_approvisionnement.main()
    print("ETL process completed successfully.")

def populate_datalake():
    load_base_analytique.main()
    print("Datalake populated successfully.")

if (__name__) == "__main__":

    st.button("Run ETL Process", on_click=run_etl_process)

    st.button("Populate datalake", on_click=populate_datalake)