import streamlit as st
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

st.title("🤖 Modello ML — Predizione HIT")

df = st.session_state["df"]

features = ["Critic_Score", "User_Score", "Critic_Count", "User_Count", "Year_of_Release"]
df_clean = df.dropna(subset=features)

X = df_clean[features]
y = df_clean["Is_Hit"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

model = RandomForestClassifier(n_estimators=200)
model.fit(X_train, y_train)

preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)

st.subheader(f"📌 Accuratezza modello: **{acc:.2f}**")

# INPUT UTENTE
st.markdown("### Inserisci le caratteristiche del nuovo gioco")

critic = st.slider("Critic Score", 0, 100, 70)
user = st.slider("User Score", 0.0, 10.0, 8.0)
cc = st.slider("Critic Count", 0, 300, 50)
uc = st.slider("User Count", 0, 10000, 500)
year = st.number_input("Anno di uscita", 1980, 2030, 2020)

X_new = np.array([[critic, user, cc, uc, year]])
proba = model.predict_proba(X_new)[0][1]

st.subheader(f"🎯 Probabilità che sia un HIT: **{proba*100:.1f}%**")
