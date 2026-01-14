import streamlit as st
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="SENTINEL", layout="centered")

# 1. LIGHTWEIGHT DATA FETCH
@st.cache_data(ttl=60)
def get_data():
    # Fetch Pressure
    try:
        atmo = requests.get("https://api.open-meteo.com/v1/forecast?latitude=37.07&longitude=-94.63&current_weather=true&hourly=surface_pressure").json()
        pres = atmo['hourly']['surface_pressure'][-1]
        wnd = atmo['current_weather']['windspeed']
    except: pres, wnd = 1013.25, 0.0
    
    # Fetch Quantum RNG
    try:
        q = requests.get("https://qrng.anu.edu.au/API/jsonI.php?length=5&type=uint8", timeout=5).json()
        rng = np.var(q['data']) / 1000
    except: rng = 0.4288
    return rng, pres, wnd

rng, pres, wnd = get_data()
timestamp = datetime.now(pytz.timezone("US/Central")).strftime("%H:%M:%S")

# --- VORTEX MATH ---
# Formula: (Standard Pres - Current Pres) * Chaos Factor
# If pressure is high (1020), risk is 0. If pressure drops (990), risk spikes.
pressure_drop = 1013.25 - pres
if pressure_drop < 0: pressure_drop = 0 # No risk if high pressure
risk_score = pressure_drop * rng * 2 # Scaling factor
if risk_score > 100: risk_score = 100
if risk_score < 0: risk_score = 0

# 2. UI DISPLAY
st.title("📡 PROJECT SENTINEL")
st.sidebar.write(f"⏱️ Sync: {timestamp}")

# Top Metrics
c1, c2, c3 = st.columns(3)
c1.metric("RNG Var", f"{rng:.4f}")
c2.metric("Pressure", f"{pres:.1f}")
c3.metric("Wind", f"{wnd}")

st.divider()

# PROBABILITY BAR
st.subheader("🌪️ Vortex Probability")
st.progress(int(risk_score))
st.caption(f"Current Threat Level: {risk_score:.1f}%")

if risk_score > 50:
    st.error("🚨 HIGH ALERT: ATMOSPHERIC INSTABILITY")
elif risk_score > 20:
    st.warning("⚠️ CAUTION: FIELD FLUX DETECTED")
else:
    st.success("✅ FIELD COHERENCE STABLE")

# 3. DEFERRED AUDIO ENGINE
st.divider()
st.subheader("🪷 Peace Radio")
if st.checkbox("Enable Audio Engine"):
    mode = st.radio("Mode:", ["7.83Hz", "60Hz", "Layered"])
    gain = st.slider("Volume", 0.0, 1.0, 0.3)
    
    if st.button("Broadcast"):
        t = np.linspace(0, 5, int(44100 * 5), False)
        if mode == "7.83Hz": note = np.sin(7.83 * t * 2 * np.pi) * gain
        elif mode == "60Hz": note = np.sin(60.0 * t * 2 * np.pi) * gain
        else: note = (np.sin(7.83 * t * 2 * np.pi) * 0.7 + np.sin(60.0 * t * 2 * np.pi) * 0.3) * gain
        st.audio(note, sample_rate=44100)

st.table(pd.DataFrame({'Metric': ['RNG', 'Pressure', 'Wind', 'Risk %'], 'Value': [rng, pres, wnd, risk_score]}))