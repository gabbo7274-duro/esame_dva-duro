import streamlit as st
import pandas as pd

# -------------------------------------------------------
# CARICAMENTO DATASET (CACHE)
# -------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(r".\data\vgsales_clean.csv")
    df["Year_of_Release"] = pd.to_numeric(df["Year_of_Release"], errors="coerce")
    df["User_Score"] = pd.to_numeric(df["User_Score"], errors="coerce")
    df["Is_Hit"] = (df["Global_Sales"] >= 1.0).astype(int)
    return df

df = load_data()

# Rendiamo il dataset disponibile a tutte le pagine
st.session_state["df"] = df

# -------------------------------------------------------
# HOME PAGE
# -------------------------------------------------------
st.title("🎮 Videogame Sales Analytics")
st.subheader("Dashboard multipagina con Streamlit")

st.markdown("""
Benvenuto nella dashboard analitica dei videogiochi!  
Da qui puoi accedere alle varie sezioni tramite il menu **Pages** sulla sinistra.

### Contenuti:
- **📊 Analisi piattaforme e generi**
- **⭐ Studio delle recensioni e dell’impatto sulle vendite**
- **🤖 Modello ML per predire se un gioco sarà un HIT**
- **💬 Query in linguaggio naturale sui dati**

Caricamento dataset completato! Buona esplorazione 🙌
""")
