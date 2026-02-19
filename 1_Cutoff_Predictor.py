import streamlit as st
import pandas as pd
from core.engine import (
    load_and_clean_data,
    load_stat_data,
    get_full_vacancy_list,
    generate_pdf
)

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

# ⬇️ PASTE YOUR FULL ALLOCATION + CUTOFF LOOP HERE EXACTLY AS IS
# DO NOT MODIFY ANYTHING

# At the end:

st.dataframe(full_df.drop(columns='PayLevelNum'), use_container_width=True, hide_index=True)

pdf_file = generate_pdf(full_df.drop(columns='PayLevelNum'))

st.download_button(
    label="⬇️ Download Full Report as PDF",
    data=pdf_file,
    file_name="SSC_CGL_2025_Cutoff_Report.pdf",
    mime="application/pdf"
)
