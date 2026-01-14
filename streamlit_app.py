import streamlit as st
import requests
import numpy as np
from datetime import datetime
import pytz

st.set_page_config(page_title="SENTINEL UNIVERSAL", layout="centered")

# --- PUSHBULLET LOGIC (100% FREE) ---
def send_push(token, score, city):
    if token:
        url = "https://api.pushbullet.com/v2/pushes"
        headers = {"Access-Token": token, "Content-Type": "application/json"}
        msg = f"⚠️ SENTINEL ALERT: {score:.1f}% Vortex Probability in {city}!"
        data = {"type": "note", "title": "PROJECT SENTINEL", "body": msg}
        try:
            requests.post(url, json=data, headers=headers)
            st.toast("📡 Signal Transmitted to Android")
        except:
            st.error("Connection Failed")

# --- CORE ENGINES ---
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
    except: pres = 1013.25
    try:
        q = requests.get("https://qrng.anu.edu.au/API/jsonI.php?length=5&type=uint8", timeout=5).json()
        rng = np.var(q['data']) / 1000
    except: rng = 0.4288
    return rng, pres

# --- UI ---
st.title("📡 PROJECT SENTINEL")
pb_token = st.sidebar.text_input("🔑 Pushbullet Token (Starts with o.)", type="password")
search_query = st.text_input("🔍 Monitor Location:", "Galena, KS")

location_data = get_coords(search_query)
if location_data:
    lat, lon, city_name, tz_name = location_data
    rng, pres = get_data(lat, lon)
    
    pressure_drop = 1013.25 - pres
    risk_score = (pressure_drop if pressure_drop > 0 else 0) * rng * 2
    
    st.metric("Risk Level", f"{risk_score:.1f}%")
    st.progress(int(risk_score) if risk_score < 100 else 100)

    if st.button("🚨 TEST ANDROID NOTIFICATION"):
        send_push(pb_token, risk_score, city_name)