import streamlit as st
import pandas as pd
import joblib
from pathlib import Path


st.set_page_config(page_title="Credit Scoring", page_icon="💳", layout="centered")
st.title("Probabilidad de default (90+ días)")

MODEL_PATH = Path("best_model.pkl")


@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        st.error("No se encontró best_model.pkl. Entrena el modelo primero (train.py o notebook).")
        st.stop()
    return joblib.load(MODEL_PATH)


model = load_model()

st.write("Ingresa las características del solicitante:")

fields = {
    "RevolvingUtilizationOfUnsecuredLines": st.number_input(
        "Utilización de líneas no garantizadas", 0.0, 10.0, 0.2, step=0.01
    ),
    "age": st.number_input("Edad", 18, 120, 40, step=1),
    "NumberOfTime30-59DaysPastDueNotWorse": st.number_input(
        "Atrasos 30-59 días (últ. 2 años)", 0, 20, 0, step=1
    ),
    "DebtRatio": st.number_input("DebtRatio", 0.0, 1000.0, 0.5, step=0.01),
    "MonthlyIncome": st.number_input("Ingreso mensual", 0.0, 1_000_000.0, 5000.0, step=100.0),
    "NumberOfOpenCreditLinesAndLoans": st.number_input("Líneas/préstamos abiertos", 0, 50, 5, step=1),
    "NumberOfTimes90DaysLate": st.number_input("Atrasos 90+ días", 0, 20, 0, step=1),
    "NumberRealEstateLoansOrLines": st.number_input("Préstamos/CRÉ inmobiliarios", 0, 20, 1, step=1),
    "NumberOfTime60-89DaysPastDueNotWorse": st.number_input(
        "Atrasos 60-89 días (últ. 2 años)", 0, 20, 0, step=1
    ),
    "NumberOfDependents": st.number_input("Dependientes", 0.0, 20.0, 0.0, step=1.0),
}

if st.button("Calcular probabilidad"):
    X_new = pd.DataFrame([fields])
    prob = model.predict_proba(X_new)[0, 1]
    st.metric("Probabilidad de default (90+ días)", f"{prob*100:.2f}%")
    st.progress(min(prob, 1.0))
