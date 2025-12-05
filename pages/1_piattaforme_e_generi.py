import streamlit as st
import plotly.express as px
import pandas as pd

st.title("Analisi Piattaforme e Generi")

df = st.session_state["df"]

st.write("""
In questa pagina analizziamo **come si sono evolute le piattaforme e i generi** nel corso del tempo.
I grafici sono filtrati sulle categorie più rilevanti per rendere l'analisi immediata.
""")


metric = st.selectbox(
    "Scegli la metrica di vendita",
    ["Global_Sales", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
)

col1, col2 = st.columns(2)
with col1:
    top_n_platforms = st.slider("Quante piattaforme mostrare?", 3, 15, 7)
with col2:
    top_n_genres = st.slider("Quanti generi mostrare?", 3, 12, 8)


st.subheader("Piattaforme e Generi più venduti (classifica totale)")

col1, col2 = st.columns(2)

with col1:
    top_platforms = (
        df.groupby("Platform")[metric]
        .sum()
        .sort_values(ascending=False)
        .head(top_n_platforms)
        .reset_index()
    )
    fig_top_plat = px.bar(
        top_platforms, x="Platform", y=metric, text=metric,
        title=f"Top {top_n_platforms} piattaforme"
    )
    fig_top_plat.update_traces(textposition="outside")
    st.plotly_chart(fig_top_plat, use_container_width=True)

    best_platform = top_platforms.iloc[0]
    st.info(f"La piattaforma più performante è **{best_platform['Platform']}** con {best_platform[metric]:,.1f} milioni di copie vendute.")

with col2:
    top_genres = (
        df.groupby("Genre")[metric]
        .sum()
        .sort_values(ascending=False)
        .head(top_n_genres)
        .reset_index()
    )
    fig_top_gen = px.bar(
        top_genres, x="Genre", y=metric, text=metric,
        title=f"Top {top_n_genres} generi"
    )
    fig_top_gen.update_traces(textposition="outside")
    st.plotly_chart(fig_top_gen, use_container_width=True)

    best_genre = top_genres.iloc[0]
    st.info(f"Il genere più venduto è **{best_genre['Genre']}** con {best_genre[metric]:,.1f} milioni di copie vendute.")


st.subheader("Vendite nel tempo per piattaforma")

df_platform = (
    df[df["Platform"].isin(top_platforms["Platform"])]
    .groupby(["Year_of_Release", "Platform"])[metric]
    .sum()
    .reset_index()
)

fig1 = px.line(
    df_platform,
    x="Year_of_Release",
    y=metric,
    color="Platform",
    title=f"Andamento delle vendite per piattaforma ({metric})",
    markers=True
)
fig1.update_layout(legend_title_text="Piattaforma")

st.plotly_chart(fig1, use_container_width=True)

trend_platform = df_platform.groupby("Platform")[metric].sum().idxmax()
st.info(f"La piattaforma con la crescita complessiva maggiore nel periodo analizzato è **{trend_platform}**.")


st.subheader("Vendite nel tempo per genere")

df_genre = (
    df[df["Genre"].isin(top_genres["Genre"])]
    .groupby(["Year_of_Release", "Genre"])[metric]
    .sum()
    .reset_index()
)

fig2 = px.line(
    df_genre,
    x="Year_of_Release",
    y=metric,
    color="Genre",
    title=f"Andamento delle vendite per genere ({metric})",
    markers=True
)
fig2.update_layout(legend_title_text="Genere")

st.plotly_chart(fig2, use_container_width=True)

trend_genre = df_genre.groupby("Genre")[metric].sum().idxmax()
st.info(f"Il genere con la crescita complessiva maggiore nel periodo analizzato è **{trend_genre}**.")

st.success("Analisi completata! Puoi cambiare metrica e numero di categorie dai filtri sopra per generare insight immediati.")
