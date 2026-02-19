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

    import os
    import pandas as pd

    st.header("📊 AI-Based Merit & Post Predictor")

    # ===============================
    # USER INPUT
    # ===============================
    st.sidebar.header("Step 1: Your Marks")

    u_main = st.sidebar.number_input("Main Paper Marks", 0.0, 390.0, 310.0)
    u_stat = st.sidebar.number_input("Statistics Marks", 0.0, 200.0, 0.0)
    u_comp = st.sidebar.number_input("Computer Marks", 0.0, 60.0, 25.0)
    u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])

    st.sidebar.markdown("### 🎯 Bonus Simulation")

    bonus_main = st.sidebar.number_input("Bonus Main", 0.0, 20.0, 0.0)
    bonus_stat = st.sidebar.number_input("Bonus Statistics", 0.0, 20.0, 0.0)
    bonus_comp = st.sidebar.number_input("Bonus Computer", 0.0, 20.0, 0.0)

    # ===============================
    # FILE PATHS
    # ===============================
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

    # ===============================
    # PREPARE MERIT LISTS
    # ===============================
    df_overall["TotalScore"] = df_overall["Main Paper Marks"]
    df_stat["TotalScore"] = (
        df_stat["Main Paper Marks"] +
        df_stat["Statistics Marks"]
    )

    # ===============================
    # APPLY BONUS
    # ===============================
    user_main = u_main + bonus_main
    user_stat = u_stat + bonus_stat
    user_comp_final = u_comp + bonus_comp

    user_total_stat = user_main + user_stat
    user_total_overall = user_main

    # ===============================
    # RANK CALCULATION
    # ===============================
    df_overall_sorted = df_overall.sort_values("TotalScore", ascending=False)
    df_stat_sorted = df_stat.sort_values("TotalScore", ascending=False)

    overall_rank_original = (df_overall_sorted["TotalScore"] > u_main).sum() + 1
    overall_rank_new = (df_overall_sorted["TotalScore"] > user_main).sum() + 1

    category_df = df_overall_sorted[df_overall_sorted["Category"] == u_cat]

    category_rank_original = (category_df["TotalScore"] > u_main).sum() + 1
    category_rank_new = (category_df["TotalScore"] > user_main).sum() + 1

    # ===============================
    # DISPLAY RANK IMPACT
    # ===============================
    st.subheader("📈 Rank Impact")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Original Overall Rank", overall_rank_original)
        st.metric("Original Category Rank", category_rank_original)

    with col2:
        st.metric("New Overall Rank", overall_rank_new,
                  delta=overall_rank_original - overall_rank_new)
        st.metric("New Category Rank", category_rank_new,
                  delta=category_rank_original - category_rank_new)

    st.divider()

    # ===============================
    # POST PREDICTION ENGINE
    # ===============================
    st.subheader("🎯 Post Prediction")

    predicted_posts = []

    if u_cat not in df_vac.columns:
        st.error(f"❌ Column '{u_cat}' not found in vacancy file.")
        st.stop()

    for _, row in df_vac.iterrows():

        # Check vacancy count
        if row[u_cat] <= 0:
            continue

        required_comp = row.get("Required Computer Marks", 0)

        if user_comp_final < required_comp:
            continue

        is_stat_post = row.get("Is_Stat_Post", False)

        if is_stat_post:
            score_to_check = user_total_stat
        else:
            score_to_check = user_total_overall

        cutoff_column = f"{u_cat}_Cutoff"

        if cutoff_column not in df_vac.columns:
            continue

        cutoff_value = row.get(cutoff_column)

        if pd.isna(cutoff_value):
            continue

        if score_to_check >= cutoff_value:
            predicted_posts.append({
                "Post": row["Post"],
                "Your Score": score_to_check,
                "Cutoff": cutoff_value
            })

    # ===============================
    # SHOW RESULTS
    # ===============================
    if predicted_posts:
        result_df = pd.DataFrame(predicted_posts)
        st.success("✅ You are eligible for the following posts:")
        st.dataframe(result_df, use_container_width=True)
    else:
        st.error("❌ No post predicted with current marks.")

    st.divider()

    # ===============================
    # CATEGORY CUTOFF TABLE
    # ===============================
    st.subheader("📋 Category Cutoff Table")

    st.dataframe(df_vac, use_container_width=True)

    # ===============================
    # BONUS INSIGHT
    # ===============================
    improvement = overall_rank_original - overall_rank_new

    if improvement > 0:
        st.success(f"🚀 Bonus improved your rank by {improvement} positions!")
    else:
        st.info("No significant rank change from bonus.")

    # -------------------------------
    # PDF GENERATION
    # -------------------------------
def generate_pdf(df):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.A4
    )

    elements = []

    # Register Korean-safe font (also works for English)
    pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

    title_style = ParagraphStyle(
        name="TitleStyle",
        fontName="HYSMyeongJo-Medium",
        fontSize=14,
        alignment=1  # Center
    )

    elements.append(Paragraph("SSC CGL 2025 Category Report", title_style))
    elements.append(Spacer(1, 12))

    # Convert dataframe to string
    data = [df.columns.tolist()] + df.astype(str).values.tolist()

    # Auto column width
    col_widths = [None] * len(df.columns)

    table = Table(data, repeatRows=1, colWidths=col_widths)

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
    if not full_df.empty:

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





