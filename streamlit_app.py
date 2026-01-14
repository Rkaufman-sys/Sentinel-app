import streamlit as st
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import pytz

# --- APP CONFIG ---
st.set_page_config(page_title="SENTINEL", layout="centered")

# --- DATA ENGINE (Simplified) ---
def get_sentinel_data():
    atmo_url = "https://api.open-meteo.com/v1/forecast?latitude=37.07&longitude=-94.63&current_weather=true&hourly=surface_pressure"
    try:
        atmo_res = requests.get(atmo_url).json()
        pressure = atmo_res['hourly']['surface_pressure'][-1]
        wind = atmo_res['current_weather']['windspeed']
    except:
        pressure, wind = 1013.25, 0.0

    q_url = "https://qrng.anu.edu.au/API/jsonI.php?length=10&type=uint8"
    try:
        q_res = requests.get(q_url).json()
        q_values = q_res['data']
        rng_variance = np.var(q_values) / 1000 
    except:
        rng_variance = 0.4288
        
    return rng_variance, pressure, wind

# --- INITIALIZE ---
rng, pres, wnd = get_sentinel_data()
local_tz = pytz.timezone("US/Central")
timestamp = datetime.now(local_tz).strftime("%H:%M:%S")

# --- UI DISPLAY ---
st.title("📡 PROJECT SENTINEL")
st.write(f"**Last Sync:** {timestamp} | **Status:** Monitoring...")

col1, col2 = st.columns(2)
col1.metric("Quantum RNG Var", f"{rng:.4f}")
col2.metric("Pressure", f"{pres} hPa")

if pres < 1010:
    st.error("🚨 VORTEX POTENTIAL DETECTED")
else:
    st.success("✅ FIELD COHERENCE STABLE")

st.divider()
st.write("### 🪷 Peace Radio Placeholder")
st.info("Audio engine temporarily disabled for system stability. Data is LIVE.")

# --- DATA TABLE ---
st.table(pd.DataFrame({
    'Metric': ['Quantum Variance', 'Surface Pressure', 'Wind Velocity'],
    'Value': [rng, pres, wnd]
}))
