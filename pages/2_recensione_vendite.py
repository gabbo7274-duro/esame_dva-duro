import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

df = st.session_state["df"]

df_scores = df.dropna(subset=["Global_Sales", "Critic_Score", "User_Score"])

# Gestione  NaN 
years = df_scores["Year_of_Release"].dropna()
if len(years) > 0:
    year_min = int(years.min())
    year_max = int(years.max())


# FILTRI 

st.sidebar.markdown(" Filtri pagina recensioni")
year_range = st.sidebar.slider(
    "Anno di uscita",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1
)

platforms = sorted(df_scores["Platform"].dropna().unique())
platform_filter = st.sidebar.multiselect(
    "Piattaforme (opzionale)",
    options=platforms,
    default=[]
)

genres = sorted(df_scores["Genre"].dropna().unique())
genre_filter = st.sidebar.multiselect(
    "Generi (opzionale)",
    options=genres,
    default=[]
)

df_filtered = df_scores[
    (df_scores["Year_of_Release"] >= year_range[0]) &
    (df_scores["Year_of_Release"] <= year_range[1])
]

if platform_filter:
    df_filtered = df_filtered[df_filtered["Platform"].isin(platform_filter)]

if genre_filter:
    df_filtered = df_filtered[df_filtered["Genre"].isin(genre_filter)]

#st.caption(f"Giochi considerati nel filtro corrente: **{len(df_filtered)}**")




st.title(" Recensioni & impatto sulle vendite")

st.markdown("""
In questa sezione analizziamo quanto le recensioni  sia della critica che degli utenti influenzano le vendite di un videogioco.



 Un gioco con buone recensioni vende davvero di più?

Qui sotto esploriamo il rapporto tra valutazioni e performance commerciali, possiamo  osservare:
- come cambiano le vendite al variare del Critic Score  
- quanto conta il User Score nel passaparola e nelle vendite  
- come la qualità percepita si riflette nella probabilità che un gioco diventi un HIT


""")

st.markdown("---")


# 1) CRITIC SCORE vs GLOBAL SALES

st.subheader(" Critica professionale vs vendite globali")

st.markdown("""
Ogni punto rappresenta un gioco.  
L’obiettivo è capire se un metascore alto si traduce in più copie vendute.
""")

sales_cap = st.slider(
    "Limite massimo vendite da visualizzare (milioni di copie)",
    min_value=1,
    max_value=int(np.ceil(df_filtered["Global_Sales"].max())),
    value=min(10, int(np.ceil(df_filtered["Global_Sales"].max()))),
)

df_plot_critic = df_filtered[df_filtered["Global_Sales"] <= sales_cap]

fig_critic = px.scatter(
    df_plot_critic,
    x="Critic_Score",
    y="Global_Sales",
    color="Is_Hit" if "Is_Hit" in df_filtered.columns else None,
    hover_data=["Name", "Platform", "Year_of_Release"],
    trendline="ols",
    labels={
        "Critic_Score": "Valutazione critica (metascore)",
        "Global_Sales": "Vendite globali (milioni)"
    },
    title="Relazione tra Critic Score e vendite globali"
)
st.plotly_chart(fig_critic, use_container_width=True)

st.caption("""
 Se la nuvola di punti e la retta di trend sono crescente, i giochi con voti migliori dalla critica tendono a vendere di più.
""")




# 2) USER SCORE vs GLOBAL SALES

st.subheader(" Valutazioni utenti vs vendite globali")

st.markdown("""
Qui analizziamo se il passaparola degli utenti (user score) è allineato o meno all’andamento delle vendite.
""")

df_plot_user = df_filtered[df_filtered["Global_Sales"] <= sales_cap]

fig_user = px.scatter(
    df_plot_user,
    x="User_Score",
    y="Global_Sales",
    color="Is_Hit" if "Is_Hit" in df_filtered.columns else None,
    hover_data=["Name", "Platform", "Year_of_Release"],
    trendline="ols",
    labels={
        "User_Score": "Valutazione media utenti",
        "Global_Sales": "Vendite globali (milioni)"
    },
    title="Relazione tra User Score e vendite globali"
)
st.plotly_chart(fig_user, use_container_width=True)

st.caption("""
 Un trend crescente suggerisce che giochi apprezzati dagli utenti generano più vendite.
""")

st.markdown("---")


# 3) RATING ESRB vs VENDITE

st.subheader(" Rating ESRB e vendite: quali fasce di pubblico sono più profittevoli?")

if "Rating" in df_filtered.columns:
    df_rating = (
        df_filtered.dropna(subset=["Rating"])
        .groupby("Rating")
        .agg(
            Vendite_medie=("Global_Sales", "mean"),
            Vendite_totali=("Global_Sales", "sum"),
            Numero_giochi=("Name", "count")
        )
        .reset_index()
        .sort_values("Vendite_totali", ascending=False)
    )

    fig_rating = px.bar(
        df_rating,
        x="Rating",
        y="Vendite_totali",
        text="Numero_giochi",
        labels={
            "Rating": "Rating ESRB",
            "Vendite_totali": "Vendite globali totali (milioni)"
        },
        title="Vendite totali per Rating ESRB (dimensione catalogo in etichetta)"
    )
    st.plotly_chart(fig_rating, use_container_width=True)

    st.caption("""
     Questa vista aiuta a capire quali fasce di età (E, T, M, …) generano più vendite complessive,
    tenendo conto anche di quanti titoli abbiano pubblicato per ogni rating.
    """)
else:
    st.info("Il campo 'Rating' non è disponibile nel dataset filtrato.")
