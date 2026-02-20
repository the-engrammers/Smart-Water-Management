# AT the END execute in Terminal space "VS CODE" this --> streamlit run app.py  
import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime, timedelta

# 1. Configuration & Branding
st.set_page_config(page_title="Engrammers | Smart Water Management", layout="wide")

# Styling (Engrammers Dark Theme)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #FFFFFF; }
    div[data-testid="stMetric"] {
        background-color: #111111; border: 1px solid #2D2D2D;
        padding: 15px; border-radius: 5px; border-left: 5px solid #6236FF;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #6236FF;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .pump-control {
        background-color: #1a1a1a;
        border: 2px solid #2D2D2D;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Initialize Session State
if 'pump_status' not in st.session_state:
    st.session_state.pump_status = "STOPPED"
if 'total_water_saved' not in st.session_state:
    st.session_state.total_water_saved = 0.0
if 'irrigation_history' not in st.session_state:
    st.session_state.irrigation_history = []
if 'selected_crop' not in st.session_state:
    st.session_state.selected_crop = "Olives"

# 3. Crop-Specific Thresholds
CROP_THRESHOLDS = {
    "Olives": {
        "soil_moisture_min": 25.0,  # %
        "optimal_volume": 40.0,      # L
        "irrigation_duration": 30,   # minutes
        "water_needs": "Low-Medium"
    },
    "Wheat": {
        "soil_moisture_min": 30.0,
        "optimal_volume": 60.0,
        "irrigation_duration": 45,
        "water_needs": "Medium-High"
    },
    "Tomatoes": {
        "soil_moisture_min": 35.0,
        "optimal_volume": 50.0,
        "irrigation_duration": 40,
        "water_needs": "High"
    },
    "Corn": {
        "soil_moisture_min": 32.0,
        "optimal_volume": 70.0,
        "irrigation_duration": 50,
        "water_needs": "High"
    },
    "Barley": {
        "soil_moisture_min": 28.0,
        "optimal_volume": 55.0,
        "irrigation_duration": 42,
        "water_needs": "Medium"
    }
}

# 4. Data Loading Logic
LOG_FILE = "alert_logs.csv"

def load_data():
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    return pd.DataFrame(columns=["timestamp", "device_id", "flow_rate", "status"])

# 5. AI Decision Logic
def get_ai_recommendation(df, crop_type):
    """Generate AI-based irrigation recommendations based on sensor data"""
    if df.empty:
        # Simulate sensor data if no real data available
        soil_moisture = np.random.uniform(20, 35)
        flow_rate = np.random.uniform(0, 5)
    else:
        # Estimate soil moisture from water level (simulated conversion)
        latest = df.iloc[-1]
        # Simulate soil moisture: lower flow_rate = lower moisture
        soil_moisture = max(15, 50 - (latest['flow_rate'] * 2))
        flow_rate = latest['flow_rate']
    
    thresholds = CROP_THRESHOLDS[crop_type]
    
    if soil_moisture < thresholds["soil_moisture_min"]:
        action = "Start Irrigation"
        volume = thresholds["optimal_volume"]
        reason = f"Soil moisture ({soil_moisture:.1f}%) below threshold ({thresholds['soil_moisture_min']}%)"
        urgency = "HIGH"
    elif soil_moisture < thresholds["soil_moisture_min"] + 5:
        action = "Monitor Closely"
        volume = thresholds["optimal_volume"] * 0.7
        reason = f"Soil moisture ({soil_moisture:.1f}%) approaching threshold"
        urgency = "MEDIUM"
    else:
        action = "No Action Needed"
        volume = 0
        reason = f"Soil moisture ({soil_moisture:.1f}%) is optimal for {crop_type}"
        urgency = "LOW"
    
    return {
        "action": action,
        "volume": volume,
        "reason": reason,
        "urgency": urgency,
        "soil_moisture": soil_moisture,
        "flow_rate": flow_rate
    }

# 6. Calculate Efficiency Score
def calculate_efficiency_score():
    """Calculate water savings compared to traditional manual watering"""
    # Traditional manual watering typically uses 20-30% more water
    baseline_usage = 100.0  # 100% baseline
    ai_usage = 75.0  # AI uses 75% (25% savings)
    
    if st.session_state.total_water_saved > 0:
        # Calculate based on actual savings
        efficiency = min(100, (st.session_state.total_water_saved / baseline_usage) * 100 + 75)
    else:
        efficiency = 75.0  # Default AI efficiency
    
    savings_percentage = 100 - ai_usage
    return efficiency, savings_percentage

# 7. Sidebar Filters
with st.sidebar:
    st.title("THE ENGRAMMERS")
    st.write("🛠️ **Backend Status:** Connected")
    
    # Crop Selection
    st.markdown("### 🌾 Crop Configuration")
    selected_crop = st.selectbox(
        "Select Crop Type",
        options=list(CROP_THRESHOLDS.keys()),
        index=list(CROP_THRESHOLDS.keys()).index(st.session_state.selected_crop)
    )
    st.session_state.selected_crop = selected_crop
    
    crop_info = CROP_THRESHOLDS[selected_crop]
    st.info(f"""
    **Crop:** {selected_crop}
    **Min Moisture:** {crop_info['soil_moisture_min']}%
    **Optimal Volume:** {crop_info['optimal_volume']}L
    **Water Needs:** {crop_info['water_needs']}
    """)
    
    st.markdown("---")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox('Auto-refresh (10s)', value=True)
    
    st.markdown("---")
    df = load_data()
    
    unique_devices = ["All"] + list(df['device_id'].unique()) if not df.empty else ["All"]
    selected_device = st.selectbox("Filter by Device ID", unique_devices)

# 8. Filter logic
if selected_device != "All" and not df.empty:
    df = df[df['device_id'] == selected_device]

# 9. Dashboard Header
st.title("🌊 SMART WATER MANAGEMENT SYSTEM")
st.caption(f"Last Updated: {time.strftime('%H:%M:%S')} | Crop: {st.session_state.selected_crop}")

# 10. AI Decision Box - Smart Recommendations
st.markdown("### 🤖 Smart Recommendations")
recommendation = get_ai_recommendation(df, st.session_state.selected_crop)

urgency_colors = {
    "HIGH": "#FF4444",
    "MEDIUM": "#FFAA00",
    "LOW": "#44FF44"
}

st.markdown(f"""
    <div class="recommendation-box">
        <h3 style="color: {urgency_colors[recommendation['urgency']]}; margin-bottom: 15px;">
            {recommendation['action']}
        </h3>
        <p style="font-size: 16px; margin: 10px 0;">
            <strong>Volume:</strong> {recommendation['volume']:.1f}L
        </p>
        <p style="font-size: 14px; color: #AAAAAA; margin: 10px 0;">
            <strong>Reason:</strong> {recommendation['reason']}
        </p>
        <p style="font-size: 12px; color: #888888; margin-top: 10px;">
            Current Soil Moisture: {recommendation['soil_moisture']:.1f}% | 
            Flow Rate: {recommendation['flow_rate']:.2f} L/min
        </p>
    </div>
""", unsafe_allow_html=True)

# 11. Interactive Controls - Pump Buttons
st.markdown("### ⚙️ Pump Controls")
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("🚀 Start Pump", type="primary", use_container_width=True):
        st.session_state.pump_status = "RUNNING"
        if recommendation['volume'] > 0:
            # Log irrigation event
            irrigation_event = {
                "timestamp": datetime.now(),
                "volume": recommendation['volume'],
                "crop": st.session_state.selected_crop,
                "action": "Started"
            }
            st.session_state.irrigation_history.append(irrigation_event)
            # Calculate water savings (AI uses optimal amount vs manual over-watering)
            manual_waste = recommendation['volume'] * 0.25  # Manual typically wastes 25%
            st.session_state.total_water_saved += manual_waste
            st.success(f"Pump started! Irrigating {recommendation['volume']:.1f}L for {st.session_state.selected_crop}")
        else:
            st.warning("No irrigation needed at this time.")

with col2:
    if st.button("🛑 Stop Pump", type="secondary", use_container_width=True):
        st.session_state.pump_status = "STOPPED"
        st.info("Pump stopped successfully")

with col3:
    pump_status_color = "#44FF44" if st.session_state.pump_status == "RUNNING" else "#FF4444"
    st.markdown(f"""
        <div class="pump-control">
            <h2 style="color: {pump_status_color}; margin: 0;">
                {st.session_state.pump_status}
            </h2>
        </div>
    """, unsafe_allow_html=True)

# 12. Optimization Insights - Efficiency Score
st.markdown("### 📊 Optimization Insights")
efficiency_score, savings_percentage = calculate_efficiency_score()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Efficiency Score", f"{efficiency_score:.1f}%", delta=f"+{savings_percentage:.1f}% vs Manual")
with col2:
    st.metric("Water Saved", f"{st.session_state.total_water_saved:.1f}L", delta="This Session")
with col3:
    manual_estimate = 100.0  # Estimated manual usage
    ai_usage = manual_estimate - st.session_state.total_water_saved
    st.metric("AI Usage", f"{ai_usage:.1f}L", delta=f"-{st.session_state.total_water_saved:.1f}L")
with col4:
    irrigation_count = len(st.session_state.irrigation_history)
    st.metric("Irrigations", irrigation_count, delta="Today")

# 13. Top Metrics (Real Data)
st.markdown("### 📈 System Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Alerts Logged", len(df))
with col2:
    avg_flow = round(df['flow_rate'].mean(), 2) if not df.empty else 0
    st.metric("Avg Flow Rate", f"{avg_flow} L/min")
with col3:
    status = "CRITICAL" if len(df) > 0 else "NOMINAL"
    st.metric("System Health", status)

# 14. Irrigation History & Data Visualization
st.markdown("### 📋 Irrigation History")
if st.session_state.irrigation_history:
    history_df = pd.DataFrame(st.session_state.irrigation_history)
    history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
    st.dataframe(
        history_df.sort_values(by='timestamp', ascending=False),
        use_container_width=True
    )
else:
    st.info("No irrigation events recorded yet. Start the pump to begin tracking.")

# 15. Map & Charts
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("🚨 Leak History (Real-time Log)")
    if not df.empty:
        st.dataframe(df.sort_values(by='timestamp', ascending=False), use_container_width=True)
    else:
        st.info("No sensor data available. Waiting for sensor readings...")

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

# 16. Water savings are calculated when pump starts (handled in button click handler above)

# 17. Real-time Auto-refresh
if auto_refresh:
    time.sleep(10)
    st.rerun()
