import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Configuration & Styling ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1/staff" 
HOSPITAL_ID = "550e8400-e29b-41d4-a716-446655440000"

st.set_page_config(page_title="Arogya Mitra | HMS Executive", layout="wide", page_icon="🏥")

# Modern dark-theme styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #00d4ff; font-weight: 700; }
    .stTable { border: 1px solid #333; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏥 Arogya Mitra: Executive Command Center")
st.caption(f"Real-time Operational Intelligence | City Central Hospital (ID: {HOSPITAL_ID[:8]}...)")
st.markdown("---")

# --- 1. OPERATIONAL KPIS (Real-Time Handshake) ---
try:
    summary = requests.get(f"{API_BASE_URL}/summary/{HOSPITAL_ID}").json()
    readiness = requests.get(f"{API_BASE_URL}/availability/daily-readiness/{HOSPITAL_ID}").json()
    
    kpi1, kpi2, kpi3 = st.columns(3)
    
    # Workforce Strength
    kpi1.metric("Total Workforce", summary.get("total_headcount", 0), delta="Clinical Assets")
    
    # On-Duty Count (Filters for 'ACTIVE' status from Supabase)
    active = summary.get("status_distribution", {}).get("ACTIVE", 0)
    kpi2.metric("Active Clinical Staff", f"{active} On-Duty", delta="Live Status")
    
    # Surgeon Readiness (Calculated from doctor_availability)
    rate = readiness.get("readiness_rate", "0.00%")
    kpi3.metric("Live Readiness Rate", rate, delta="Operational")

except Exception as e:
    st.error("⚠️ Primary Data Feed Offline. Checking Backup...")

st.markdown("### 📊 Departmental Analytics & Deployment Stability")

# --- 2. ANALYTICS GRID (New 2026 Width Syntax) ---
col_left, col_right = st.columns(2)

with col_left:
    try:
        # Specialty Mix (Center of Excellence Distribution)
        spec_res = requests.get(f"{API_BASE_URL}/doctors/specialty-mix/{HOSPITAL_ID}").json()
        if spec_res:
            df_spec = pd.DataFrame(list(spec_res.items()), columns=['Department', 'Count'])
            fig_pie = px.pie(df_spec, values='Count', names='Department', hole=0.6,
                             title="Medical Center of Excellence",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            # 2026 Syntax: width='stretch'
            st.plotly_chart(fig_pie, width='stretch')
    except:
        st.info("Generating Departmental Insights...")

with col_right:
    try:
        # Nursing Deployment (Contract vs Permanent)
        shift_res = requests.get(f"{API_BASE_URL}/nurses/shift-load/{HOSPITAL_ID}").json()
        if shift_res:
            df_shift = pd.DataFrame(list(shift_res.items()), columns=['Status', 'Count'])
            fig_bar = px.bar(df_shift, x='Status', y='Count', color='Status',
                             title="Workforce Stability (Employment Type)",
                             color_discrete_map={'PERMANENT': '#00CC96', 'TEMPORARY': '#636EFA'})
            # 2026 Syntax: width='stretch'
            st.plotly_chart(fig_bar, width='stretch')
    except:
        st.info("Analyzing Deployment Stability...")

# --- 3. CLINICAL EXCELLENCE LEADERBOARD ---
st.markdown("### ⭐ Star Performers (Top Rated Specialists)")
try:
    top_docs = requests.get(f"{API_BASE_URL}/doctors/top-rated/{HOSPITAL_ID}").json()
    if top_docs:
        df_top = pd.DataFrame(top_docs)
        
        # Professional Formatting: Force 1-decimal place
        df_top['rating'] = df_top['rating'].apply(lambda x: f"{float(x):.1f} ⭐")
        
        # Cleanup Column Headers
        df_top.columns = ["Physician Name", "Specialization", "Clinical Rating", "Duty Status"]
        
        # 2026 Syntax: width='stretch'
        st.dataframe(df_top, width='stretch', hide_index=True)
    else:
        st.warning("Awaiting current shift performance data.")
except:
    st.error("Quality Feed Error")