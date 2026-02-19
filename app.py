import streamlit as st
from engine import (
    load_and_clean_data,
    load_stat_data,
    get_full_vacancy_list,
    generate_pdf
)
if "page" not in st.session_state:
    st.session_state.page = "Home"

nav1, nav2, nav3 = st.columns(3)

with nav1:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"

with nav2:
    if st.button("📊 Cutoff Predictor", use_container_width=True):
        st.session_state.page = "Predictor"

with nav3:
    if st.button("📈 Analytics", use_container_width=True):
        st.session_state.page = "Analytics"

st.divider()
elif st.session_state.page == "Predictor":
    st.title("📊 Full Post-wise Cutoff Table + Your Prediction")

st.sidebar.header("Step 1: Your Profile")
u_marks = st.sidebar.number_input("Main Paper Marks", 0.0, 390.0, 310.0)
u_stat = st.sidebar.number_input("Statistics Marks", 0.0, 200.0, 0.0)
u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])
u_comp = st.sidebar.number_input("Computer Marks", 0.0, 60.0, 25.0)

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

cutoffs_rules = {'UR': (18, 27), 'OBC': (15, 24), 'EWS': (15, 24), 'SC': (12, 21), 'ST': (12, 21)}
u_b_min, u_c_min = cutoffs_rules.get(u_cat, (12, 21))

# --- VACANCY DATAFRAME ---
posts = get_full_vacancy_list()
posts_df = pd.DataFrame(posts, columns=[
    'Level', 'Post', 'UR', 'SC', 'ST', 'OBC', 'EWS', 'Total', 'IsCPT', 'IsStat'
])
pay_level_order = {"L-7": 7, "L-6": 6, "L-5": 5, "L-4": 4}
posts_df['PayLevelNum'] = posts_df['Level'].map(pay_level_order)
posts_df = posts_df.sort_values(by='PayLevelNum', ascending=False)

# --- GLOBAL POOL SORTED ---
df_final['TotalScore'] = df_final['Total_Stat_Marks']
global_pool = df_final.sort_values(by='TotalScore', ascending=False).copy()

# --- FULL CATEGORY CUTOFF TABLE + USER PREDICTION ---
display_full = []
allocated_indices_full = set()

for _, row in posts_df.iterrows():
    lvl = row['Level']
    name = row['Post']
    ur_v, sc_v, st_v, obc_v, ews_v = row['UR'], row['SC'], row['ST'], row['OBC'], row['EWS']
    is_cpt, is_stat = row['IsCPT'], row['IsStat']

    pool = global_pool[~global_pool.index.isin(allocated_indices_full)]
    score_col = 'Total_Stat_Marks' if is_stat else 'Main Paper Marks'
    user_score = (u_marks + u_stat) if is_stat else u_marks

    ur_candidates = pool.head(ur_v)
    ur_cut = ur_candidates[score_col].min() if not ur_candidates.empty else 0
    allocated_indices_full.update(ur_candidates.index)

    cat_v_map = {'SC': st_v, 'ST': st_v, 'OBC': obc_v, 'EWS': ews_v}
    cat_cutoffs = {}
    user_cat_cut = 0
    for cat, vac in cat_v_map.items():
        if vac == 0:
            cat_cutoffs[cat] = "N/A"
            continue
        cat_pool = pool[~pool.index.isin(ur_candidates.index)]
        cat_pool = cat_pool[cat_pool['Category'] == cat].sort_values(by=score_col, ascending=False).head(vac)
        cat_cut = cat_pool[score_col].min() if not cat_pool.empty else 0
        cat_cutoffs[cat] = cat_cut if cat_cut > 0 else "N/A"
        allocated_indices_full.update(cat_pool.index)
        if cat == u_cat:
            user_cat_cut = cat_cut

    req_comp = u_c_min if is_cpt else u_b_min
    if u_comp < req_comp:
        chance = "❌ FAIL (Comp)"
    elif is_stat and u_stat == 0:
        chance = "⚠️ Stat Paper Absent"
    elif user_score >= ur_cut and ur_cut > 0:
        chance = "⭐ HIGH (UR Merit)"
    elif user_score >= user_cat_cut and user_cat_cut > 0:
        chance = "✅ HIGH CHANCE"
    else:
        chance = "📉 LOW CHANCE"

    display_full.append({
        "Pay Level": lvl,
        "Post": name,
        "UR Cutoff": ur_cut if ur_cut > 0 else "N/A",
        "SC Cutoff": cat_cutoffs.get('SC', "N/A"),
        "ST Cutoff": cat_cutoffs.get('ST', "N/A"),
        "OBC Cutoff": cat_cutoffs.get('OBC', "N/A"),
        "EWS Cutoff": cat_cutoffs.get('EWS', "N/A"),
        f"{u_cat} Prediction": chance
    })
    
full_df = pd.DataFrame(display_full)
full_df['PayLevelNum'] = full_df['Pay Level'].map(pay_level_order)
full_df = full_df.sort_values(['PayLevelNum', 'Post'], ascending=[False, True])

st.subheader("📊 Full Post-wise Cutoff Table + Your Prediction")

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


