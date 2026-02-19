import streamlit as st
import pandas as pd
from engine import (
    load_and_clean_data,
    load_stat_data,
    get_full_vacancy_list,
    generate_pdf
)
from engine import train_cutoff_model, predict_cutoff

# ---------------- NAVIGATION STATE ----------------
import streamlit as st

st.set_page_config(
    page_title="SSC CGL 2025 Portal",
    page_icon="🇮🇳",
    layout="wide"
)

# ---------------- PAGE STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------------- NAVBAR CSS ----------------
st.markdown("""
<style>

/* Header */
.gov-header {
    background-color: #0B3D91;
    padding: 15px;
    color: white;
    font-size: 26px;
    font-weight: bold;
    text-align: center;
}

/* Navbar container */
.nav-container {
    display: flex;
    justify-content: center;
    gap: 15px;
    background-color: #f5f7fa;
    padding: 10px;
    border-bottom: 3px solid #0B3D91;
}

/* Base button */
div.stButton > button {
    font-size: 17px;
    padding: 8px 18px;
    border-radius: 6px;
    border: none;
    background-color: #e6e6e6;
    color: black;
    transition: 0.3s;
}

/* Hover */
div.stButton > button:hover {
    background-color: #FF9933;
    color: white;
}

/* Active button */
.active-btn button {
    background-color: #0B3D91 !important;
    color: white !important;
    font-weight: bold !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    '<div class="gov-header">🇮🇳 SSC CGL 2025 Cutoff Portal</div>',
    unsafe_allow_html=True
)

# ---------------- NAVBAR ----------------
nav1, nav2, nav3 = st.columns(3)

with nav1:
    btn_home = st.button("🏠 Home", use_container_width=True)

with nav2:
    btn_pred = st.button("📊 Cutoff Predictor", use_container_width=True)

with nav3:
    btn_analytics = st.button("📈 Analytics", use_container_width=True)

# ---------------- BUTTON LOGIC ----------------
if btn_home:
    st.session_state.page = "Home"

if btn_pred:
    st.session_state.page = "Predictor"

if btn_analytics:
    st.session_state.page = "Analytics"

# ---------------- ACTIVE HIGHLIGHT ----------------
if st.session_state.page == "Home":
    nav1.markdown('<div class="active-btn"></div>', unsafe_allow_html=True)

elif st.session_state.page == "Predictor":
    nav2.markdown('<div class="active-btn"></div>', unsafe_allow_html=True)

elif st.session_state.page == "Analytics":
    nav3.markdown('<div class="active-btn"></div>', unsafe_allow_html=True)

st.divider()
# =====================================================
# ================== HOME PAGE ========================
# =====================================================

if st.session_state.page == "Home":
    st.title("SSC CGL 2025 Allocation System")
    st.write("Welcome to the Full Post-wise Cutoff & Prediction System.")

# =====================================================
# ================== PREDICTOR PAGE ===================
# =====================================================

elif st.session_state.page == "Predictor":

    st.title("🤖 AI-Based Cutoff Prediction")

    # ---------------- LOAD AI DATA ----------------
    hist_df, _ = load_and_clean_data("historical_cutoff_data.csv")

    if hist_df is not None:

        model = train_cutoff_model(hist_df)

        st.subheader("AI Prediction")

        vacancies = st.number_input("Total Vacancies", 1000, 50000, 20000)
        avg_marks = st.number_input("Expected Average Marks", 200.0, 350.0, 280.0)
        category = st.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])

        category_code = ["UR", "OBC", "EWS", "SC", "ST"].index(category)

        if st.button("Predict Cutoff"):
            predicted = predict_cutoff(model, vacancies, avg_marks, category_code)
            st.success(f"🎯 Predicted Cutoff for {category}: {predicted}")

    else:
        st.warning("Historical cutoff dataset not found.")

    st.divider()

    # ---------------- FULL POST TABLE ----------------
    st.title("📊 Full Post-wise Cutoff Table + Your Prediction")

    col1, col2 = st.columns(2)

    with col1:
        u_marks = st.number_input("Main Paper Marks", 0.0, 390.0, 310.0)
        u_cat = st.selectbox("Your Category", ["UR", "OBC", "EWS", "SC", "ST"])

    with col2:
        u_stat = st.number_input("Statistics Marks", 0.0, 200.0, 0.0)
        u_comp = st.number_input("Computer Marks", 0.0, 60.0, 25.0)

    # -------- LOAD DATA ----------
    MAIN_FILE = "CSV - SSC CGL Mains 2025 Marks List.xlsx - in.csv"
    STAT_FILE = "CSV - SSC CGL Mains 2025 Statistics Paper Marks List (1).csv"

    df_main, main_key = load_and_clean_data(MAIN_FILE)
    df_stat, stat_key = load_stat_data(STAT_FILE)

    if df_main is None:
        st.error(f"File '{MAIN_FILE}' not found!")
        st.stop()

    if df_stat is not None:
        df_final = pd.merge(df_main, df_stat, left_on=main_key, right_on=stat_key, how='left').fillna(0)
        df_final['Total_Stat_Marks'] = df_final['Main Paper Marks'] + df_final['Stat Marks']
    else:
        df_final = df_main.copy()
        df_final['Total_Stat_Marks'] = df_final['Main Paper Marks']

    posts = get_full_vacancy_list()
    posts_df = pd.DataFrame(posts, columns=[
        'Level', 'Post', 'UR', 'SC', 'ST', 'OBC', 'EWS', 'Total', 'IsCPT', 'IsStat'
    ])

    pay_level_order = {"L-7": 7, "L-6": 6, "L-5": 5, "L-4": 4}
    posts_df['PayLevelNum'] = posts_df['Level'].map(pay_level_order)
    posts_df = posts_df.sort_values(by='PayLevelNum', ascending=False)

    df_final['TotalScore'] = df_final['Total_Stat_Marks']
    global_pool = df_final.sort_values(by='TotalScore', ascending=False).copy()

    display_full = []
    allocated_indices_full = set()

    for _, row in posts_df.iterrows():

        lvl = row['Level']
        name = row['Post']
        ur_v = row['UR']
        is_stat = row['IsStat']

        pool = global_pool[~global_pool.index.isin(allocated_indices_full)]
        score_col = 'Total_Stat_Marks' if is_stat else 'Main Paper Marks'
        user_score = (u_marks + u_stat) if is_stat else u_marks

        ur_candidates = pool.head(ur_v)
        ur_cut = ur_candidates[score_col].min() if not ur_candidates.empty else 0
        allocated_indices_full.update(ur_candidates.index)

        chance = "📉 LOW CHANCE"
        if user_score >= ur_cut and ur_cut > 0:
            chance = "⭐ HIGH (UR Merit)"

        display_full.append({
            "Pay Level": lvl,
            "Post": name,
            "UR Cutoff": ur_cut if ur_cut > 0 else "N/A",
            "Prediction": chance
        })

    full_df = pd.DataFrame(display_full)
    full_df['PayLevelNum'] = full_df['Pay Level'].map(pay_level_order)
    full_df = full_df.sort_values(['PayLevelNum', 'Post'], ascending=[False, True])

    st.dataframe(full_df.drop(columns='PayLevelNum'),
                 use_container_width=True,
                 hide_index=True)

    pdf_file = generate_pdf(full_df.drop(columns='PayLevelNum'))

    st.download_button(
        label="⬇️ Download Full Report as PDF",
        data=pdf_file,
        file_name="SSC_CGL_2025_Cutoff_Report.pdf",
        mime="application/pdf"
    )
# =====================================================
# ================== ANALYTICS PAGE ===================
# =====================================================

elif st.session_state.page == "Analytics":
    st.title("📈 Analytics Dashboard")
    st.write("Analytics section coming soon.")










