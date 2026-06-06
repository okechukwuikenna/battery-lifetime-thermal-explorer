# pages/4_Machine_Learning.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

st.title("🤖 High-Throughput ML Predictive Page")
st.markdown("Train a machine learning model on a synthetic multi-variable simulation run to predict cell End-of-Life (EOL).")

# Secure/Auto-generate background dataset if file is absent
@st.cache_data
def load_or_create_synthetic_data():
    try:
        df = pd.read_csv("data/synthetic_eol_data.csv")
    except FileNotFoundError:
        # Create a reliable mathematical surrogate data set mimicking battery wear
        np.random.seed(42)
        n_samples = 300
        c_rates = np.random.uniform(1.0, 4.5, n_samples)
        temps = np.random.uniform(10, 45, n_samples)
        dods = np.random.uniform(70, 100, n_samples)
        
        # EOL cycles heavily penalize high C-rate, high Temp, and high DOD
        eol_cycles = 1200 - (c_rates * 120) - (temps * 6) - (dods * 3) + np.random.normal(0, 25, n_samples)
        df = pd.DataFrame({"Charge_C_Rate": c_rates, "Ambient_Temp": temps, "DOD": dods, "Cycles_To_EOL": eol_cycles})
    return df

df_clean = load_or_create_synthetic_data()

st.subheader("Dataset Preview")
st.dataframe(df_clean.head(5), use_container_width=True)

# Interactive Parameter inputs for Realtime Prediction
st.sidebar.header("User Target Conditions")
user_c = st.sidebar.slider("Target Charge C-Rate", 1.0, 4.5, 2.5, step=0.1)
user_t = st.sidebar.slider("Target Operating Temp (°C)", 10, 45, 25, step=1)
user_dod = st.sidebar.slider("Target Depth of Discharge (%DOD)", 70, 100, 80, step=1)

if st.button("Train Predictive Random Forest Pipeline"):
    X = df_clean[["Charge_C_Rate", "Ambient_Temp", "DOD"]]
    y = df_clean["Cycles_To_EOL"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    with st.spinner("Fitting Regressor Tree structures..."):
        model.fit(X_train, y_train)
        
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    
    st.success("Model trained successfully!")
    st.metric("Pipeline Cross-Validation MAE Error", f"{mae:.2f} Cycles")
    
    # Run interactive real-time estimation
    prediction = model.predict([[user_c, user_t, user_dod]])[0]
    
    st.subheader("🔮 Predictive Insights Result")
    st.markdown(f"Given your custom operating conditions, the battery is estimated to survive for **{int(prediction)} cycles** before hit 80% EOL.")