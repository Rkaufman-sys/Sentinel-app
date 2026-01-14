import streamlit as st
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="SENTINEL MARK II", layout="centered")

# --- ENGINES ---
def get_coords(query):
    # Fix for City, State: Open-Meteo prefers just the name, but we can help it
    clean_query = query.split(',')[0].strip() 
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean_query}&count=5&language=en&format=json"
    try:
        res = requests.get(geo_url).json()
        if "results" in res:
            # If user provided a state (e.g. Paris, TX), we look for a match in the results
            if ',' in query:
                state_search = query.split(',')[1].strip().lower()
                for r in res["results"]:
                    admin1 = r.get("admin1", "").lower()
                    if state_search in admin1 or state_search == r.get("country_code", "").lower():
                        return r["latitude"], r["longitude"], f"{r['name']}, {r.get('admin1','')}", r["timezone"]
            
            # Default to the first result if no state match found
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
        q = requests.get("https://qrng.anu.edu.au/API/jsonI.php?length=5&type=uint8", timeout=5).json()
        rng = np.var(q['data']) / 1000
    except: rng = 0.4288
    return rng, pres, wnd

# --- UI START ---
st.title("📡 PROJECT SENTINEL")

# SIDEBAR
st.sidebar.header("Settings")
pb_token = st.sidebar.text_input("🔑 Pushbullet Token", type="password")

with st.sidebar.expander("🌐 Manual Coordinate Override"):
    m_lat = st.number_input("Lat:", value=0.0, format="%.2f")
    m_lon = st.number_input("Lon:", value=0.0, format="%.2f")
    use_manual = st.checkbox("USE MANUAL COORDS")

# MAIN SEARCH
search_query = st.text_input("🔍 Monitor Location:", "Galena, KS")

# LOGIC SWITCH: MANUAL VS SEARCH
if use_manual:
    lat, lon = m_lat, m_lon
    city_name = f"Point ({lat}, {lon})"
    tz_name = "UTC"
else:
    loc = get_coords(search_query)
    if loc:
        lat, lon, city_name, tz_name = loc
    else:
        st.error("Location not found. Use 'City, State' or Manual Coords.")
        st.stop()

# PULL DATA
rng, pres, wnd = get_data(lat, lon)
p_drop = 1013.25 - pres
risk = (p_drop if p_drop > 0 else 0) * rng * 2
if risk > 100: risk = 100

# DISPLAY
c1, c2, c3 = st.columns(3)
c1.metric("RNG Var", f"{rng:.4f}")
c2.metric("Pressure", f"{pres:.1f}")
c3.metric("Wind", f"{wnd}")

st.divider()
st.subheader(f"🌪️ Monitoring: {city_name}")
st.progress(int(risk))
st.caption(f"Risk Level: {risk:.1f}% | Coordinates: {lat}, {lon}")