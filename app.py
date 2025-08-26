import streamlit as st
import datetime as dt

st.set_page_config(page_title="XAUUSD Morning Dashboard", layout="wide")
st.title("XAUUSD Morning Dashboard — London Open (Demo Mode)")

# Refresh button
if st.button("🔄 Refresh"):
    st.experimental_rerun()

# ---------- Dummy Live Prices ----------
st.subheader("Live Prices")
xau_price = 1950.25
dxy_val = 105.23
st.write(f"Gold (XAUUSD): {xau_price} USD")
st.write(f"DXY: {dxy_val}")

# ---------- Dummy Yields ----------
st.subheader("Yields")
nominal_yield = 4.50
real_yield = 1.25
st.write(f"10y nominal: {nominal_yield}%")
st.write(f"10y real: {real_yield}%")

# ---------- Dummy Economic Calendar ----------
st.subheader("Economic Calendar")
calendar_data = [
    {"time": "07:00 WAT", "event": "US Consumer Confidence", "forecast": "110", "previous": "108"},
    {"time": "09:30 WAT", "event": "UK CPI", "forecast": "3.2%", "previous": "3.1%"},
    {"time": "10:00 WAT", "event": "EU Manufacturing PMI", "forecast": "48.5", "previous": "48.0"}
]
st.table(calendar_data)

# ---------- Dummy News / Geopolitics ----------
st.subheader("Gold & USD News / Geopolitics")
news_list = [
    "Gold steadies as dollar strengthens — Reuters",
    "US yields rise on Fed comments — Bloomberg",
    "Middle East tensions push safe-haven demand — CNBC"
]
for news in news_list:
    st.write(f"- {news}")

# ---------- Dummy Retail Sentiment ----------
st.subheader("Retail Sentiment")
long_pct = 60
short_pct = 40
st.write(f"Long: {long_pct}%, Short: {short_pct}%")

# ---------- Dummy Outlook ----------
st.subheader("Outlook")
st.write("**Yesterday:** US Consumer Confidence exceeded forecast, supporting USD")
st.write("**Current:** Gold consolidates near 1950, DXY stable")
st.write("**Future / Possible:** Fed comments could spike DXY; geopolitical tensions may lift gold")
st.write("**Possible Outcomes:** Gold up 1-2% if safe haven demand rises; down 1% if USD surges")
st.write(f"*Last refresh: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
