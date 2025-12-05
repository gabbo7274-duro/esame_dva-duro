import streamlit as st
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from category_encoders import TargetEncoder
import xgboost as xgb

st.title("📈 Modello ML — Predizione vendite globali")

df = st.session_state["df"]
df = df.dropna(subset=[
    "Platform", "Publisher", "Developer",
    "Genre", "Rating", "Critic_Score",
    "Critic_Count", "User_Score",
    "User_Count", "Year_of_Release"
])

one_hot_cols = ["Genre", "Rating"]
target_enc_cols = ["Platform", "Publisher", "Developer"]

numeric_cols = [
    "Critic_Score", "Critic_Count", "User_Score",
    "User_Count", "Year_of_Release"
]

all_features = one_hot_cols + target_enc_cols + numeric_cols

X = df[all_features].copy()
y = df["Global_Sales"]


te = TargetEncoder(cols=target_enc_cols)
X[target_enc_cols] = te.fit_transform(X[target_enc_cols], y)


X = pd.get_dummies(X, columns=one_hot_cols, drop_first=True)


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)


model = xgb.XGBRegressor(
    n_estimators=133,
    learning_rate=0.038,
    max_depth=10,
    subsample=0.82,
    colsample_bytree=0.63,
    min_child_weight=1,
    objective="reg:squarederror"
)

model.fit(X_train, y_train)


preds = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, preds))

st.subheader(f"📌 RMSE: **{rmse:.2f}** milioni")


importances = model.feature_importances_
encoded_cols = X_train.columns

rows = []
for col, imp in zip(encoded_cols, importances):
    if col.startswith("Genre_"):
        orig = "Genre"
    elif col.startswith("Rating_"):
        orig = "Rating"
    else:
        orig = col
    rows.append((orig, imp))

imp_df = pd.DataFrame(rows, columns=["feature", "importance"]) \
           .groupby("feature", as_index=False)["importance"].sum() \
           .sort_values("importance", ascending=False)

st.subheader("Feature Importances (per variabile originale)")
st.bar_chart(imp_df.set_index("feature"))



st.markdown("### Inserisci i dati del nuovo gioco")

platform = st.selectbox("Platform", sorted(df["Platform"].dropna().unique()))
publisher = st.selectbox("Publisher", sorted(df["Publisher"].dropna().unique()))
developer = st.selectbox("Developer", sorted(df["Developer"].dropna().unique()))
genre = st.selectbox("Genre", sorted(df["Genre"].dropna().unique()))
rating = st.selectbox("Rating", sorted(df["Rating"].dropna().unique()))

critic = st.slider("Critic Score", 0, 100, 70)
user = st.slider("User Score", 0.0, 10.0, 8.0)
cc = st.slider("Critic Count", 0, 300, 50)
uc = st.slider("User Count", 0, 10000, 500)
year = st.number_input("Anno di uscita", 1980, 2030, 2020)


X_new = pd.DataFrame([{
    "Platform": platform,
    "Publisher": publisher,
    "Developer": developer,
    "Genre": genre,
    "Rating": rating,
    "Critic_Score": critic,
    "Critic_Count": cc,
    "User_Score": user,
    "User_Count": uc,
    "Year_of_Release": year
}])

X_new[target_enc_cols] = te.transform(X_new[target_enc_cols])

X_new = pd.get_dummies(X_new, columns=one_hot_cols, drop_first=True)

X_new = X_new.reindex(columns=X_train.columns, fill_value=0)


predicted_sales = model.predict(X_new)[0]

if st.button("Predici"):
    if predicted_sales >= 1.0:
        st.success(f"🎉 Il gioco è previsto come un **HIT** con vendite globali di circa **{predicted_sales:.2f} milioni**!")
    elif 0.8 <= predicted_sales < 1.0:
        st.warning(f"👍 Il gioco ha discrete probabilità di essere **HIT** con vendite globali di circa **{predicted_sales:.2f} milioni**.")
    else:
        st.error(f"⚠️ Il gioco potrebbe non essere **HIT**, con vendite globali previste di circa **{predicted_sales:.2f} milioni**.")