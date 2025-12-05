import streamlit as st
import pandas as pd

st.title("💬 Query in Linguaggio Naturale (Simple NLP Parser)")

df = st.session_state["df"]

query = st.text_input("Chiedi qualcosa sui dati...")

if query:

    q = query.lower()

    if "top" in q and "vend" in q:
        st.subheader("Top 10 giochi per vendite globali")
        st.dataframe(df.nlargest(10, "Global_Sales")[["Name", "Platform", "Global_Sales"]])

    elif "critic" in q and ("top" in q):
        st.subheader("Top 10 Critic Score")
        st.dataframe(df.nlargest(10, "Critic_Score")[["Name", "Critic_Score"]])

    elif "genere" in q:
        st.subheader("Vendite totali per genere")
        st.bar_chart(df.groupby("Genre")["Global_Sales"].sum())

    else:
        st.error("❌ Query non riconosciuta. (Parser molto semplice)")
