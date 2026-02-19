import streamlit as st
import pandas as pd
import os
import io
import csv

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors, pagesizes
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics


# =====================================================
# DATA CLEANING FUNCTION  ✅ ADDED
# =====================================================
def clean_vacancy_data(df):

    df.columns = df.columns.str.strip()

    # Remove newline characters & extra spaces
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.replace("\n", " ", regex=False).str.strip()

    # Convert vacancy columns to numeric
    vacancy_cols = ["UR", "SC", "ST", "OBC", "EWS", "Total"]
    for col in vacancy_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


# =====================================================
# PDF GENERATION FUNCTION
# =====================================================
def generate_pdf(df):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.A4
    )

    elements = []

    pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

    title_style = ParagraphStyle(
        name="TitleStyle",
        fontName="HYSMyeongJo-Medium",
        fontSize=14,
        alignment=1
    )

    elements.append(Paragraph("SSC CGL 2025 Category Prediction Report", title_style))
    elements.append(Spacer(1, 12))

    data = [df.columns.tolist()] + df.astype(str).values.tolist()

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'HYSMyeongJo-Medium'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)
    return buffer


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="SSC CGL 2025 Optimized Predictor",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align:center;'>🇮🇳 SSC CGL 2025 Optimized Predictor System</h1>",
    unsafe_allow_html=True
)

# =====================================================
# NAVIGATION
# =====================================================
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
# HOME PAGE
# =====================================================
if st.session_state.page == "Home":

    st.subheader("Welcome to SSC CGL 2025 AI Predictor")

    st.write("""
    ✅ Rank-based Post Prediction  
    ✅ Merit Rank Impact Analysis  
    ✅ Bonus Marks Simulation  
    ✅ Vacancy-Based Real SSC Logic  
    """)


# =====================================================
# PREDICTOR PAGE
# =====================================================
elif st.session_state.page == "Predictor":

    st.header("📊 Rank-Based SSC Post Predictor")

    # ---------------------------
    # USER INPUT
    # ---------------------------
    st.sidebar.header("Step 1: Your Marks")

    u_main = st.sidebar.number_input("Main Paper Marks", 0.0, 390.0, 321.0)
    u_stat = st.sidebar.number_input("Statistics Marks", 0.0, 200.0, 96.5)
    u_comp = st.sidebar.number_input("Computer Marks", 0.0, 60.0, 16.0)
    u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])

    st.sidebar.markdown("### 🎯 Bonus Simulation")

    bonus_main = st.sidebar.number_input("Bonus Main", 0.0, 20.0, 0.0)
    bonus_stat = st.sidebar.number_input("Bonus Statistics", 0.0, 20.0, 0.0)
    bonus_comp = st.sidebar.number_input("Bonus Computer", 0.0, 20.0, 0.0)

    # ---------------------------
    # FILE PATHS
    # ---------------------------
    OVERALL_FILE = "CSV - SSC CGL Mains 2025 Marks List.xlsx - in.csv"
    STAT_FILE = "CSV - SSC CGL Mains 2025 Statistics Paper Marks List (1).csv"
    VAC_FILE = "vacancy_data.csv"

    for file in [OVERALL_FILE, STAT_FILE, VAC_FILE]:
        if not os.path.exists(file):
            st.error(f"❌ {file} not found in project folder.")
            st.stop()

    df_overall = pd.read_csv(OVERALL_FILE)
    df_stat = pd.read_csv(STAT_FILE)
    df_vac = pd.read_csv(VAC_FILE)

    # ✅ CLEAN VACANCY DATA
    df_vac = clean_vacancy_data(df_vac)

    # ---------------------------
    # PREPARE DATA
    # ---------------------------
    df_overall["TotalScore"] = df_overall["Main Paper Marks"]
    df_stat["TotalScore"] = (
        df_stat["Main Paper Marks"] + df_stat["Statistics Marks"]
    )

    user_main = u_main + bonus_main
    user_stat = u_stat + bonus_stat
    user_total_stat = user_main + user_stat

    # ---------------------------
    # RANK CALCULATION
    # ---------------------------
    df_overall_sorted = df_overall.sort_values("TotalScore", ascending=False)
    df_stat_sorted = df_stat.sort_values("TotalScore", ascending=False)

    overall_rank_new = (df_overall_sorted["TotalScore"] > user_main).sum() + 1
    stat_rank_new = (df_stat_sorted["TotalScore"] > user_total_stat).sum() + 1

    category_df = df_overall_sorted[df_overall_sorted["Category"] == u_cat]
    category_rank_new = (category_df["TotalScore"] > user_main).sum() + 1

    # ---------------------------
    # DISPLAY RANK
    # ---------------------------
    st.subheader("📈 Your Estimated Rank")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Overall Rank (All India)", overall_rank_new)
        st.metric("Category Rank", category_rank_new)

    with col2:
        st.metric("Statistics Rank (if applicable)", stat_rank_new)

    st.divider()

    # ---------------------------
    # POST PREDICTION
    # ---------------------------
    st.subheader("🎯 Predicted Posts (Based on Rank & Vacancies)")

    predicted_posts = []

    for _, row in df_vac.iterrows():

        vacancy_count = row.get(u_cat, 0)

        if vacancy_count <= 0:
            continue

        is_stat_post = str(row.get("Is_Stat_Post", "")).strip().lower() in ["true", "yes", "1"]

        user_rank = stat_rank_new if is_stat_post else category_rank_new

        # ✅ Correct comparison logic
        
        department_col = "Department"  # define column name
post_col = "Post Name"         # define column name

with open("vacancy_data.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if user_rank <= vacancy_count:
            predicted_posts.append({
                "Department": row.get(department_col, "N/A"),
                "Post Name": row.get(post_col, "N/A"),
                "Your Rank": user_rank,
                f"{u_cat} Vacancies": vacancy_count,
                "Post Type": "Statistics Post" if is_stat_post else "Normal Post"
            })

    # ---------------------------
    # SHOW RESULTS
    # ---------------------------
    if predicted_posts:

        result_df = pd.DataFrame(predicted_posts)

        st.success("✅ Based on your rank, you are eligible for the following posts:")
        st.dataframe(result_df, use_container_width=True)

        pdf_file = generate_pdf(result_df)

        st.download_button(
            label="⬇️ Download Prediction Report (PDF)",
            data=pdf_file,
            file_name="SSC_CGL_2025_Prediction_Report.pdf",
            mime="application/pdf"
        )

    else:
        st.warning("⚠️ Your rank exceeds available vacancies in all posts.")

    st.divider()

    st.subheader("📋 Full Vacancy Table")
    st.dataframe(df_vac, use_container_width=True)


# =====================================================
# ANALYTICS PAGE
# =====================================================








