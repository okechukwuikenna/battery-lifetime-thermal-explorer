# pages/0_RPT_Simulation.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pybamm

# ---- Page config ----
st.set_page_config(
    page_title="Battery Lifetime & Thermal Explorer",
    layout="wide",
)

st.title("🔋 Battery Lifetime & Thermal Explorer")
st.markdown(
    "Interactive PyBaMM-based app for exploring **fast charging and degradation**."
)

# ---- Sidebar: user inputs ----
st.sidebar.header("Simulation setup")

model_type = st.sidebar.selectbox(
    "Model type", ["DFN (Doyle–Fuller–Newman)", "SPM (Single Particle Model)"]
)

n_blocks = st.sidebar.slider("Number of ageing blocks (with RPT)", 1, 10, 3)
n_ageing_cycles_per_block = st.sidebar.slider(
    "Ageing cycles per block", 5, 50, 10, step=5
)

fast_charge_C = st.sidebar.slider(
    "Fast charge C-rate", 1.0, 5.0, 3.0, step=0.5
)
discharge_C = st.sidebar.slider(
    "Discharge C-rate", 0.5, 3.0, 1.0, step=0.5
)
rpt_discharge_C = st.sidebar.slider(
    "RPT discharge C-rate", 0.2, 1.0, 0.33, step=0.1
)

upper_voltage = st.sidebar.number_input(
    "Upper cut-off voltage [V]", 3.8, 4.4, 4.2, step=0.05
)
lower_voltage = st.sidebar.number_input(
    "Lower cut-off voltage [V]", 2.5, 3.2, 3.0, step=0.05
)

st.sidebar.checkbox(
    "Enable simple thermal model (coming soon)", value=False, disabled=True
)
st.sidebar.checkbox(
    "Enable explicit degradation submodels (coming soon)", value=False, disabled=True
)

run_sim = st.sidebar.button("Run simulation")

summary_placeholder = st.empty()
plot_col1, plot_col2 = st.columns(2)
data_placeholder = st.expander("Show raw RPT data (capacity vs index)", expanded=False)

@st.cache_data(show_spinner=False)
def run_pybamm_sim(
    model_type,
    n_blocks,
    n_ageing_cycles_per_block,
    fast_charge_C,
    discharge_C,
    rpt_discharge_C,
    upper_voltage,
    lower_voltage,
):
    if model_type.startswith("DFN"):
        model = pybamm.lithium_ion.DFN()
    else:
        model = pybamm.lithium_ion.SPM()

    param = model.default_parameter_values

    ageing_cycle = [(
        f"Charge at {fast_charge_C}C until {upper_voltage} V",
        f"Hold at {upper_voltage} V until C/20",
        "Rest for 10 minutes",
        f"Discharge at {discharge_C}C until {lower_voltage} V",
        "Rest for 20 minutes",
    )]

    rpt_cycle = [(
        f"Charge at 1C until {upper_voltage} V",
        f"Hold at {upper_voltage} V until C/50",
        "Rest for 20 minutes",
        f"Discharge at {rpt_discharge_C}C until {lower_voltage} V",
        "Rest for 30 minutes",
    )]

    experiment_steps = []
    for _ in range(n_blocks):
        experiment_steps += ageing_cycle * n_ageing_cycles_per_block
        experiment_steps += rpt_cycle

    experiment = pybamm.Experiment(experiment_steps)

    sim = pybamm.Simulation(model=model, parameter_values=param, experiment=experiment)
    solution = sim.solve()

    rpt_capacities = []
    rpt_indices = []
    rpt_counter = 0

    n_cycles = len(solution.cycles)
    cycles_per_block = n_ageing_cycles_per_block + 1

    for cycle_idx in range(n_cycles):
        cycle = solution.cycles[cycle_idx]
        is_rpt_cycle = (cycle_idx + 1) % cycles_per_block == 0
        
        for step_idx, step_sol in enumerate(cycle.steps):
            step_desc = str(experiment.cycles[cycle_idx][step_idx]).lower()

            if is_rpt_cycle and "discharge" in step_desc:
                try:
                    cap = step_sol["Discharge capacity [A.h]"].entries[-1]
                except KeyError:
                    current = step_sol["Current [A]"].entries
                    t_local = step_sol["Time [s]"].entries
                    cap = np.trapz(-current, t_local) / 3600.0

                rpt_counter += 1
                rpt_capacities.append(cap)
                rpt_indices.append(rpt_counter)

    df_rpt = pd.DataFrame({"RPT_index": rpt_indices, "capacity_Ah": rpt_capacities})

    voltage_curves = {}
    if rpt_counter >= 1:
        def get_rpt_step(k):
            counter = 0
            for cycle_idx in range(len(solution.cycles)):
                cycle = solution.cycles[cycle_idx]
                is_rpt_cycle = (cycle_idx + 1) % cycles_per_block == 0
                
                for step_idx, step_sol in enumerate(cycle.steps):
                    step_desc = str(experiment.cycles[cycle_idx][step_idx]).lower()
                    if is_rpt_cycle and "discharge" in step_desc:
                        counter += 1
                        if counter == k:
                            return step_sol
            return None

        first_step = get_rpt_step(1)
        last_step = get_rpt_step(rpt_counter)

        if first_step is not None:
            voltage_curves["first"] = {
                "time_min": first_step["Time [s]"].entries / 60.0,
                "voltage": first_step["Terminal voltage [V]"].entries,
            }
        if last_step is not None:
            voltage_curves["last"] = {
                "time_min": last_step["Time [s]"].entries / 60.0,
                "voltage": last_step["Terminal voltage [V]"].entries,
            }

    return df_rpt, voltage_curves

