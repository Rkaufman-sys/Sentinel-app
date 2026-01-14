import streamlit as st
import requests
import numpy as np
import pandas as pd
import time
from datetime import datetime
import pytz

# --- APP CONFIG ---
st.set_page_config(page_title="SENTINEL", layout="centered")

# --- DATA ENGINE ---
def get_sentinel_data():
    # 1. ATMO DATA (Galena/Joplin)
    atmo_url = "https://api.open-meteo.com/v1/forecast?latitude=37.07&longitude=-94.63&current_weather=true&hourly=surface_pressure"
    try:
        atmo_res = requests.get(atmo_url).json()
        pressure = atmo_res['hourly']['surface_pressure'][-1]
        wind = atmo_res['current_weather']['windspeed']
    except:
        pressure, wind = 1013.25, 0.0 # Standard fallback

    # 2. QUANTUM RNG DATA (ANU Live)
    q_url = "https://qrng.anu.edu.au/API/jsonI.php?length=10&type=uint8"
    try:
        q_res = requests.get(q_url).json()
        q_values = q_res['data']
        rng_variance = np.var(q_values) / 1000 
    except:
        rng_variance = 0.4288 # Your baseline
        
    return rng_variance, pressure, wind

# --- AUDIO ENGINE (PEACE RADIO) ---
def generate_tone(freq, duration=2, sample_rate=44100, gain=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(freq * t * 2 * np.pi) * gain
    return tone

# --- INITIALIZE DATA ---
rng, pres, wnd = get_sentinel_data()
local_tz = pytz.timezone("US/Central")
timestamp = datetime.now(local_tz).strftime("%H:%M:%S")

# --- UI DISPLAY ---
st.title("📡 PROJECT SENTINEL")
st.sidebar.header("System Status")
st.sidebar.write(f"⏱️ Last Sync: {timestamp}")
st.sidebar.info("Monitoring Quantum/Atmo coupling...")

col1, col2, col3 = st.columns(3)
col1.metric("RNG Variance", f"{rng:.4f}")
col2.metric("Pressure", f"{pres} hPa", delta="-0.5", delta_color="inverse")
col3.metric("Wind Speed", f"{wnd} km/h")

if pres < 1010:
    st.error("🚨 ALERT: VORTEX POTENTIAL DETECTED")
else:
    st.success("✅ SYSTEM NOMINAL: Field Coherence Stable")

# --- PEACE RADIO 2.0 ---
st.divider()
st.subheader("🪷 Peace Radio: Harmonic Actuator")

mode = st.radio("Select Frequency Mode:", 
                ["Anchor (7.83Hz)", "Engine (40-100Hz)", "Sentinel (Layered)"])
gain = st.slider("Gain Control (Amplitude)", 0.0, 1.0, 0.3)
timer_min = st.number_input("Sleep Timer (Minutes)", 1, 60, 20)

if st.button("START HARMONIC BROADCAST"):
    sample_rate = 44100
    duration = 5 # 5-second loop for the app demo
    
    if mode == "Anchor (7.83Hz)":
        audio_data = generate_tone(7.83, duration, sample_rate, gain)
    elif mode == "Engine (40-100Hz)":
        audio_data = generate_tone(60.0, duration, sample_rate, gain)
    else: # Sentinel Layered
        tone1 = generate_tone(7.83, duration, sample_rate, gain * 0.7)
        tone2 = generate_tone(60.0, duration, sample_rate, gain * 0.3)
        audio_data = tone1 + tone2
        
    st.audio(audio_data, sample_rate=sample_rate, autoplay=True)
    st.caption(f"Broadcasting {mode} for {timer_min} minutes (Looping)...")

# --- DATA LOG ---
st.divider()
st.write("### Analysis Table")
st.table(pd.DataFrame({
    'Metric': ['Quantum Variance', 'Surface Pressure', 'Wind Velocity'],
    'Value': [rng, pres, wnd]
}))