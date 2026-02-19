import streamlit as st
import pandas as pd
import numpy as np
import os
import io

# --- PART 1: DATA LOADING & CLEANING ---
@st.cache_data
def load_and_clean_data(file_name):
    if not os.path.exists(file_name):
        return None, None
    df = pd.read_csv(file_name, encoding='latin1', on_bad_lines='skip')
    df.columns = [str(c).strip() for c in df.columns]

    if 'Main Paper Marks' not in df.columns:
        df = pd.read_csv(file_name, skiprows=1, encoding='latin1')
        df.columns = [str(c).strip() for c in df.columns]

    key_col = 'Roll Number' if 'Roll Number' in df.columns else df.columns[0]
    df['Main Paper Marks'] = pd.to_numeric(df['Main Paper Marks'], errors='coerce')
    df['Computer Marks'] = pd.to_numeric(df['Computer Marks'], errors='coerce')
    df = df.dropna(subset=['Main Paper Marks', 'Category', 'Computer Marks'])

    rules = {'UR': (18, 27), 'OBC': (15, 24), 'EWS': (15, 24), 'SC': (12, 21), 'ST': (12, 21)}
    def get_pass_status(row):
        b, c = rules.get(row['Category'], (12, 21))
        return pd.Series([row['Computer Marks'] >= b, row['Computer Marks'] >= c])
    df[['Pass_B', 'Pass_C']] = df.apply(get_pass_status, axis=1)
    return df, key_col


@st.cache_data
def load_stat_data(file_name):
    if not os.path.exists(file_name): 
        return None, None
    df = pd.read_csv(file_name, encoding='latin1', on_bad_lines='skip')
    df.columns = [str(c).strip() for c in df.columns]
    key_col = 'Roll Number' if 'Roll Number' in df.columns else df.columns[0]
    df['Stat Marks'] = pd.to_numeric(df.get('Stat Marks', df.iloc[:, -1]), errors='coerce')
    return df[[key_col, 'Stat Marks']], key_col


def get_full_vacancy_list():    
    return [
        # ⬇️ PASTE YOUR FULL VACANCY LIST HERE EXACTLY AS IS
    ]


def generate_pdf(df):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib import pagesizes
    from reportlab.lib.units import inch
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase import pdfmetrics
    
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
