# AT the END execute in Terminal space "VS CODE" this --> streamlit run app.py  
import streamlit as st
import pandas as pd
import numpy as np
import os
import time

# 1. Configuration & Branding
st.set_page_config(page_title="Engrammers | Live Water Monitor", layout="wide")

# Styling (Engrammers Dark Theme)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #FFFFFF; }
    div[data-testid="stMetric"] {
        background-color: #111111; border: 1px solid #2D2D2D;
        padding: 15px; border-radius: 5px; border-left: 5px solid #6236FF;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading Logic
LOG_FILE = "alert_logs.csv"

def load_data():
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    return pd.DataFrame(columns=["timestamp", "device_id", "flow_rate", "status"])

# 3. Sidebar Filters
with st.sidebar:
    st.title("THE ENGRAMMERS")
    st.write("🛠️ **Backend Status:** Connected")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox('Auto-refresh (10s)', value=True)
    
    st.markdown("---")
    df = load_data()
    
    unique_devices = ["All"] + list(df['device_id'].unique())
    selected_device = st.selectbox("Filter by Device ID", unique_devices)

# 4. Filter logic
if selected_device != "All":
    df = df[df['device_id'] == selected_device]

# 5. Dashboard Header
st.title("LIVE SENSOR **OPTIMIZATION**")
st.caption(f"Last Updated: {time.strftime('%H:%M:%S')}")

# 6. Top Metrics (Real Data)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Alerts Logged", len(df))
with col2:
    avg_flow = round(df['flow_rate'].mean(), 2) if not df.empty else 0
    st.metric("Avg Leak Flow", f"{avg_flow} L/min")
with col3:
    status = "CRITICAL" if len(df) > 0 else "NOMINAL"
    st.metric("System Health", status)

# 7. Map & Charts
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("🚨 Leak History (Real-time Log)")
    st.dataframe(df.sort_values(by='timestamp', ascending=False), use_container_width=True)

with right_col:
    st.subheader("📍 Sensor Locations")
    # Mapping actual device IDs to dummy coordinates for the map
    # In a real app, these would come from a database
    map_points = pd.DataFrame({
        'lat': [33.8938, 33.8950, 33.8910],
        'lon': [-5.5547, -5.5520, -5.5580],
        'device_id': ["SN-MEKNES-001", "SN-MEKNES-002", "SN-MEKNES-003"]
    })
    st.map(map_points)

# 8. Real-time Auto-refresh
if auto_refresh:
    time.sleep(10)
    st.rerun()
