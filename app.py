import streamlit as st
import pandas as pd
import io

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors, pagesizes
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics


# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="SSC CGL 2025 Optimized Predictor",
    layout="wide"
)

# ==============================
# HEADER
# ==============================
st.markdown(
    "<h1 style='text-align:center;'>🇮🇳 SSC CGL 2025 Optimized Predictor System</h1>",
    unsafe_allow_html=True
)

# ==============================
# NAVIGATION
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "Home"

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"

with col2:
    if st.button("📊 Predictor", use_container_width=True):
        st.session_state.page = "Predictor"

with col3:
    if st.button("📈 Analytics", use_container_width=True):
        st.session_state.page = "Analytics"

st.divider()


# =====================================================
# ================== HOME PAGE ========================
# =====================================================
if st.session_state.page == "Home":

    st.subheader("Welcome to SSC CGL 2025 AI Predictor")

    st.write("""
    ✅ Predict your Post  
    ✅ Check Merit Rank Impact  
    ✅ Simulate Bonus Marks  
    ✅ Analyze Category Cutoff  
    """)


# =====================================================
# ================== PREDICTOR PAGE ===================
# =====================================================
elif st.session_state.page == "Predictor":

    st.header("📊 AI-Based Merit & Post Predictor")

    # -------------------------------
    # USER INPUT
    # -------------------------------
    st.sidebar.header("Step 1: Your Marks")

    u_marks = st.sidebar.number_input("Main Paper Marks", 0.0, 390.0, 310.0)
    u_stat = st.sidebar.number_input("Statistics Marks", 0.0, 200.0, 0.0)
    u_comp = st.sidebar.number_input("Computer Marks", 0.0, 60.0, 25.0)
    u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])

    st.sidebar.markdown("### 🎯 Bonus Simulation")

    bonus_main = st.sidebar.number_input("Bonus Main", 0.0, 20.0, 0.0)
    bonus_comp = st.sidebar.number_input("Bonus Computer", 0.0, 20.0, 0.0)
    bonus_stat = st.sidebar.number_input("Bonus Statistics", 0.0, 20.0, 0.0)

    # -------------------------------
    # LOAD DATA
    # -------------------------------
    MAIN_FILE = "your_main_file.csv"
    VAC_FILE = "your_vacancy_file.csv"

    df_main = pd.read_csv(MAIN_FILE)
    df_vac = pd.read_csv(VAC_FILE)

    df_main["TotalScore"] = (
        df_main["Main Paper Marks"] +
        df_main["Statistics Marks"]
    )

    # -------------------------------
    # APPLY BONUS
    # -------------------------------
    user_main = u_marks + bonus_main
    user_stat = u_stat + bonus_stat
    user_comp_final = u_comp + bonus_comp
    user_score = user_main + user_stat

    # -------------------------------
    # RANK CALCULATION
    # -------------------------------
    df_sorted = df_main.sort_values(by="TotalScore", ascending=False)

    overall_rank_original = (df_sorted["TotalScore"] > (u_marks + u_stat)).sum() + 1
    overall_rank_new = (df_sorted["TotalScore"] > user_score).sum() + 1

    df_cat = df_sorted[df_sorted["Category"] == u_cat]

    category_rank_original = (df_cat["TotalScore"] > (u_marks + u_stat)).sum() + 1
    category_rank_new = (df_cat["TotalScore"] > user_score).sum() + 1

    # -------------------------------
    # BONUS IMPACT DISPLAY
    # -------------------------------
    st.subheader("📈 Bonus Impact Summary")

    colA, colB = st.columns(2)

    with colA:
        st.metric("Original Total", round(u_marks + u_stat, 2))
        st.metric("Original Overall Rank", overall_rank_original)
        st.metric("Original Category Rank", category_rank_original)

    with colB:
        st.metric("New Total", round(user_score, 2))
        st.metric("New Overall Rank", overall_rank_new,
                  delta=overall_rank_original - overall_rank_new)
        st.metric("New Category Rank", category_rank_new,
                  delta=category_rank_original - category_rank_new)

    st.divider()

    # -------------------------------
    # POST PREDICTION
    # -------------------------------
    st.subheader("🎯 Post Prediction")

    predicted_post = None

    for _, row in df_vac.iterrows():

        if row["Category"] != u_cat:
            continue

        required_comp = row.get("Required Computer Marks", 0)

        if user_comp_final < required_comp:
            continue

        if user_score >= row["Cutoff"]:
            predicted_post = row["Post"]
            break

    if predicted_post:
        st.success(f"✅ Predicted Post: {predicted_post}")
    else:
        st.error("❌ No post predicted with current marks.")

    # -------------------------------
    # CATEGORY CUTOFF TABLE
    # -------------------------------
    st.subheader("📋 Category Cutoff Table")

    cat_df = df_vac[df_vac["Category"] == u_cat]
    st.dataframe(cat_df, use_container_width=True)

    full_df = cat_df.copy()


    # -------------------------------
    # PDF GENERATION
    # -------------------------------
    def generate_pdf(df):
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)
        elements = []

        pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

        data = [df.columns.tolist()] + df.astype(str).values.tolist()

        table = Table(data, repeatRows=1)

        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'HYSMyeongJo-Medium'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))

        elements.append(table)
        doc.build(elements)

        buffer.seek(0)
        return buffer

    pdf_file = generate_pdf(full_df)

    st.download_button(
        label="⬇️ Download Category Report PDF",
        data=pdf_file,
        file_name="SSC_CGL_2025_Report.pdf",
        mime="application/pdf"
    )


# =====================================================
# ================== ANALYTICS PAGE ===================
# =====================================================
elif st.session_state.page == "Analytics":

    st.header("📈 Analytics Dashboard")

    st.info("Analytics features coming soon 🚀")
