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
    try:
        atmo = requests.get("https://api.open-meteo.com/v1/forecast?latitude=37.07&longitude=-94.63&current_weather=true&hourly=surface_pressure").json()
        pres = atmo['hourly']['surface_pressure'][-1]
        wnd = atmo['current_weather']['windspeed']
    except: pres, wnd = 1013.25, 0.0
    
    try:
        q = requests.get("https://qrng.anu.edu.au/API/jsonI.php?length=5&type=uint8", timeout=5).json()
        rng = np.var(q['data']) / 1000
    except: rng = 0.4288
    return rng, pres, wnd

rng, pres, wnd = get_data()
timestamp = datetime.now(pytz.timezone("US/Central")).strftime("%H:%M:%S")

# 2. IMMEDIATE UI RENDER (This breaks the 'Blank Screen' loop)
st.title("📡 PROJECT SENTINEL")
st.sidebar.write(f"⏱️ Sync: {timestamp}")

c1, c2, c3 = st.columns(3)
c1.metric("RNG", f"{rng:.4f}")
c2.metric("PRES", f"{pres}")
c3.metric("WIND", f"{wnd}")

if pres < 1010: st.error("🚨 VORTEX ALERT")
else: st.success("✅ FIELD STABLE")

# 3. DEFERRED AUDIO ENGINE (Only loads if you interact)
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

st.table(pd.DataFrame({'Metric': ['RNG', 'Pressure', 'Wind'], 'Value': [rng, pres, wnd]}))