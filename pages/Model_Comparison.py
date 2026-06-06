# pages/1_Model_Comparison.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pybamm
import time

st.title("⚖️ Model Comparison: SPM vs DFN")
st.markdown("""
Evaluate the engineering trade-offs between **Single Particle Model (SPM)** and **Doyle-Fuller-Newman (DFN)**.
* **SPM:** Extremely fast, great for rapid prototyping, lacks electrolyte dynamics.
* **DFN:** Full physics-based fidelity, tracks macro-scale gradients, computationally intensive.
""")

st.sidebar.header("Comparison Parameters")
c_rate = st.sidebar.slider("Discharge C-rate for comparison", 0.5, 3.0, 1.0, step=0.5)
run_comparison = st.sidebar.button("Run Comparison Profile")

if run_comparison:
    with st.spinner("Simulating both models simultaneously..."):
        # 1. SPM Simulation
        t0_spm = time.time()
        model_spm = pybamm.lithium_ion.SPM()
        sim_spm = pybamm.Simulation(model_spm)
        sol_spm = sim_spm.solve(t_eval=np.linspace(0, 3600, 100), inputs={"C-rate": c_rate})
        t_spm = time.time() - t0_spm

        # 2. DFN Simulation
        t0_dfn = time.time()
        model_dfn = pybamm.lithium_ion.DFN()
        sim_dfn = pybamm.Simulation(model_dfn)
        sol_dfn = sim_dfn.solve(t_eval=np.linspace(0, 3600, 100), inputs={"C-rate": c_rate})
        t_dfn = time.time() - t0_dfn

    # ---- Metrics Display ----
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="SPM Solve Time", value=f"{t_spm:.3f} sec", delta="Fast Baseline")
    with col2:
        st.metric(label="DFN Solve Time", value=f"{t_dfn:.3f} sec", delta=f"{t_dfn/max(0.001, t_spm):.1f}x Slower", delta_color="inverse")

    # ---- Plotting Comparison ----
    st.subheader("Terminal Voltage Discrepancy Profile")
    fig, ax = plt.subplots(figsize=(10, 4))
    
    ax.plot(sol_spm["Time [min]"].entries, sol_spm["Terminal voltage [V]"].entries, label="SPM (Simplified Physics)", linestyle="--", color="orange")
    ax.plot(sol_dfn["Time [min]"].entries, sol_dfn["Terminal voltage [V]"].entries, label="DFN (Full Electrochemical Fidelity)", color="dodgerblue")
    
    ax.set_xlabel("Time [min]")
    ax.set_ylabel("Terminal Voltage [V]")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.6)
    st.pyplot(fig)

    st.info("💡 **Observation:** Notice how at higher C-rates, SPM deviates from DFN because it neglects the salt concentration gradients inside the liquid electrolyte.")
else:
    st.info("Adjust the comparison settings in the sidebar and click **Run Comparison Profile** to generate the physics benchmark.")