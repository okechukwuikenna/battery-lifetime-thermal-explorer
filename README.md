# Battery Lifetime & Thermal Explorer

An advanced, interactive multi-page Streamlit web application designed for the multi-scale modeling, simulation, and prognostic analysis of lithium-ion battery systems. This platform bridges physics-based electrochemical modeling with data-driven machine learning frameworks to evaluate battery degradation, health diagnostics, and thermal behaviors.

## 🚀 Core Features

The framework is divided into dedicated functional modules:
* **RPT (Reference Performance Test) Simulation:** Evaluates capacity retention and resistance growth over standardized test cycles.
* **Degradation Physics:** Models internal electrochemical aging mechanisms (e.g., SEI growth, lithium inventory loss, active material loss) using physical equations.
* **Thermal Analysis:** Investigates heat generation, temperature distribution, and thermal management impacts on cell longevity.
* **Model Comparison:** Benchmarks different electrochemical models against experimental data curves.
* **Machine Learning Prognostics:** Leverages data-driven models (such as `RandomForestRegressor`) to predict Remaining Useful Life (RUL) and State of Health (SOH).

## 🛠️ Tech Stack & Libraries

* **Frontend UI:** Streamlit (Multi-page architecture)
* **Electrochemical Engine:** PyBaMM (Python Battery Mathematical Modelling)
* **Machine Learning:** Scikit-Learn
* **Data Processing:** NumPy, Pandas
* **Visualization:** Matplotlib, Plotly

## 📂 Repository Structure

```text
├── pages/
│   ├── RPT_Simulation.py
│   ├── Model_Comparison.py
│   ├── Degradation_Physics.py
│   ├── Thermal_Analysis.py
│   └── Machine_Learning.py
├── core/
│   └── sim_engine.py       # Core computational backend
├── app.py                  # Streamlit application entry point
└── requirements.txt        # Managed cloud deployment dependencies
