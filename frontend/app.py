# AT the END execute in Terminal space "VS CODE" this --> streamlit run app.py  
import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Config & Branding
st.set_page_config(page_title="City Water Manager | Engrammers", layout="wide")

# Custom CSS to match "The Engrammers" aesthetic
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1a1c24;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #6366f1; /* Purple accent */
    }
    div[data-testid="stSidebar"] {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - Filtering
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=ENGRAMMERS", width=200) # Replace with actual logo
    st.title("Filters")
    selected_zone = st.selectbox("Select Zone", ["Zone A (Downtown)", "Zone B (Industrial)", "Zone C (Residential)"])
    date_range = st.date_input("Select Date Range")
    st.info("System Status: **KNOWLEDGE_NODE_ACTIVE**")

# 3. Header
st.title("City Water Management Dashboard")
st.markdown("---")

# 4. Metric Cards (Key Indicators)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Water Flow", value="1,240 m³/h", delta="12%")
with col2:
    st.metric(label="Current Pressure", value="4.2 Bar", delta="-0.5 Bar", delta_color="inverse")
with col3:
    st.metric(label="Active Leaks", value="3", delta="1 New", delta_color="inverse")

st.markdown("###")

# 5. Charts & Maps
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Flow Over Time")
    # Generating Dummy Data
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Zone A', 'Zone B', 'Zone C']
    )
    st.line_area_chart = st.line_chart(chart_data)

with right_col:
    st.subheader("Sensor Locations")
    # Dummy Map Data (centered roughly near Meknes/Morocco based on the image text)
    map_data = pd.DataFrame({
        'lat': [33.8935, 33.8950, 33.8910],
        'lon': [-5.5547, -5.5520, -5.5580]
    })
    st.map(map_data)

# 6. Footer
st.markdown("---")
st.caption("Engrammers Industrial-Grade AI & Optimization Solutions | Master IASDO")
