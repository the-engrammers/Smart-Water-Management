# AT the END execute in Terminal space "VS CODE" this --> streamlit run app.py  
import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime, timedelta

from components.decision_box import render_decision_box
from components.controls import render_pump_controls
from components.analytics import render_analytics

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
if 'selected_zone' not in st.session_state:
    st.session_state.selected_zone = "All"
if 'water_cost_per_m3' not in st.session_state:
    st.session_state.water_cost_per_m3 = 0.5

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
    """Load sensor data from CSV, handling optional columns gracefully"""
    default_columns = ["timestamp", "device_id", "flow_rate", "status", "water_level", "temperature"]
    
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Ensure all expected columns exist, fill missing ones with NaN
        for col in default_columns:
            if col not in df.columns:
                df[col] = None
        
        return df
    return pd.DataFrame(columns=default_columns)

# 5. AI Decision Logic
def get_ai_recommendation(df, crop_type):
    """Generate AI-based irrigation recommendations based on sensor data"""
    if df.empty:
        # Simulate sensor data if no real data available
        soil_moisture = np.random.uniform(20, 35)
        flow_rate = np.random.uniform(0, 5)
        water_level = np.random.uniform(5, 15)  # meters depth
        temperature = np.random.uniform(18, 32)  # Celsius
    else:
        latest = df.iloc[-1]
        flow_rate = latest.get('flow_rate', 0) if pd.notna(latest.get('flow_rate')) else 0
        
        # Use water_level if available, otherwise estimate from flow_rate
        if 'water_level' in latest and pd.notna(latest.get('water_level')):
            water_level = latest['water_level']
            # Convert water level (depth in meters) to soil moisture estimate
            # Deeper water = lower soil moisture (inverse relationship)
            soil_moisture = max(15, min(50, 50 - (water_level * 2)))
        else:
            # Fallback: estimate soil moisture from flow_rate
            soil_moisture = max(15, 50 - (flow_rate * 2))
            water_level = None
        
        # Get temperature if available
        temperature = latest.get('temperature') if 'temperature' in latest and pd.notna(latest.get('temperature')) else None
    
    thresholds = CROP_THRESHOLDS[crop_type]
    
    # Enhanced reasoning with temperature and water level
    reasons = []
    
    if soil_moisture < thresholds["soil_moisture_min"]:
        action = "Start Irrigation"
        volume = thresholds["optimal_volume"]
        reasons.append(f"Soil moisture ({soil_moisture:.1f}%) below threshold ({thresholds['soil_moisture_min']}%)")
        urgency = "HIGH"
    elif soil_moisture < thresholds["soil_moisture_min"] + 5:
        action = "Monitor Closely"
        volume = thresholds["optimal_volume"] * 0.7
        reasons.append(f"Soil moisture ({soil_moisture:.1f}%) approaching threshold")
        urgency = "MEDIUM"
    else:
        action = "No Action Needed"
        volume = 0
        reasons.append(f"Soil moisture ({soil_moisture:.1f}%) is optimal for {crop_type}")
        urgency = "LOW"
    
    # Add temperature-based reasoning
    if temperature is not None:
        if temperature > 30:
            reasons.append(f"High temperature ({temperature:.1f}°C) increases water needs")
            if urgency == "LOW":
                urgency = "MEDIUM"
                if volume == 0:
                    volume = thresholds["optimal_volume"] * 0.5
        elif temperature < 15:
            reasons.append(f"Low temperature ({temperature:.1f}°C) reduces water needs")
    
    # Add water level context
    if water_level is not None:
        if water_level > 10:
            reasons.append(f"Deep groundwater ({water_level:.1f}m) - irrigation may be needed")
        elif water_level < 3:
            reasons.append(f"Shallow groundwater ({water_level:.1f}m) - good water availability")
    
    reason = " | ".join(reasons)
    
    return {
        "action": action,
        "volume": volume,
        "reason": reason,
        "urgency": urgency,
        "soil_moisture": soil_moisture,
        "flow_rate": flow_rate,
        "water_level": water_level,
        "temperature": temperature
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

    # Zone selector based on device IDs
    unique_zones = ["All"]
    if not df.empty and 'device_id' in df.columns:
        unique_zones += sorted([d for d in df['device_id'].dropna().unique()])

    selected_zone = st.selectbox("Select Zone", unique_zones, index=unique_zones.index(st.session_state.selected_zone) if st.session_state.selected_zone in unique_zones else 0)
    st.session_state.selected_zone = selected_zone

    st.session_state.water_cost_per_m3 = st.number_input(
        "Water cost per m³",
        min_value=0.0,
        value=float(st.session_state.water_cost_per_m3),
        step=0.1,
        help="Utilisé pour calculer les économies de coûts (1 m³ = 1000 L).",
    )

# 8. Filter logic (by zone)
if st.session_state.selected_zone != "All" and not df.empty and 'device_id' in df.columns:
    df = df[df['device_id'] == st.session_state.selected_zone]

# 9. Dashboard Header
st.title("🌊 SMART WATER MANAGEMENT SYSTEM")
st.caption(f"Last Updated: {time.strftime('%H:%M:%S')} | Crop: {st.session_state.selected_crop}")

recommendation = get_ai_recommendation(df, st.session_state.selected_crop)
render_decision_box(recommendation, zone=st.session_state.selected_zone)

# 11. Interactive Controls - Pump Buttons (via component)
render_pump_controls(recommendation, selected_zone=st.session_state.selected_zone)

# 12. Analytics Section - Water Savings & Trends
render_analytics(
    df=df,
    irrigation_history=st.session_state.irrigation_history,
    total_water_saved=st.session_state.total_water_saved,
    water_cost_per_m3=st.session_state.water_cost_per_m3,
    selected_zone=st.session_state.selected_zone,
)

# 13. Current Sensor Metrics
st.markdown("### 📊 Current Sensor Readings")
if not df.empty:
    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        current_flow = latest.get('flow_rate', 0) if pd.notna(latest.get('flow_rate')) else 0
        st.metric("Flow Rate", f"{current_flow:.2f} L/min")
    
    with col2:
        if 'temperature' in latest and pd.notna(latest.get('temperature')):
            current_temp = latest['temperature']
            st.metric("Temperature", f"{current_temp:.1f}°C")
        else:
            st.metric("Temperature", "N/A", delta="No data")
    
    with col3:
        if 'water_level' in latest and pd.notna(latest.get('water_level')):
            current_water_level = latest['water_level']
            # Water level is depth, so higher depth = lower availability
            depth_status = "Good" if current_water_level < 5 else "Deep"
            st.metric("Water Level (Depth)", f"{current_water_level:.2f}m", delta=depth_status)
        else:
            st.metric("Water Level (Depth)", "N/A", delta="No data")
    
    with col4:
        status = "CRITICAL" if len(df[df['status'] == 'Leak']) > 0 else "NOMINAL"
        st.metric("System Health", status)
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Flow Rate", "N/A", delta="Waiting for data")
    with col2:
        st.metric("Temperature", "N/A", delta="Waiting for data")
    with col3:
        st.metric("Water Level (Depth)", "N/A", delta="Waiting for data")
    with col4:
        st.metric("System Health", "NOMINAL")

# 14. Historical Metrics
st.markdown("### 📈 Historical Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Readings", len(df))
with col2:
    avg_flow = round(df['flow_rate'].mean(), 2) if not df.empty and 'flow_rate' in df.columns else 0
    st.metric("Avg Flow Rate", f"{avg_flow} L/min" if avg_flow > 0 else "N/A")
with col3:
    if not df.empty and 'temperature' in df.columns:
        avg_temp = df['temperature'].mean()
        if pd.notna(avg_temp):
            st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
        else:
            st.metric("Avg Temperature", "N/A")
    else:
        st.metric("Avg Temperature", "N/A")

# 15. Irrigation History & Data Visualization
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

# 16. Map & Charts
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📋 Sensor Data History (Real-time Log)")
    if not df.empty:
        # Select and order columns for display
        display_columns = ['timestamp', 'device_id', 'flow_rate']
        
        # Add optional columns if they exist and have data
        if 'temperature' in df.columns:
            display_columns.append('temperature')
        if 'water_level' in df.columns:
            display_columns.append('water_level')
        if 'status' in df.columns:
            display_columns.append('status')
        
        # Filter to only columns that exist in dataframe
        display_columns = [col for col in display_columns if col in df.columns]
        
        # Format the dataframe for better display
        display_df = df[display_columns].sort_values(by='timestamp', ascending=False).copy()
        
        # Format numeric columns for better readability
        if 'flow_rate' in display_df.columns:
            display_df['flow_rate'] = display_df['flow_rate'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        if 'temperature' in display_df.columns:
            display_df['temperature'] = display_df['temperature'].apply(lambda x: f"{x:.1f}°C" if pd.notna(x) else "N/A")
        if 'water_level' in display_df.columns:
            display_df['water_level'] = display_df['water_level'].apply(lambda x: f"{x:.2f}m" if pd.notna(x) else "N/A")
        
        st.dataframe(display_df, use_container_width=True)
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

# 17. Water savings are calculated when pump starts (handled in button click handler above)

# 18. Real-time Auto-refresh
if auto_refresh:
    time.sleep(10)
    st.rerun()
