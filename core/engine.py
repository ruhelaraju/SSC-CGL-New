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
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import streamlit as st

@st.cache_resource
def train_cutoff_model(df):
    """
    Train AI model based on historical cutoff data.
    """

    # Example feature columns (modify as per your dataset)
    feature_cols = [
        "Vacancies",
        "Avg_Marks",
        "Category_Code"
    ]

    # Convert category to numeric
    df["Category_Code"] = df["Category"].astype("category").cat.codes

    X = df[feature_cols]
    y = df["Final_Cutoff"]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        random_state=42
    )

    model.fit(X, y)
    return model
    
@st.cache_data
def load_stat_data(file_name):
    if not os.path.exists(file_name): 
        return None, None
    df = pd.read_csv(file_name, encoding='latin1', on_bad_lines='skip')
    df.columns = [str(c).strip() for c in df.columns]
    key_col = 'Roll Number' if 'Roll Number' in df.columns else df.columns[0]
    df['Stat Marks'] = pd.to_numeric(df.get('Stat Marks', df.iloc[:, -1]), errors='coerce')
    return df[[key_col, 'Stat Marks']], key_col
def predict_cutoff(model, vacancies, avg_marks, category_code):
    input_data = np.array([[vacancies, avg_marks, category_code]])
    prediction = model.predict(input_data)
    return round(prediction[0], 2)

def get_full_vacancy_list():    
    return [
        ("L-7", "CSS (DoPT) - ASO", 273, 104, 52, 185, 68, 682, True, False),
        ("L-7", "MEA - ASO", 44, 13, 0, 33, 10, 100, True, False),
        ("L-7", "CBIC - Inspector (Examiner)", 68, 18, 24, 13, 14, 137, True, False),
        ("L-7", "CBIC - Inspector (Preventive Officer)", 138, 75, 20, 91, 29, 353, True, False),
        ("L-7", "CBIC - Inspector (Central Excise)", 611, 175, 82, 269, 169, 1306, True, False),
        ("L-7", "CBDT - IT Inspector", 176, 52, 39, 95, 27, 389, False, False),
        ("L-7", "ED - Assistant Enforcement Officer", 1, 2, 2, 13, 0, 18, False, False),
        ("L-7", "IB - ASO", 100, 24, 19, 39, 15, 197, False, False),
        ("L-7", "Railways - ASO", 23, 4, 4, 14, 3, 48, False, False),
        ("L-7", "EPFO - ASO", 36, 17, 5, 30, 6, 94, False, False),
        ("L-7", "CBI - Sub Inspector", 52, 12, 5, 18, 6, 93, False, False),
        ("L-7", "NIC - ASO", 2, 0, 0, 0, 1, 3, False, False),
        ("L-7", "CAT - ASO", 0, 0, 0, 0, 1, 1, False, False),
        ("L-7", "CBN - Inspector", 1, 1, 0, 1, 1, 4, False, False),
        ("L-7", "ECI - ASO", 0, 0, 0, 5, 1, 6, False, False),
        ("L-7", "MeitY - ASO", 2, 0, 1, 0, 0, 3, False, False),
        ("L-6", "CBIC - Executive Assistant", 89, 24, 12, 40, 18, 183, True, False),
        ("L-6", "CBDT - Office Superintendent", 2766, 1012, 496, 1822, 657, 6753, False, False),
        ("L-6", "RGI - Statistical Investigator Gr. II", 50, 18, 12, 28, 10, 118, False, True),
        ("L-6", "MoSPI - Junior Statistical Officer", 124, 47, 15, 36, 27, 249, False, True),
        ("L-6", "ED - Assistant", 0, 0, 0, 3, 0, 3, False, False),
        ("L-6", "TRAI - Assistant", 2, 1, 0, 0, 0, 3, False, False),
        ("L-6", "Official Language - Assistant", 4, 0, 0, 1, 0, 5, False, False),
        ("L-6", "MCA - Assistant", 0, 1, 0, 0, 0, 1, False, False),
        ("L-6", "Mines - Assistant", 11, 2, 2, 3, 4, 22, True, False),
        ("L-6", "Textiles - Assistant", 1, 0, 0, 0, 0, 1, False, False),
        ("L-6", "Indian Coast Guard - Assistant", 8, 3, 1, 5, 1, 18, False, False),
        ("L-6", "DFSS - Assistant", 1, 0, 0, 1, 1, 3, False, False),
        ("L-6", "NCB - ASO", 7, 1, 1, 2, 0, 11, False, False),
        ("L-6", "NCB - Sub-Inspector/JIO", 10, 3, 4, 8, 5, 30, False, False),
        ("L-6", "NIA - Sub Inspector", 6, 2, 1, 3, 2, 14, False, False),
        ("L-6", "MoSPI - Assistant", 0, 0, 0, 2, 0, 2, False, False),
        ("L-5", "CGDA - Auditor", 477, 176, 88, 316, 117, 1174, False, False),
        ("L-5", "C&AG - Accountant", 86, 31, 17, 28, 18, 180, False, False),
        ("L-5", "Posts - Accountant", 42, 13, 6, 12, 3, 76, False, False),
        ("L-5", "CGCA - Accountant", 15, 6, 3, 9, 3, 36, False, False),
        ("L-4", "CBIC - Tax Assistant", 256, 136, 82, 203, 94, 771, True, False),
        ("L-4", "CBDT - Tax Assistant", 572, 171, 80, 340, 86, 1249, False, False),
        ("L-4", "MSME - UDC/SSA", 25, 4, 5, 16, 5, 55, False, False),
        ("L-4", "Science & Tech - UDC/SSA", 24, 9, 4, 16, 6, 59, False, False),
        ("L-4", "CBN - UDC/SSA", 12, 2, 0, 5, 2, 21, False, False),
        ("L-4", "CBN - Sub-Inspector", 11, 2, 0, 6, 0, 19, False, False),
        ("L-4", "Mines - UDC/SSA", 13, 2, 3, 4, 4, 26, False, False),
        ("L-4", "DGDE - UDC/SSA", 7, 2, 1, 3, 1, 14, False, False),
        ("L-4", "MeitY - UDC/SSA", 5, 1, 1, 2, 1, 10, False, False),
        ("L-4", "Textiles - UDC/SSA", 4, 0, 1, 1, 2, 8, False, False),
        ("L-4", "Water Resources - UDC/SSA", 5, 0, 0, 0, 0, 5, False, False),
        ("L-4", "BRO - UDC/SSA", 20, 1, 0, 0, 4, 25, False, False),
        ("L-4", "Agriculture - UDC/SSA", 2, 0, 0, 0, 1, 3, False, False),
        ("L-4", "Health - UDC/SSA", 1, 0, 0, 0, 0, 1, False, False),
        ("L-4", "Dept of Post - PA/SA", 0, 0, 0, 0, 0, 0, True, False)
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

