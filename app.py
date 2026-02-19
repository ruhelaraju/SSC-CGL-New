import streamlit as st

st.set_page_config(
    page_title="SSC CGL 2025 Optimized Predictor",
    layout="wide"
)

# ==============================
# HEADER
# ==============================
st.markdown(
    '<div class="header">🇮🇳 SSC CGL 2025 Optimized Predictor System</div>',
    unsafe_allow_html=True
)

# ==============================
# NAVIGATION STATE
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

# =====================================================
# ================== PREDICTOR PAGE ===================
# =====================================================
elif st.session_state.page == "Predictor":

    st.header("📊 AI-Based Merit & Post Predictor")

    # ===============================
    # STEP 1: USER INPUT
    # ===============================
    st.sidebar.header("Step 1: Your Marks")

    u_marks = st.sidebar.number_input("Main Paper Marks", 0.0, 390.0, 310.0)
    u_stat = st.sidebar.number_input("Statistics Marks (if applicable)", 0.0, 200.0, 0.0)
    u_comp = st.sidebar.number_input("Computer Marks", 0.0, 60.0, 25.0)
    u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])

    st.sidebar.markdown("### 🎯 Bonus Simulation")

    bonus_main = st.sidebar.number_input("Bonus in Main Paper", 0.0, 20.0, 0.0)
    bonus_comp = st.sidebar.number_input("Bonus in Computer", 0.0, 20.0, 0.0)
    bonus_stat = st.sidebar.number_input("Bonus in Statistics", 0.0, 20.0, 0.0)

    # ===============================
    # LOAD DATA
    # ===============================
    MAIN_FILE = "your_main_file.csv"
    VAC_FILE = "your_vacancy_file.csv"

    df_main = pd.read_csv(MAIN_FILE)
    df_vac = pd.read_csv(VAC_FILE)

    # Ensure proper column names exist:
    # df_main must contain:
    # 'Main Paper Marks', 'Statistics Marks', 'Computer Marks', 'Category'

    df_main["TotalScore"] = (
        df_main["Main Paper Marks"] +
        df_main["Statistics Marks"]
    )

    # ===============================
    # APPLY BONUS TO USER
    # ===============================
    user_main = u_marks + bonus_main
    user_stat = u_stat + bonus_stat
    user_comp_final = u_comp + bonus_comp

    user_score = user_main + user_stat

    # ===============================
    # MERIT RANK CALCULATION
    # ===============================
    df_sorted = df_main.sort_values(by="TotalScore", ascending=False).reset_index(drop=True)

    overall_rank_original = (df_sorted["TotalScore"] > (u_marks + u_stat)).sum() + 1
    overall_rank_new = (df_sorted["TotalScore"] > user_score).sum() + 1

    df_cat = df_sorted[df_sorted["Category"] == u_cat]

    category_rank_original = (df_cat["TotalScore"] > (u_marks + u_stat)).sum() + 1
    category_rank_new = (df_cat["TotalScore"] > user_score).sum() + 1

    # ===============================
    # BONUS IMPACT SUMMARY
    # ===============================
    st.subheader("📈 Bonus Impact Summary")

    colA, colB = st.columns(2)

    with colA:
        st.metric("Original Total Score", round(u_marks + u_stat, 2))
        st.metric("Original Overall Rank", overall_rank_original)
        st.metric("Original Category Rank", category_rank_original)

    with colB:
        st.metric("New Total Score", round(user_score, 2))
        st.metric("New Overall Rank", overall_rank_new,
                  delta=overall_rank_original - overall_rank_new)
        st.metric("New Category Rank", category_rank_new,
                  delta=category_rank_original - category_rank_new)

    st.divider()

    # ===============================
    # POST ALLOCATION SIMULATION
    # ===============================
    st.subheader("🎯 Post Allocation Prediction")

    predicted_post = None
    predicted_cutoff = None
    eligible = False

    for _, row in df_vac.iterrows():

        post_name = row["Post"]
        post_category = row["Category"]
        post_cutoff = row["Cutoff"]
        required_comp = row.get("Required Computer Marks", 0)

        if post_category != u_cat:
            continue

        # CPT check
        if user_comp_final < required_comp:
            continue

        # Merit check
        if user_score >= post_cutoff:
            predicted_post = post_name
            predicted_cutoff = post_cutoff
            eligible = True
            break

    if eligible:
        st.success(f"✅ Predicted Post: **{predicted_post}**")
        st.info(f"Post Cutoff: {predicted_cutoff}")
    else:
        st.error("❌ Based on current bonus, no post predicted.")

    # ===============================
    # CATEGORY-WISE CUTOFF TABLE
    # ===============================
    st.subheader("📋 Category-wise Cutoff Overview")

    cat_df = df_vac[df_vac["Category"] == u_cat]
    st.dataframe(cat_df[["Post", "Cutoff"]])

    # ===============================
    # FINAL INSIGHT
    # ===============================
    improvement = overall_rank_original - overall_rank_new

    if improvement > 0:
        st.success(f"🚀 Bonus improved your overall rank by {improvement} positions!")
    else:
        st.info("No significant rank improvement from bonus.")

# At the end:

st.dataframe(full_df.drop(columns='PayLevelNum'), use_container_width=True, hide_index=True)
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.platypus import TableStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io
import streamlit as st

def generate_pdf(df):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.A4
    )

    elements = []

    # Register built-in Unicode font (safe)
    pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

    style = ParagraphStyle(
        name='Normal',
        fontName='HYSMyeongJo-Medium',
        fontSize=8
    )

    # Prepare table data
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

























