import streamlit as st
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
import plotly.express as px
import requests
from sklearn.preprocessing import MinMaxScaler
import os

st.set_page_config(page_title="Career Mobility AI", layout="wide")

# =====================================================
# PREMIUM UI STYLING
# =====================================================

st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}

.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    font-family: 'Segoe UI', sans-serif;
}

.stButton>button {
    background: linear-gradient(135deg, #00f5ff, #7f00ff);
    border-radius: 25px;
    padding: 12px 28px;
    font-weight: bold;
    color: white !important;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HERO SECTION
# =====================================================

st.markdown("""
<div style="padding:50px;border-radius:25px;
background:linear-gradient(135deg,#00f5ff,#7f00ff);
text-align:center;
box-shadow:0 0 40px rgba(0,255,255,0.6);
margin-bottom:40px;">
<h1>🚀 AI Career Mobility Intelligence Platform (India)</h1>
<h3>Entrapment • Burnout • Market Demand • Skill Intelligence</h3>
</div>
""", unsafe_allow_html=True)

# =====================================================
# MARKET DATA
# =====================================================

market_data = pd.DataFrame({
    "Skill": ["python", "cloud", "ai", "ml", "devops", "data", "backend", "system design"],
    "DemandScore": [95, 90, 98, 92, 85, 93, 88, 87],
    "AvgSalary_LPA": [12, 15, 20, 18, 14, 16, 13, 17]
})

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs(
    ["🧠 Career Risk", "🏢 Market & Jobs", "📊 Skill Intelligence", "📈 Executive Summary"]
)

# =====================================================
# TAB 1 – CAREER RISK + BURNOUT
# =====================================================

with tab1:

    st.header("Career Entrapment & Burnout Prediction")

    col1, col2 = st.columns(2)

    with col1:
        skills = st.text_area("Your Skills (comma separated)")
        salary = st.number_input("Current Salary (₹ LPA)", min_value=0)
        years = st.number_input("Years of Experience", min_value=0)

    with col2:
        debt = st.number_input("Total Debt (₹)", min_value=0)
        savings = st.number_input("Savings (₹)", min_value=0)
        expenses = st.number_input("Monthly Expenses (₹)", min_value=1)

    analyze = st.button("Analyze Career")

    if analyze:

        skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
        skill_count = len(skill_list)

        portability = min(25, skill_count * 1.5)
        income_risk = 15
        debt_ratio = debt / salary if salary > 0 else 0
        runway = savings / expenses if expenses > 0 else 0

        lock_in = min(25, debt_ratio * 15 + (12/runway if runway > 0 else 10))
        decay = (1 - math.exp(-0.05 * years)) * 25

        total_score = min(100, portability + income_risk + lock_in + decay)
        burnout_probability = min(100, years * 4 + debt_ratio * 50)

        st.session_state.entrapment = total_score
        st.session_state.burnout = burnout_probability
        st.session_state.runway = runway
        st.session_state.skill_count = skill_count

    if "entrapment" in st.session_state:

        colA, colB, colC = st.columns(3)
        colA.metric("🔥 Entrapment Score", f"{round(st.session_state.entrapment,2)}/100")
        colB.metric("⚠ Burnout Probability", f"{round(st.session_state.burnout,2)}%")
        colC.metric("💰 Financial Runway", f"{round(st.session_state.runway,2)} months")

# =====================================================
# TAB 2 – LIVE JOB SCRAPING (UNCHANGED FROM app.py)
# =====================================================

with tab2:

    st.header("Live Market Intelligence")

    city = st.selectbox("Select Indian City", ["bangalore", "hyderabad", "mumbai", "pune", "chennai"])
    keyword = st.text_input("Job Keyword (e.g. python, cloud)")

    if st.button("Fetch Live Jobs"):

        APP_ID="3855f57a"
        APP_KEY="06d8f4360d531a49cad05a0ab95d9370"

        url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={APP_ID}&app_key={APP_KEY}&what={keyword}&where={city}"

        try:
            response = requests.get(url)
            data = response.json()

            jobs = []
            for job in data.get("results", [])[:10]:
                jobs.append({
                    "Title": job["title"],
                    "Company": job.get("company", {}).get("display_name", "Unknown"),
                    "Location": job["location"]["display_name"]
                })

            if jobs:
                st.dataframe(pd.DataFrame(jobs))
            else:
                st.warning("No jobs found.")

        except:
            st.error("API failed. Add your Adzuna credentials.")

# =====================================================
# TAB 3 – SKILL GAP (UNCHANGED FROM app.py)
# =====================================================

with tab3:

    st.header("Skill Gap & Market Demand Analysis")

    resume_text = st.text_area("Paste Resume Text")

    if st.button("Analyze Skill Gap"):

        resume_lower = resume_text.lower()
        detected = [skill for skill in market_data["Skill"] if skill in resume_lower]
        missing = list(set(market_data["Skill"]) - set(detected))

        st.success(f"Detected Skills: {detected}")
        st.error(f"Missing High-Demand Skills: {missing}")

        demand_df = market_data.copy()
        demand_df["Present"] = demand_df["Skill"].apply(lambda x: 1 if x in detected else 0)

        fig = px.bar(
            demand_df,
            x="Skill",
            y="DemandScore",
            color="Present",
            title="Skill Demand vs Your Coverage",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TAB 4 – INTELLIGENT EXECUTIVE SUMMARY
# =====================================================

with tab4:

    st.header("Executive AI Summary")

    if "entrapment" not in st.session_state:
        st.info("Run Career Risk Analysis first.")
    else:

        if st.button("Generate Executive Report"):

            entrapment = st.session_state.entrapment
            burnout = st.session_state.burnout
            runway = st.session_state.runway
            skill_count = st.session_state.skill_count

            if entrapment > 70:
                risk = "🔴 High Career Risk"
            elif entrapment > 40:
                risk = "🟠 Moderate Risk"
            else:
                risk = "🟢 Low Risk"

            recommendations = []

            if entrapment > 70:
                recommendations.append("Initiate job switch within 6 months.")
            if burnout > 60:
                recommendations.append("Reduce workload to prevent burnout.")
            if runway < 6:
                recommendations.append("Increase savings buffer to 6–12 months.")
            if skill_count < 4:
                recommendations.append("Add AI/Cloud/Data skills.")

            if not recommendations:
                recommendations.append("Maintain growth trajectory.")

            st.success(f"""
### Strategic Executive Assessment

Risk Level: {risk}

Recommendations:
- {'\n- '.join(recommendations)}
""").stButton>button {
    background: linear-gradient(135deg, #00f5ff, #7f00ff);
    border-radius: 25px;
    padding: 12px 28px;
    font-weight: bold;
    color: white !important;
    border: none;
}

.stButton>button:hover {
    box-shadow: 0 0 25px #00f5ff;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 0 20px rgba(0,255,255,0.4);
}

div[data-testid="stMetricValue"] {
    color: #00f5ff !important;
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HERO SECTION
# =====================================================

st.markdown("""
<div style="padding:50px;border-radius:25px;
background:linear-gradient(135deg,#00f5ff,#7f00ff);
text-align:center;
box-shadow:0 0 40px rgba(0,255,255,0.6);
margin-bottom:40px;">
<h1>🚀 AI Career Mobility Intelligence Platform (India)</h1>
<h3>Entrapment • Burnout • Market Demand • Skill Intelligence</h3>
</div>
""", unsafe_allow_html=True)

# =====================================================
# MARKET DATA
# =====================================================

market_data = pd.DataFrame({
    "Skill": ["python", "cloud", "ai", "ml", "devops", "data", "backend", "system design"],
    "DemandScore": [95, 90, 98, 92, 85, 93, 88, 87],
    "AvgSalary_LPA": [12, 15, 20, 18, 14, 16, 13, 17]
})

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs(
    ["🧠 Career Risk", "🏢 Market & Jobs", "📊 Skill Intelligence", "📈 Executive Summary"]
)

# =====================================================
# TAB 1 – CAREER RISK + BURNOUT
# =====================================================

with tab1:

    st.header("Career Entrapment & Burnout Prediction")

    col1, col2 = st.columns(2)

    with col1:
        skills = st.text_area("Your Skills (comma separated)")
        salary = st.number_input("Current Salary (₹ LPA)", min_value=0)
        years = st.number_input("Years of Experience", min_value=0)

    with col2:
        debt = st.number_input("Total Debt (₹)", min_value=0)
        savings = st.number_input("Savings (₹)", min_value=0)
        expenses = st.number_input("Monthly Expenses (₹)", min_value=1)

    analyze = st.button("Analyze Career")

    if analyze:

        skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
        skill_count = len(skill_list)

        portability = min(25, skill_count * 1.5)
        income_risk = 15
        debt_ratio = debt / salary if salary > 0 else 0
        runway = savings / expenses if expenses > 0 else 0

        lock_in = min(25, debt_ratio * 15 + (12/runway if runway > 0 else 10))
        decay = (1 - math.exp(-0.05 * years)) * 25

        total_score = min(100, portability + income_risk + lock_in + decay)
        burnout_probability = min(100, years * 4 + debt_ratio * 50)

        st.session_state.entrapment = total_score
        st.session_state.burnout = burnout_probability
        st.session_state.runway = runway
        st.session_state.skill_count = skill_count

    if "entrapment" in st.session_state:

        colA, colB, colC = st.columns(3)
        colA.metric("🔥 Entrapment Score", f"{round(st.session_state.entrapment,2)}/100")
        colB.metric("⚠ Burnout Probability", f"{round(st.session_state.burnout,2)}%")
        colC.metric("💰 Financial Runway", f"{round(st.session_state.runway,2)} months")

# =====================================================
# TAB 2 – LIVE JOB SCRAPING (UNCHANGED FROM app.py)
# =====================================================

with tab2:

    st.header("Live Market Intelligence")

    city = st.selectbox("Select Indian City", ["bangalore", "hyderabad", "mumbai", "pune", "chennai"])
    keyword = st.text_input("Job Keyword (e.g. python, cloud)")

    if st.button("Fetch Live Jobs"):

        APP_ID = os.getenv("ADZUNA_ID")
        APP_KEY = os.getenv("ADZUNA_KEY")

        url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={APP_ID}&app_key={APP_KEY}&what={keyword}&where={city}"

        try:
            response = requests.get(url)
            data = response.json()

            jobs = []
            for job in data.get("results", [])[:10]:
                jobs.append({
                    "Title": job["title"],
                    "Company": job.get("company", {}).get("display_name", "Unknown"),
                    "Location": job["location"]["display_name"]
                })

            if jobs:
                st.dataframe(pd.DataFrame(jobs))
            else:
                st.warning("No jobs found.")

        except:
            st.error("API failed. Add your Adzuna credentials.")

# =====================================================
# TAB 3 – SKILL GAP (UNCHANGED FROM app.py)
# =====================================================

with tab3:

    st.header("Skill Gap & Market Demand Analysis")

    resume_text = st.text_area("Paste Resume Text")

    if st.button("Analyze Skill Gap"):

        resume_lower = resume_text.lower()
        detected = [skill for skill in market_data["Skill"] if skill in resume_lower]
        missing = list(set(market_data["Skill"]) - set(detected))

        st.success(f"Detected Skills: {detected}")
        st.error(f"Missing High-Demand Skills: {missing}")

        demand_df = market_data.copy()
        demand_df["Present"] = demand_df["Skill"].apply(lambda x: 1 if x in detected else 0)

        fig = px.bar(
            demand_df,
            x="Skill",
            y="DemandScore",
            color="Present",
            title="Skill Demand vs Your Coverage",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TAB 4 – INTELLIGENT EXECUTIVE SUMMARY
# =====================================================

with tab4:

    st.header("Executive AI Summary")

    if "entrapment" not in st.session_state:
        st.info("Run Career Risk Analysis first.")
    else:

        if st.button("Generate Executive Report"):

            entrapment = st.session_state.entrapment
            burnout = st.session_state.burnout
            runway = st.session_state.runway
            skill_count = st.session_state.skill_count

            if entrapment > 70:
                risk = "🔴 High Career Risk"
            elif entrapment > 40:
                risk = "🟠 Moderate Risk"
            else:
                risk = "🟢 Low Risk"

            recommendations = []

            if entrapment > 70:
                recommendations.append("Initiate job switch within 6 months.")
            if burnout > 60:
                recommendations.append("Reduce workload to prevent burnout.")
            if runway < 6:
                recommendations.append("Increase savings buffer to 6–12 months.")
            if skill_count < 4:
                recommendations.append("Add AI/Cloud/Data skills.")

            if not recommendations:
                recommendations.append("Maintain growth trajectory.")

            st.success(f"""
### Strategic Executive Assessment

Risk Level: {risk}

Recommendations:
- {'\n- '.join(recommendations)}
""")