if run_sim:
    with st.spinner("Running PyBaMM simulation... this may take a bit."):
        df_rpt, voltage_curves = run_pybamm_sim(
            model_type,
            n_blocks,
            n_ageing_cycles_per_block,
            fast_charge_C,
            discharge_C,
            rpt_discharge_C,
            upper_voltage,
            lower_voltage,
        )

    if not df_rpt.empty:
        initial_cap = df_rpt["capacity_Ah"].iloc[0]
        final_cap = df_rpt["capacity_Ah"].iloc[-1]
        fade_pct = 100 * (1 - final_cap / initial_cap)

        summary_placeholder.markdown(
            f"""
            **Simulation complete.** Initial RPT capacity: {initial_cap:.3f} A·h  
            Final RPT capacity: {final_cap:.3f} A·h  
            Approximate capacity fade: {fade_pct:.1f} %
            """
        )

        with plot_col1:
            fig1, ax1 = plt.subplots(figsize=(5, 4))
            ax1.plot(df_rpt["RPT_index"], df_rpt["capacity_Ah"], marker="o")
            ax1.set_xlabel("RPT index (-)")
            ax1.set_ylabel("Capacity [A·h]")
            ax1.set_title("Capacity vs RPT index")
            st.pyplot(fig1)

        with plot_col2:
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            if "first" in voltage_curves:
                ax2.plot(voltage_curves["first"]["time_min"], voltage_curves["first"]["voltage"], label="First RPT")
            if "last" in voltage_curves:
                ax2.plot(voltage_curves["last"]["time_min"], voltage_curves["last"]["voltage"], label="Last RPT")
            ax2.set_xlabel("Time [min]")
            ax2.set_ylabel("Voltage [V]")
            ax2.set_title("Voltage vs time (RPT discharge)")
            ax2.legend()
            st.pyplot(fig2)

        with data_placeholder:
            st.dataframe(df_rpt)
            csv = df_rpt.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download RPT dataset (CSV)",
                data=csv,
                file_name="rpt_capacity_dataset.csv",
                mime="text/csv",
            )
    else:
        summary_placeholder.warning("No RPT points found.")
else:
    st.info("Configure parameters in the sidebar, then click **Run simulation**.")