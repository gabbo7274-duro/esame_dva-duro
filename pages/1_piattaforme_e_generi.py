import streamlit as st
import plotly.express as px
import pandas as pd

st.title("📊 Analisi Piattaforme e Generi")

df = st.session_state["df"]

st.write("Esplora come sono cambiate nel tempo le piattaforme e i generi più venduti.")

metric = st.selectbox(
    "Scegli la metrica di vendita",
    ["Global_Sales", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
)

# ------------------- ANALISI PIATTAFORME -------------------
st.subheader("Vendite nel tempo per piattaforma")

df_platform = df.groupby(["Year_of_Release", "Platform"])[metric].sum().reset_index()

fig1 = px.line(df_platform,
               x="Year_of_Release",
               y=metric,
               color="Platform",
               title="Vendite per piattaforma nel tempo")

st.plotly_chart(fig1, use_container_width=True)

# ------------------- ANALISI GENERI -------------------
st.subheader("Vendite nel tempo per genere")

df_genre = df.groupby(["Year_of_Release", "Genre"])[metric].sum().reset_index()

fig2 = px.line(df_genre,
               x="Year_of_Release",
               y=metric,
               color="Genre",
               title="Vendite per genere nel tempo")

st.plotly_chart(fig2, use_container_width=True)
