import streamlit as st

st.set_page_config(
    page_title="SSC CGL 2025 Optimized Predictor",
    layout="wide"
)

st.title("📊 SSC CGL 2025 Optimized Predictor System")
st.markdown("Use the sidebar to navigate between modules.")

st.divider()

# =============================
# HOME PAGE SLIDER ESTIMATOR
# =============================

st.header("🎯 Quick Cutoff Estimator")

col1, col2 = st.columns(2)

with col1:
    vacancies = st.slider(
        "Total Vacancies",
        min_value=5000,
        max_value=50000,
        value=20000,
        step=1000
    )

with col2:
    avg_marks = st.slider(
        "Expected Average Marks",
        min_value=200,
        max_value=350,
        value=280,
        step=5
    )

category = st.selectbox(
    "Select Category",
    ["UR", "OBC", "EWS", "SC", "ST"]
)

st.divider()

# =============================
# SIMPLE LOGICAL ESTIMATION
# =============================

base_cutoff = 320

vacancy_factor = (20000 - vacancies) * 0.0008
marks_factor = (avg_marks - 280) * 0.6

category_adjustment = {
    "UR": 0,
    "OBC": -8,
    "EWS": -5,
    "SC": -20,
    "ST": -25
}

estimated_cutoff = (
    base_cutoff
    + vacancy_factor
    + marks_factor
    + category_adjustment[category]
)

st.success(
    f"🎯 Estimated Cutoff for {category}: {round(estimated_cutoff, 2)}"
)













