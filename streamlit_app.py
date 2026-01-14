import streamlit as st
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="SENTINEL MARK II", layout="centered")

# --- ENGINES ---
def get_coords(query):
    # Splits "Paris, TX" into "Paris" for the search
    clean_query = query.split(',')[0].strip() 
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean_query}&count=10&language=en&format=json"
    try:
        res = requests.get(geo_url).json()
        if "results" in res:
            # If user provided a state (e.g. Paris, TX), we filter for it
            if ',' in query:
                state_search = query.split(',')[1].strip().lower()
                for r in res["results"]:
                    admin1 = r.get("admin1", "").lower()
                    if state_search in admin1 or state_search == r.get("country_code", "").lower():
                        return r["latitude"], r["longitude"], f"{r['name']}, {r.get('admin1','')}", r["timezone"]
            
            # Default to top result
            d = res["results"][0]
            return d["latitude"], d["longitude"], f"{d['name']}, {d.get('admin1','')}", d["timezone"]
    except: return None

@st.cache_data(ttl=60)
def get_data(lat, lon):
    try:
        atmo = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=surface_pressure").json()
        pres = atmo['hourly']['surface_pressure'][-1]
        wnd = atmo['current_weather']['windspeed']
    except: pres, wnd = 1013.25, 0.0
    try:
        # Quantum RNG Source (ANU Canberra)
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

# --- UI & SIDEBAR ---
st.title("📡 PROJECT SENTINEL")
st.sidebar.header("Command Console")
pb_token = st.sidebar.text_input("🔑 Pushbullet Token", type="password")

with st.sidebar.expander("🌐 Manual Coordinate Override"):
    m_lat = st.number_input("Latitude:", value=0.0, format="%.4f")
    m_lon = st.number_input("Longitude:", value=0.0, format="%.4f")
    use_manual = st.checkbox("ENABLE MANUAL OVERRIDE")

# --- CORE LOGIC ---
search_query = st.text_input("🔍 Monitor Location (City, State):", "Galena, KS")

# THE IRONCLAD SWITCH
if use_manual:
    lat, lon = m_lat, m_lon
    city_name = f"Point ({lat}, {lon})"
    tz_name = "UTC"
    st.sidebar.success("Manual Tracking Active")
else:
    loc = get_coords(search_query)
    if loc:
        lat, lon, city_name, tz_name = loc
    else:
        st.error("Location not found. Try 'City, State' or check sidebar.")
        st.stop()

# DATA PROCESSING
rng, pres, wnd = get_data(lat, lon)
p_drop = 1013.25 - pres
risk = (p_drop if p_drop > 0 else 0) * rng * 2
if risk > 100: risk = 100

# MAIN DASHBOARD
c1, c2, c3 = st.columns(3)
c1.metric("RNG Var", f"{rng:.4f}")
c2.metric("Pressure", f"{pres:.1f}")
c3.metric("Wind", f"{wnd} mph")

st.divider()
st.subheader(f"🌪️ Vortex Probability: {city_name}")
st.progress(int(risk))
st.caption(f"Current Risk: {risk:.1f}% | Mode: {'Manual' if use_manual else 'Search'}")

if st.button("🚨 TEST ANDROID NOTIFICATION"):
    send_push(pb_token, risk, city_name)
    st.toast("Signal Transmitted")

# PEACE RADIO & DATA TABLE
st.divider()
if st.checkbox("Show Technical Data"):
    st.table(pd.DataFrame({'Metric': ['RNG', 'Pressure', 'Wind', 'Lat/Lon'], 'Value': [rng, pres, wnd, f"{lat}, {lon}"]}))