# pages/Degradation_Physics.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pybamm

st.title("🔬 Degradation Physics Sandbox")
st.markdown("""
Isolate specific electrochemical failure mechanisms. This module tracks **Solid Electrolyte Interphase (SEI)** thickness growth and lithium inventory loss over time.
""")

st.sidebar.header("Degradation Settings")
# FIX: The strings must exactly match PyBaMM's internal option parser (spaces, not hyphens!)
sei_scheme = st.sidebar.selectbox(
    "SEI Growth Kinetic Scheme", 
    ["constant", "reaction limited", "solvent-diffusion limited", "electron-migration limited"]
)
cycles = st.sidebar.slider("Number of cycles to evaluate", 1, 10, 2)
run_deg = st.sidebar.button("Simulate Degradation Dynamics")

if run_deg:
    with st.spinner("Compiling model with degradation submodels..."):
        # PyBaMM requires the uppercase "SEI" key and perfectly matched string values
        try:
            model = pybamm.lithium_ion.DFN(
                options={"SEI": sei_scheme}
            )
        except pybamm.OptionError:
            # Safe fallback just in case an older PyBaMM version uses lowercase "sei"
            model = pybamm.lithium_ion.DFN(
                options={"sei": sei_scheme}
            )
        
        experiment = pybamm.Experiment([
            (
                "Charge at 1C until 4.2 V",
                "Hold at 4.2 V until C/20",
                "Discharge at 1C until 3.0 V"
            )
        ] * cycles)
        
        sim = pybamm.Simulation(model=model, experiment=experiment)
        sol = sim.solve()

    # ---- Safe Variable Extraction ----
    available_vars = list(model.variables.keys())
    
    sei_thickness_key = None
    for var in available_vars:
        if "sei thickness" in var.lower() and "[m]" in var.lower():
            if "total" in var.lower() or "x-averaged" in var.lower():
                sei_thickness_key = var
                break
            sei_thickness_key = var

    # ---- Plotting Results ----
    if sei_thickness_key:
        st.subheader("🔋 SEI Layer Proliferation Over Time")
        
        time_hours = sol["Time [h]"].entries
        sei_thickness_nm = sol[sei_thickness_key].entries * 1e9  # Convert meters to nanometers
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(time_hours, sei_thickness_nm, color="crimson", lw=2, label=f"Scheme: {sei_scheme}")
        ax.set_xlabel("Time [hours]")
        ax.set_ylabel("SEI Thickness [nm]")
        ax.set_title("Anode SEI Layer Growth Passivation Track")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig)
        
        final_thickness = sei_thickness_nm[-1]
        growth = final_thickness - sei_thickness_nm[0]
        
        col1, col2 = st.columns(2)
        col1.metric("Final SEI Thickness", f"{final_thickness:.2f} nm")
        col2.metric("Net Growth Profile", f"+{growth:.4f} nm", delta_color="inverse")
    else:
        st.error("Could not find SEI Thickness variables in this PyBaMM solution configuration.")
        st.write("Available variables matching your submodel choice:", [v for v in available_vars if "sei" in v.lower()][:10])
else:
    st.info("Select an SEI growth mechanism in the sidebar and click **Simulate Degradation Dynamics**.")