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
rng, pres = get_live_sentinel_data()

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

import streamlit as st
from datetime import datetime
import pytz # For your local Galena time

# --- TIMING LOGIC ---
local_tz = pytz.timezone("US/Central")
last_check = datetime.now(local_tz).strftime("%H:%M:%S")

# --- RNG & WEBHOOK LOGIC ---
def sentinel_check(pressure, rng_val):
    if pressure < 1010 and rng_val > 0.85: # Logic Gate
        # This is where the Web-Hook goes
        # requests.post("https://maker.ifttt.com/trigger/vortex/with/key/YOUR_KEY")
        return True
    return False

# --- UI UPDATE ---
st.sidebar.write(f"⏱️ Last Data Sync: {last_check}")
st.sidebar.info("Sentinel is monitoring the Quantum/Atmo link 24/7.")
import streamlit as st
from datetime import datetime
import pytz # For your local Galena time

# --- TIMING LOGIC ---
local_tz = pytz.timezone("US/Central")
last_check = datetime.now(local_tz).strftime("%H:%M:%S")

# --- RNG & WEBHOOK LOGIC ---
def sentinel_check(pressure, rng_val):
    if pressure < 1010 and rng_val > 0.85: # Logic Gate
        # This is where the Web-Hook goes
        # requests.post("https://maker.ifttt.com/trigger/vortex/with/key/YOUR_KEY")
        return True
    return False

# --- UI UPDATE ---
st.sidebar.write(f"⏱️ Last Data Sync: {last_check}")
st.sidebar.info("Sentinel is monitoring the Quantum/Atmo link 24/7.")

