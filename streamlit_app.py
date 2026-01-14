import streamlit as st
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="SENTINEL UNIVERSAL", layout="centered")

# --- 1. LOCATION SEARCH ENGINE ---
def get_coords(location_query):
    # This uses Open-Meteo's free geocoding API
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location_query}&count=1&language=en&format=json"
    try:
        res = requests.get(geo_url).json()
        if "results" in res:
            data = res["results"][0]
            return data["latitude"], data["longitude"], data["name"], data["timezone"]
    except:
        pass
    return None

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_sentinel_data(lat, lon):
    try:
        atmo = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=surface_pressure").json()
        pres = atmo['hourly']['surface_pressure'][-1]
        wnd = atmo['current_weather']['windspeed']
    except: pres, wnd = 1013.25, 0.0
    
    try:
        q = requests.get("https://qrng.anu.edu.au/API/jsonI.php?length=5&type=uint8", timeout=5).json()
        rng = np.var(q['data']) / 1000
    except: rng = 0.4288
    return rng, pres, wnd

# --- 3. UI LAYOUT ---
st.title("📡 PROJECT SENTINEL")
st.write("### Universal Early Warning System")

# THE SEARCH BAR
search_query = st.text_input("🔍 Enter Town or Zip Code:", "Galena, KS")
location_data = get_coords(search_query)

if location_data:
    lat, lon, city_name, tz_name = location_data
    rng, pres, wnd = get_sentinel_data(lat, lon)
    timestamp = datetime.now(pytz.timezone(tz_name)).strftime("%H:%M:%S")

    st.sidebar.success(f"Locked onto: {city_name}")
    st.sidebar.write(f"⏱️ Local Time: {timestamp}")

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("RNG Var", f"{rng:.4f}")
    c2.metric("Pressure", f"{pres:.1f}")
    c3.metric("Wind", f"{wnd}")

    # Vortex Math
    pressure_drop = 1013.25 - pres
    if pressure_drop < 0: pressure_drop = 0
    risk_score = pressure_drop * rng * 2 
    if risk_score > 100: risk_score = 100

    st.divider()
    st.subheader(f"🌪️ Vortex Probability: {city_name}")
    st.progress(int(risk_score))
    
    if risk_score > 50: st.error(f"🚨 ALERT: HIGH INSTABILITY IN {city_name.upper()}")
    elif risk_score > 20: st.warning("⚠️ FIELD FLUX DETECTED")
    else: st.success("✅ FIELD COHERENCE STABLE")

else:
    st.warning("Please enter a valid location to begin monitoring.")

# --- 4. PEACE RADIO ---
st.divider()
if st.checkbox("Enable Peace Radio (Harmonic Anchor)"):
    mode = st.radio("Mode:", ["7.83Hz", "60Hz", "Layered"])
    if st.button("Broadcast Tone"):
        t = np.linspace(0, 5, int(44100 * 5), False)
        gain = 0.3
        if mode == "7.83Hz": note = np.sin(7.83 * t * 2 * np.pi) * gain
        elif mode == "60Hz": note = np.sin(60.0 * t * 2 * np.pi) * gain
        else: note = (np.sin(7.83 * t * 2 * np.pi) * 0.7 + np.sin(60.0 * t * 2 * np.pi) * 0.3) * gain
        st.audio(note, sample_rate=44100)