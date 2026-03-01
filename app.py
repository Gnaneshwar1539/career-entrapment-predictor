import streamlit as st
import pandas as pd
import numpy as np
import math
import plotly.express as px
import requests
import PyPDF2
from docx import Document
from urllib.parse import quote
import re

st.set_page_config(page_title="Career Mobility AI", layout="wide")

# =====================================================
# SESSION STATE INIT
# =====================================================

for key in ["page", "selected_company", "selected_job", "job_results"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "job_results" else []

if not st.session_state.page:
    st.session_state.page = "jobs"

# =====================================================
# PREMIUM UI
# =====================================================

st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    font-family: 'Segoe UI', sans-serif;
}
h1,h2,h3,h4,h5,h6,label,p {color:white !important;}
.stButton>button {
    background: linear-gradient(135deg,#00f5ff,#7f00ff);
    border-radius: 25px;
    color: white !important;
    padding: 10px 25px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding:40px;border-radius:25px;
background:linear-gradient(135deg,#00f5ff,#7f00ff);
text-align:center;margin-bottom:40px;">
<h1>🚀 AI Career Mobility Intelligence Platform (India)</h1>
<h4>Entrapment • Burnout • Market Demand • Skill Intelligence</h4>
</div>
""", unsafe_allow_html=True)

# =====================================================
# HELPERS
# =====================================================

def get_secret(key):
    try:
        return st.secrets[key]
    except:
        return None

def clean_company_name(name):
    remove = ["ltd","limited","pvt","private","inc","llp"]
    name = name.lower()
    for r in remove:
        name = name.replace(r,"")
    return name.strip()

# -----------------------------------------------------
# Salary Estimation Engine (AI Modeled)
# -----------------------------------------------------

def estimate_salary_from_title(title, description):
    title = title.lower()
    description = description.lower()

    base = 6  # Base LPA

    if "senior" in title:
        base += 6
    if "lead" in title or "architect" in title:
        base += 10
    if "manager" in title:
        base += 12

    if "python" in title:
        base += 3
    if "ai" in description or "machine learning" in description:
        base += 8
    if "cloud" in description:
        base += 4
    if "devops" in description:
        base += 5

    match = re.search(r'(\d+)\s*-\s*(\d+)\s*years', description)
    if match:
        exp = int(match.group(2))
        base += exp * 0.8

    return round(base,1), round(base*1.4,1)

# -----------------------------------------------------
# APIs
# -----------------------------------------------------

@st.cache_data(ttl=3600)
def fetch_jobs(app_id, app_key, keyword, city):
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": keyword,
        "where": city,
        "results_per_page": 10
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=86400)
def get_company_details(company):
    api_key = get_secret("API_NINJAS_KEY")
    if not api_key:
        return None

    cleaned = clean_company_name(company)
    encoded = quote(cleaned)

    try:
        r = requests.get(
            f"https://api.api-ninjas.com/v1/company?name={encoded}",
            headers={"X-Api-Key": api_key},
            timeout=5
        )
        if r.status_code != 200:
            return None
        data = r.json()
        if not data:
            return None
        return data[0]
    except:
        return None

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs(
    ["🧠 Career Risk","🏢 Market & Jobs","📊 Skill Intelligence","📈 Executive Summary"]
)

# =====================================================
# TAB 1 – CAREER RISK
# =====================================================

with tab1:
    st.header("Career Entrapment & Burnout Prediction")

    skills = st.text_area("Your Skills (comma separated)")
    salary = st.number_input("Current Salary (₹ LPA)", min_value=0.0)
    years = st.number_input("Years Experience", min_value=0.0)
    debt = st.number_input("Debt (₹)", min_value=0.0)
    savings = st.number_input("Savings (₹)", min_value=0.0)
    expenses = st.number_input("Monthly Expenses (₹)", min_value=1.0)

    if st.button("Analyze Career"):
        skill_list = skills.split(",")
        portability = min(25, len(skill_list)*1.5)
        debt_ratio = debt/salary if salary>0 else 0
        runway = savings/expenses
        decay = (1-math.exp(-0.05*years))*25

        st.session_state.entrapment = min(100, portability+15+(debt_ratio*20)+decay)
        st.session_state.burnout = min(100, years*4 + debt_ratio*40)
        st.session_state.runway = runway

    if "entrapment" in st.session_state:
        col1,col2,col3 = st.columns(3)
        col1.metric("Entrapment Score", round(st.session_state.entrapment,2))
        col2.metric("Burnout %", round(st.session_state.burnout,2))
        col3.metric("Financial Runway (months)", round(st.session_state.runway,2))

# =====================================================
# TAB 2 – MARKET & JOBS
# =====================================================

with tab2:

    if st.session_state.page=="company" and st.session_state.selected_job:

        if st.button("⬅ Back to Jobs"):
            st.session_state.page="jobs"
            st.rerun()

        job=st.session_state.selected_job
        company=st.session_state.selected_company

        st.header(f"🏢 {company}")

        st.subheader("📄 Job Description")
        st.write(job.get("description","No description available"))

        # Salary Logic
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        if salary_min and salary_max:
            st.metric("💰 Salary (Actual)",
                      f"₹ {int(salary_min)} - ₹ {int(salary_max)}")
        else:
            est_min, est_max = estimate_salary_from_title(
                job.get("title",""),
                job.get("description","")
            )
            st.metric("💰 Estimated Salary (AI Modeled)",
                      f"₹ {est_min} - ₹ {est_max} LPA")

        # Company Intelligence
        st.subheader("🏢 Company Intelligence")

        details = get_company_details(company)

        if details:
            col1,col2,col3=st.columns(3)
            col1.metric("Founded", details.get("founded","N/A"))
            col2.metric("Employees", details.get("employees","N/A"))
            col3.metric("Industry", details.get("industry","N/A"))

            st.write("CEO:", details.get("ceo","N/A"))
            st.write("HQ:", details.get("city","")+" "+details.get("country",""))
            st.write("Market Cap:", details.get("market_cap","N/A"))
        else:
            desc = job.get("description","").lower()

            industry = "Technology Services"
            if "finance" in desc:
                industry = "Financial Services"
            if "health" in desc:
                industry = "Healthcare Tech"

            col1,col2,col3 = st.columns(3)
            col1.metric("Industry (Estimated)", industry)
            col2.metric("Company Size (Estimated)", "200-1000 employees")
            col3.metric("Revenue (Estimated)", "₹100Cr - ₹500Cr")

    else:

        st.header("Live Market Intelligence")

        city=st.selectbox("Select City",
                          ["bangalore","hyderabad","mumbai","pune","chennai","noida"])
        keyword=st.text_input("Job Keyword")

        if st.button("Fetch Live Jobs"):

            APP_ID=get_secret("ADZUNA_ID")
            APP_KEY=get_secret("ADZUNA_KEY")

            data=fetch_jobs(APP_ID,APP_KEY,keyword,city)

            if "error" in data:
                st.error(data["error"])
            else:
                st.session_state.job_results=data.get("results",[])

        if st.session_state.job_results:
            for idx,job in enumerate(st.session_state.job_results):
                col1,col2=st.columns([4,2])
                col1.write(f"**{job['title']}**")
                company=job.get("company",{}).get("display_name","Unknown")

                if col2.button(company,key=f"btn_{idx}"):
                    st.session_state.selected_company=company
                    st.session_state.selected_job=job
                    st.session_state.page="company"
                    st.rerun()

# =====================================================
# TAB 3 – SKILL INTELLIGENCE
# =====================================================

with tab3:
    st.header("Skill Gap Analysis")
    uploaded=st.file_uploader("Upload Resume", type=["pdf","docx","txt"])
    resume_text=""

    if uploaded:
        if uploaded.type=="application/pdf":
            reader=PyPDF2.PdfReader(uploaded)
            for page in reader.pages:
                resume_text+=page.extract_text() or ""
        elif uploaded.type.endswith("document"):
            doc=Document(uploaded)
            for p in doc.paragraphs:
                resume_text+=p.text+"\n"
        else:
            resume_text=uploaded.read().decode()

    if st.button("Analyze Skills"):
        skills_db=["python","ai","ml","cloud","devops","data"]
        found=[s for s in skills_db if s in resume_text.lower()]
        missing=list(set(skills_db)-set(found))

        st.success(f"Detected Skills: {found}")
        st.error(f"Missing Skills: {missing}")

# =====================================================
# TAB 4 – EXECUTIVE SUMMARY
# =====================================================

with tab4:
    st.header("Executive Summary")

    if "entrapment" not in st.session_state:
        st.info("Run Career Risk first")
    else:
        if st.button("Generate Report"):
            risk="High" if st.session_state.entrapment>70 else "Moderate" if st.session_state.entrapment>40 else "Low"

            st.success(f"""
Risk Level: {risk}

Burnout Probability: {round(st.session_state.burnout,2)}%

Recommended Actions:
• Upskill in AI/Cloud
• Improve savings buffer
• Monitor market demand
""")
