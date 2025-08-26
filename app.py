import streamlit as st
from util import get_xauusd_price, compute_dxy_from_pairs, get_yields, get_calendar_today, get_calendar_prevday, get_newsapi_gold, get_myfxbook_xauusd_sentiment, make_outlook
import pandas as pd

st.set_page_config(page_title="XAUUSD Morning Dashboard", layout="wide")
st.title("XAUUSD Morning Dashboard — London Open")

# Refresh button
if st.button("🔄 Refresh"):
    st.experimental_rerun()

# Prices
xau = get_xauusd_price()
dxy = compute_dxy_from_pairs()
st.subheader("Live Prices")
st.write(f"Gold (XAUUSD): {xau['price']} USD ({xau['source']})")
st.write(f"DXY: {dxy:.2f}")

# Yields
nominal, real = get_yields()
st.subheader("Yields")
st.write(f"10y nominal: {nominal['value'].iloc[-1] if not nominal.empty else 'NA'}")
st.write(f"10y real: {real['value'].iloc[-1] if not real.empty else 'NA'}")

# Calendar
st.subheader("Economic Calendar")
today_cal = get_calendar_today()
prev_cal = get_calendar_prevday()
st.dataframe(today_cal)

# News
st.subheader("Gold & USD News / Geopolitics")
news = get_newsapi_gold()
if news:
    for n in news[:5]:
        st.markdown(f"- [{n['title']}]({n['url']}) — {n['source']}")
else:
    st.write("No news found.")

# Sentiment
st.subheader("Retail Sentiment")
sent = get_myfxbook_xauusd_sentiment()
if sent:
    st.write(f"Long: {sent['long_pct']}%, Short: {sent['short_pct']}% ({sent['source']})")
else:
    st.write("No sentiment data available.")

# Outlook
st.subheader("Outlook")
xau_price = xau['price'] if xau['price'] else float("nan")
outlook = make_outlook(today_cal, prev_cal, nominal, real, dxy, xau_price)
st.write("**Yesterday:**")
st.write(outlook["yesterday"])
st.write("**Current:**")
st.write(outlook["current"])
st.write("**Future / Possible:**")
st.write(outlook["future"])
st.write("**Possible Outcomes:**")
st.write(outlook["possible"])
