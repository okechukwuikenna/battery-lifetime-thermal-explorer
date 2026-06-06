# pages/3_Thermal_Analysis.py
import streamlit as st
import matplotlib.pyplot as plt
from core.sim_engine import run_thermal_sim

st.title("🔥 Lumped Thermal Explorer")
st.markdown("Observe how ambient environmental temperatures and internal Joule heating interact via **Arrhenius dynamics**.")

ambient_t = st.sidebar.slider("Ambient Temperature (°C)", 0, 50, 25)
c_rate = st.sidebar.slider("Discharge Rate (C-rate)", 0.5, 5.0, 3.0, step=0.5)

if st.sidebar.button("Execute Thermal Sweep"):
    with st.spinner("Simulating core thermal transients..."):
        sol = run_thermal_sim(ambient_t, c_rate)
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cell Temperature Over Time")
        fig, ax = plt.subplots()
        ax.plot(sol["Time [s]"].entries / 60, sol["Volume-averaged cell temperature [K]"].entries - 273.15, color="orange", lw=2)
        ax.axhline(ambient_t, color="blue", linestyle=":", label="Ambient Boundary")
        ax.set_xlabel("Time [mins]")
        ax.set_ylabel("Temperature [°C]")
        ax.legend()
        st.pyplot(fig)
        
    with col2:
        st.subheader("Thermal Physics Summary")
        max_t = sol["Volume-averaged cell temperature [K]"].entries.max() - 273.15
        st.metric("Peak Internal Temperature Reached", f"{max_t:.2f} °C")
        st.write(f"""
        **Arrhenius Behavior Note:** Chemical degradation rates scale exponentially according to the classic relationship:
        """)
        st.latex(r"k = A \exp\left(-\frac{E_a}{R T}\right)")
        st.write("A higher discharge C-rate accelerates internal heat generation, increasing temperature ($T$) and exponentially driving up parasitic side reactions.")