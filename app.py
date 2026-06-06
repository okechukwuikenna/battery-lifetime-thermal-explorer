# app.py
import streamlit as st

# 1. Define the clean, professional entry point paths for every page
welcome_page = st.Page("app.py", title="Home", icon="🔋", default=True)

rpt_page = st.Page("pages/RPT_Simulation.py", title="RPT Simulation", icon="🔄")
model_page = st.Page("pages/Model_Comparison.py", title="Model Comparison", icon="⚖️")
deg_page = st.Page("pages/Degradation_Physics.py", title="Degradation Physics", icon="🔬")
thermal_page = st.Page("pages/Thermal_Analysis.py", title="Thermal Analysis", icon="🔥")
ml_page = st.Page("pages/Machine_Learning.py", title="Machine Learning", icon="🤖")

# 2. Assign the clean pages to the navigation engine sidebar groupings
pg = st.navigation({
    "Main Menu": [welcome_page],
    "Analytics Suite Modules": [rpt_page, model_page, deg_page, thermal_page, ml_page]
})

# 3. Configure the broad app viewport layout
st.set_page_config(page_title="Advanced Battery Analytics Suite", layout="wide")

# 4. Render layout conditionally based on selection
if pg == welcome_page:
    st.title("🔋 Advanced Electrochemical & Analytics Suite")
    st.markdown("""
    ### Welcome to the Top-Tier Battery Engineering Sandbox
    This multi-page application leverages physics-based modeling and machine learning to analyze cell performance, thermal dynamics, and degradation.

    **Use the sidebar on the left to navigate between modules:**
    * **🔄 RPT Simulation:** Your core reference performance testing and baseline capacity fade explorer.
    * **⚖️ Model Comparison:** Evaluate the trade-offs between calculation speed (SPM) and electrochemical fidelity (DFN).
    * **🔬 Degradation Physics:** Isolate specific failure mechanisms like SEI layer growth, lithium plating, and active material loss.
    * **🔥 Thermal Analysis:** Analyze how operational temperatures alter degradation kinetics via Arrhenius equations.
    * **🤖 Machine Learning:** Train an ensemble model to instantly predict battery End-of-Life (EOL) across diverse deployment scenarios.
    """)
else:
    # 5. Execute the active file's code seamlessly under the matching route
    pg.run()