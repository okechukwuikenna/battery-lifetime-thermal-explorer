# core/sim_engine.py
import pybamm
import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def run_comparison_sim(fast_charge_C, discharge_C, upper_v, lower_v, cycles=3):
    """Runs both SPM and DFN under identical conditions for comparison."""
    experiment = pybamm.Experiment([
        (f"Charge at {fast_charge_C}C until {upper_v} V",
         f"Hold at {upper_v} V until C/20",
         f"Discharge at {discharge_C}C until {lower_v} V")
    ] * cycles)
    
    # Run SPM
    spm = pybamm.lithium_ion.SPM()
    sim_spm = pybamm.Simulation(model=spm, experiment=experiment)
    sol_spm = sim_spm.solve()
    
    # Run DFN
    dfn = pybamm.lithium_ion.DFN()
    sim_dfn = pybamm.Simulation(model=dfn, experiment=experiment)
    sol_dfn = sim_dfn.solve()
    
    return sol_spm, sol_dfn

@st.cache_data(show_spinner=False)
def run_degradation_sim(sei_option, plating_option, lam_option, cycles=5):
    """Runs a DFN model equipped with custom physical degradation submodels."""
    options = {
        "SEI": sei_option,
        "lithium plating": plating_option,
        "loss of active material": lam_option
    }
    
    model = pybamm.lithium_ion.DFN(options=options)
    experiment = pybamm.Experiment([
        ("Charge at 2C until 4.2 V", 
         "Hold at 4.2 V until C/20", 
         "Discharge at 1C until 3.0 V")
    ] * cycles)
    
    sim = pybamm.Simulation(model=model, experiment=experiment)
    try:
        sol = sim.solve()
        return sol
    except Exception as e:
        st.error(f"Simulation failed with current configuration: {e}")
        return None

@st.cache_data(show_spinner=False)
def run_thermal_sim(ambient_temp_C, C_rate, thermal_option="lumped"):
    """Runs an SPM coupled with a lumped thermal model."""
    options = {"thermal": thermal_option}
    model = pybamm.lithium_ion.SPM(options=options)
    
    # Set ambient temperature parameter
    param = model.default_parameter_values
    param.update({"Initial temperature [K]": ambient_temp_C + 273.15,
                  "Ambient temperature [K]": ambient_temp_C + 273.15})
    
    experiment = pybamm.Experiment([
        (f"Discharge at {C_rate}C until 3.0 V",)
    ])
    
    sim = pybamm.Simulation(model=model, parameter_values=param, experiment=experiment)
    return sim.solve()