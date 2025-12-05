import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("⭐ Recensioni & impatto sulle vendite")

st.markdown("""
Questa pagina risponde alla domanda:

> **Quanto contano le recensioni (critica & utenti) e il rating ESRB sul successo commerciale di un gioco?**

I grafici e gli indicatori sotto aiutano il management a capire **se conviene investire in qualità critica/
user experience** oppure spingere solo su marketing e IP esistenti.
""")

# -------------------------------------------------------
# DATI DI LAVORO
# -------------------------------------------------------
df = st.session_state["df"]

# Filtriamo solo i record con informazioni utili
df_scores = df.dropna(subset=["Global_Sales", "Critic_Score", "User_Score"])

# Gestione anni (rimuovo NaN sugli anni per i filtri)
years = df_scores["Year_of_Release"].dropna()
if len(years) > 0:
    year_min = int(years.min())
    year_max = int(years.max())
else:
    year_min, year_max = 2000, 2020  # fallback

# -------------------------------------------------------
# FILTRI EXECUTIVE-FRIENDLY
# -------------------------------------------------------
st.sidebar.markdown("### 🔎 Filtri pagina recensioni")
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

st.caption(f"Giochi considerati nel filtro corrente: **{len(df_filtered)}**")

# -------------------------------------------------------
# KPI PRINCIPALI: CORRELAZIONE RECENSIONI vs VENDITE
# -------------------------------------------------------
col1, col2, col3 = st.columns(3)

if len(df_filtered) > 10:
    corr_critic = df_filtered["Critic_Score"].corr(df_filtered["Global_Sales"])
    corr_user = df_filtered["User_Score"].corr(df_filtered["Global_Sales"])

    # Probabilità media di HIT (Is_Hit viene creato in app.py)
    if "Is_Hit" in df_filtered.columns:
        hit_rate = df_filtered["Is_Hit"].mean()
    else:
        hit_rate = (df_filtered["Global_Sales"] >= 1.0).mean()

    col1.metric("Correlazione Critic Score / vendite", f"{corr_critic:.2f}")
    col2.metric("Correlazione User Score / vendite", f"{corr_user:.2f}")
    col3.metric("Quota HIT nel campione", f"{hit_rate*100:.1f}%")
else:
    col1.write("Dataset troppo piccolo per KPI affidabili.")
    col2.empty()
    col3.empty()

st.markdown("""
💡 **Lettura veloce**  
- Valori vicini a **0.5–0.7** indicano una relazione forte: i giochi con valutazioni alte vendono sensibilmente di più.  
- Valori vicini a **0** indicano che la recensione pesa poco rispetto ad altri driver (brand, marketing, piattaforma, IP, ecc.).
""")

st.markdown("---")

# -------------------------------------------------------
# 1) CRITIC SCORE vs GLOBAL SALES
# -------------------------------------------------------
st.subheader("1️⃣ Critica professionale vs vendite globali")

st.markdown("""
Ogni punto rappresenta un gioco.  
L’obiettivo è capire se **un metascore alto** si traduce in **più copie vendute**.
""")

# Per evitare che pochi outlier schiaccino il grafico:
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
📌 Se la nuvola di punti e la retta di trend sono **crescente**, i giochi con voti migliori dalla critica tendono a vendere di più.
""")

st.markdown("---")

# -------------------------------------------------------
# 2) USER SCORE vs GLOBAL SALES
# -------------------------------------------------------
st.subheader("2️⃣ Valutazioni utenti vs vendite globali")

st.markdown("""
Qui analizziamo se il **passaparola degli utenti** (user score) è allineato o meno all’andamento delle vendite.
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
📌 Un trend **crescente** suggerisce che giochi apprezzati dagli utenti generano più vendite
(o mantengono vendite solide grazie al passaparola).
""")

st.markdown("---")

# -------------------------------------------------------
# 3) BUCKET DI SCORE E PROBABILITÀ DI HIT
# -------------------------------------------------------
st.subheader("3️⃣ Quanto aumentano le chance di HIT con buone recensioni?")

st.markdown("""
Qui raggruppiamo i giochi in **fasce di valutazione** e misuriamo la **probabilità di HIT**
(≥ 1M copie) in ciascuna fascia.
""")

# Se Is_Hit non fosse presente per qualche motivo, lo ricreiamo
if "Is_Hit" not in df_filtered.columns:
    df_filtered["Is_Hit"] = (df_filtered["Global_Sales"] >= 1.0).astype(int)

def bucket_user(score):
    if pd.isna(score):
        return np.nan
    if score < 6:
        return "Bassa (<6)"
    elif score < 8:
        return "Media (6-8)"
    else:
        return "Alta (8-10)"

def bucket_critic(score):
    if pd.isna(score):
        return np.nan
    if score < 60:
        return "Bassa (<60)"
    elif score < 80:
        return "Media (60-80)"
    else:
        return "Alta (80-100)"

df_buckets = df_filtered.copy()
df_buckets["Fascia_User_Score"] = df_buckets["User_Score"].apply(bucket_user)
df_buckets["Fascia_Critic_Score"] = df_buckets["Critic_Score"].apply(bucket_critic)

# Probabilità di HIT per fascia User Score
hit_by_user_bucket = (
    df_buckets.dropna(subset=["Fascia_User_Score"])
    .groupby("Fascia_User_Score")["Is_Hit"]
    .mean()
    .reindex(["Bassa (<6)", "Media (6-8)", "Alta (8-10)"])
    * 100
)

# Probabilità di HIT per fascia Critic Score
hit_by_critic_bucket = (
    df_buckets.dropna(subset=["Fascia_Critic_Score"])
    .groupby("Fascia_Critic_Score")["Is_Hit"]
    .mean()
    .reindex(["Bassa (<60)", "Media (60-80)", "Alta (80-100)"])
    * 100
)

col_u, col_c = st.columns(2)

with col_u:
    fig_hit_user = px.bar(
        hit_by_user_bucket.dropna().reset_index(),
        x="Fascia_User_Score",
        y="Is_Hit",
        labels={"Fascia_User_Score": "Fascia User Score", "Is_Hit": "% HIT"},
        title="Probabilità di HIT per fascia User Score"
    )
    st.plotly_chart(fig_hit_user, use_container_width=True)

with col_c:
    fig_hit_critic = px.bar(
        hit_by_critic_bucket.dropna().reset_index(),
        x="Fascia_Critic_Score",
        y="Is_Hit",
        labels={"Fascia_Critic_Score": "Fascia Critic Score", "Is_Hit": "% HIT"},
        title="Probabilità di HIT per fascia Critic Score"
    )
    st.plotly_chart(fig_hit_critic, use_container_width=True)

st.caption("""
📌 Questi grafici rispondono in modo diretto al management:
**quanto aumenta la probabilità di successo commerciale se il gioco supera certe soglie di valutazione?**
""")

st.markdown("---")

# -------------------------------------------------------
# 4) RATING ESRB vs VENDITE
# -------------------------------------------------------
st.subheader("4️⃣ Rating ESRB e vendite: quali fasce di pubblico sono più profittevoli?")

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
    📌 Questa vista aiuta a capire **quali fasce di età (E, T, M, …)** generano più vendite complessive,
    tenendo conto anche di **quanti titoli** abbiamo pubblicato per ogni rating.
    """)
else:
    st.info("Il campo 'Rating' non è disponibile nel dataset filtrato.")
