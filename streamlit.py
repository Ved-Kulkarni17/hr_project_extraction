import os
import sys
import tempfile
import streamlit as st
import pandas as pd
from datetime import datetime, date

sys.path.append(os.path.abspath("src"))
from extract_form import extract_form_based_fields
from extract_text import extract_text_based_fields
from merge_records import merge_by_candidate

st.set_page_config(page_title="HR Pre-Onboarding Dashboard", page_icon="👥", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    [data-testid="stMetricValue"] { font-size: 24px; color: #4ade80; }
    [data-testid="stDataFrame"] { border: 1px solid #334155; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

def calculate_status(row):
    missing = []
    if not row.get("bank_name"): missing.append("Bank")
    if not row.get("aadhar_number"): missing.append("Aadhar")
    return "✅ Ready" if not missing else f"⚠️ Missing: {', '.join(missing)}"

def days_to_join(doj_str):
    try:
        if not doj_str: return "-"
        doj = datetime.strptime(str(doj_str), "%Y-%m-%d").date()
        delta = (doj - date.today()).days
        if delta < 0: return "Joined"
        elif delta == 0: return "Today!"
        else: return f"{delta} Days"
    except: return "-"

st.title("🚀 Pre-Onboarding Command Center")

uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    records = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        fname = uploaded_file.name.lower()
        try:
            if "bank" in fname or "personal" in fname:
                rec = extract_form_based_fields(pdf_path)
            else:
                rec = extract_text_based_fields(pdf_path)
            rec["email"] = rec.get("email") # Ensure email key exists
            records.append(rec)
        except: pass
        finally: os.unlink(pdf_path)

    if records:
        df = pd.DataFrame(merge_by_candidate(records))
        
        # Derived Fields
        if "role" in df.columns:
            df["Dept"] = df["role"].apply(lambda x: "Engg." if "Engineer" in str(x) else "Product" if "Product" in str(x) else "Design" if "Design" in str(x) else "General")
        
        if "date_of_joining" in df.columns:
            df["Timeline"] = df["date_of_joining"].apply(days_to_join)
            
        df["Status"] = df.apply(calculate_status, axis=1)

        # Columns to display (ADDED: experience_years, education, cgpa)
        cols = [
            "candidate_id", "full_name", "Status", "Dept", "role", "reporting_manager", 
            "Timeline", "date_of_joining", "location", "t_shirt_size", 
            "experience_years", "education", "cgpa",  # <--- NEWLY ADDED
            "phone_number", "email", "bank_name", "account_number", "aadhar_number"
        ]
        
        # Rename map (ADDED mappings)
        rename_map = {
            "candidate_id": "ID", "full_name": "Name", "role": "Role", 
            "reporting_manager": "Manager", "date_of_joining": "DOJ", 
            "t_shirt_size": "Size", "phone_number": "Phone", 
            "bank_name": "Bank", "account_number": "Account", "aadhar_number": "Aadhar",
            "experience_years": "Exp (Yrs)", "education": "Degree", "cgpa": "CGPA" # <--- NEWLY ADDED
        }

        # Filter and rename
        final_cols = [c for c in cols if c in df.columns]
        df_final = df[final_cols].rename(columns=rename_map)

        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Candidates", len(df_final))
        m2.metric("Ready to Join", len(df_final[df_final["Status"].str.contains("Ready")]))
        m3.metric("Missing Docs", len(df_final[df_final["Status"].str.contains("Missing")]), delta_color="inverse")

        st.dataframe(df_final, use_container_width=True)
        
        st.download_button("Download CSV", df_final.to_csv(index=False).encode("utf-8"), "hr_data.csv", "text/csv")
