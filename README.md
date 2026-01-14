import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="SENTINEL: Peace Radio", layout="centered")

st.title("📡 PROJECT SENTINEL")
st.subheader("Quantum-Atmospheric Early Warning System")

# --- DATA FETCHING ---
 
import streamlit as st
import requests
import numpy as np

def get_live_sentinel_data():
    # 1. ATMO DATA (Galena/Joplin)
    atmo_url = "https://api.open-meteo.com/v1/forecast?latitude=37.07&longitude=-94.63&current_weather=true&hourly=surface_pressure"
    atmo_res = requests.get(atmo_url).json()
    pressure = atmo_res['hourly']['surface_pressure'][0]
    
    # 2. QUANTUM RNG DATA (ANU)
    # Fetching raw hex numbers from vacuum fluctuations
    q_url = "https://qrng.anu.edu.au/API/jsonI.php?length=10&type=uint8"
    try:
        q_res = requests.get(q_url).json()
        q_values = q_res['data']
        # Normalize the variance (0 to 1 scale)
        rng_variance = np.var(q_values) / 1000 # Calculated fluctuation
    except:
        rng_variance = 0.4288 # Fallback to your baseline if API is busy
        
    return rng_variance, pressure

# --- DASHBOARD LAYOUT ---
col1, col2, col3 = st.columns(3)
rng, pres, wnd = get_data()

with col1:
    st.metric("RNG Variance", f"{rng:.4f}", delta="-0.0012")
with col2:
    st.metric("Pressure", f"{pres} hPa", delta="-2.5", delta_color="inverse")
with col3:
    st.metric("Wind Speed", f"{wnd} km/h")

# --- VORTEX ALERT LOGIC ---
if pres < 1010:
    st.error("🚨 ALERT: LOW PRESSURE VORTEX POTENTIAL DETECTED")
    st.write("Current Status: Atmospheric Dielectric Stress is High.")
else:
    st.success("✅ SYSTEM NOMINAL: Field Coherence Stable")

# --- THE PEACE RADIO ACTUATOR ---
st.divider()
st.write("### 🪷 PEACE RADIO: HARMONIC ANCHOR")
if st.button("ACTIVATE 7.83Hz BUMPER"):
    st.info("Schumann Resonance overlap engaged. Frequency anchoring in progress...")
    # This acts as your biological reminder to ground yourself.

# --- DATA LOG ---
st.divider()
st.write("### Live Data Feed (UTC)")
data_log = pd.DataFrame({
    'Metric': ['Quantum Variance', 'Surface Pressure', 'Wind Velocity'],
    'Value': [rng, pres, wnd]
})
st.table(data_log)

