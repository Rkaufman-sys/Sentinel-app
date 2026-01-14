import streamlit as st
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="SENTINEL FULL SUITE", layout="centered")

# --- ENGINES ---
def get_coords(query):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=1&language=en&format=json"
    try:
        res = requests.get(geo_url).json()
        if "results" in res:
            d = res["results"][0]
            return d["latitude"], d["longitude"], d["name"], d["timezone"]
    except: return None

@st.cache_data(ttl=60)
def get_data(lat, lon):
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

def send_push(token, score, city):
    if token:
        url = "https://api.pushbullet.com/v2/pushes"
        headers = {"Access-Token": token, "Content-Type": "application/json"}
        msg = f"⚠️ SENTINEL ALERT: {score:.1f}% Vortex Probability in {city}!"
        data = {"type": "note", "title": "PROJECT SENTINEL", "body": msg}
        requests.post(url, json=data, headers=headers)

# --- UI START ---
st.title("📡 PROJECT SENTINEL")
pb_token = st.sidebar.text_input("🔑 Pushbullet Token", type="password")
search_query = st.text_input("🔍 Monitor Location:", "Galena, KS")
# --- MANUAL COORDINATE OVERRIDE ---
with st.sidebar.expander("🌐 Manual Coordinate Override"):
    manual_lat = st.number_input("Lat:", value=0.0, format="%.2f")
    manual_lon = st.number_input("Lon:", value=0.0, format="%.2f")
    if st.checkbox("Use Manual Coordinates"):
        lat, lon = manual_lat, manual_lon
        city_name = f"Point ({lat}, {lon})"

loc = get_coords(search_query)
if loc:
    lat, lon, city_name, tz_name = loc
    rng, pres, wnd = get_data(lat, lon)
    timestamp = datetime.now(pytz.timezone(tz_name)).strftime("%H:%M:%S")
    
    # MATH
    p_drop = 1013.25 - pres
    risk = (p_drop if p_drop > 0 else 0) * rng * 2
    if risk > 100: risk = 100

    # TOP METRICS
    c1, c2, c3 = st.columns(3)
    c1.metric("RNG Var", f"{rng:.4f}")
    c2.metric("Pressure", f"{pres:.1f}")
    c3.metric("Wind", f"{wnd}")

    st.divider()
    st.subheader(f"🌪️ Vortex Probability: {city_name}")
    st.progress(int(risk))
    st.caption(f"Current Threat Level: {risk:.1f}%")

    if st.button("🚨 TEST ANDROID NOTIFICATION"):
        send_push(pb_token, risk, city_name)
        st.toast("Signal Sent")

    # PEACE RADIO
    st.divider()
    st.subheader("🪷 Peace Radio")
    if st.checkbox("Enable Audio Engine"):
        mode = st.radio("Mode:", ["7.83Hz", "60Hz", "Layered"])
        if st.button("Broadcast Tone"):
            t = np.linspace(0, 5, int(44100 * 5), False)
            gain = 0.3
            note = np.sin(7.83 * t * 2 * np.pi) * gain # Default
            st.audio(note, sample_rate=44100)

    # DATA TABLE
    st.table(pd.DataFrame({'Metric': ['RNG', 'Pressure', 'Wind', 'Risk %'], 'Value': [rng, pres, wnd, risk]}))