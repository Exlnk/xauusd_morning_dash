import os, time, math, datetime as dt, pytz, requests, pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

WAT = pytz.timezone("Africa/Lagos")

def now_wat():
    return dt.datetime.now(WAT)

# ---------- Price feeds ----------
def get_xauusd_price():
    """Try Twelve Data first, fallback to Finnhub (OANDA:XAU_USD). Returns {'price': float, 'source': str}"""
    td_key = os.getenv("TWELVEDATA_API_KEY")
    if td_key:
        try:
            url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={td_key}"
            r = requests.get(url, timeout=10)
            j = r.json()
            if "price" in j:
                return {"price": float(j["price"]), "source": "TwelveData"}
        except Exception:
            pass
    # Finnhub fallback
    fh_key = os.getenv("FINNHUB_API_KEY")
    if fh_key:
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol=OANDA:XAU_USD&token={fh_key}"
            j = requests.get(url, timeout=10).json()
            if "c" in j and j["c"]:
                return {"price": float(j["c"]), "source": "Finnhub (OANDA)"}
        except Exception:
            pass
    return {"price": float("nan"), "source": "none"}

def get_fx_pair(pair):
    td_key = os.getenv("TWELVEDATA_API_KEY")
    if td_key:
        try:
            url = f"https://api.twelvedata.com/price?symbol={pair}&apikey={td_key}"
            j = requests.get(url, timeout=10).json()
            if "price" in j: return float(j["price"])
        except Exception:
            pass
    fh_key = os.getenv("FINNHUB_API_KEY")
    if fh_key:
        sym = pair.replace("/", "_")
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol=OANDA:{sym}&token={fh_key}"
            j = requests.get(url, timeout=10).json()
            if "c" in j and j["c"]: return float(j["c"])
        except Exception:
            pass
    return float("nan")

def compute_dxy_from_pairs():
    w = {"EURUSD": 0.576, "USDJPY": 0.136, "GBPUSD": 0.119, "USDCAD": 0.091, "USDSEK": 0.042, "USDCHF": 0.036}
    eurusd = get_fx_pair("EUR/USD")
    usdjpy = get_fx_pair("USD/JPY")
    gbpusd = get_fx_pair("GBP/USD")
    usdcad = get_fx_pair("USD/CAD")
    usdsek = get_fx_pair("USD/SEK")
    usdchf = get_fx_pair("USD/CHF")
    if any(math.isnan(x) for x in [eurusd, usdjpy, gbpusd, usdcad, usdsek, usdchf]):
        return float("nan")
    try:
        dxy = 50.14348112 * (eurusd ** (-w["EURUSD"])) * (usdjpy ** (w["USDJPY"])) * (gbpusd ** (-w["GBPUSD"])) \
              * (usdcad ** (w["USDCAD"])) * (usdsek ** (w["USDSEK"])) * (usdchf ** (w["USDCHF"]))
        return float(dxy)
    except Exception:
        return float("nan")

# ---------- Yields / Fed ----------
def fred_series(series_id, api_key=None):
    api_key = api_key or os.getenv("FRED_API_KEY")
    if not api_key: return pd.DataFrame()
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&observation_start=2020-01-01&file_type=json"
    j = requests.get(url, timeout=15).json()
    obs = j.get("observations", [])
    if not obs: return pd.DataFrame()
    df = pd.DataFrame(obs)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    return df[["date", "value"]]

def get_yields():
    dgs10 = fred_series("DGS10")  # 10y nominal
    dfii10 = fred_series("DFII10")  # 10y real yield
    return dgs10, dfii10

# ---------- Economic calendar ----------
def get_calendar_today():
    key = os.getenv("TE_API_KEY")
    if not key:
        return pd.DataFrame()
    today_wat = now_wat().date()
    start = dt.datetime.combine(today_wat, dt.time(0,0)).astimezone(pytz.UTC)
    end   = dt.datetime.combine(today_wat, dt.time(23,59)).astimezone(pytz.UTC)
    url = f"https://api.tradingeconomics.com/calendar?d1={start:%Y-%m-%d}&d2={end:%Y-%m-%d}&c=United%20States,Euro%20Area,China,Japan,United%20Kingdom&importance=2,3&format=json&client={key}"
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return pd.DataFrame()
    j = r.json()
    if not isinstance(j, list):
        return pd.DataFrame()
    df = pd.DataFrame(j)
    keep_cols = [c for c in df.columns if c.lower() in {
        "country", "category", "title", "date", "actual", "previous", "forecast", "importance", "unit", "source"
    }]
    if "Date" in df.columns: df["date"] = pd.to_datetime(df["Date"])
    elif "date" in df.columns: df["date"] = pd.to_datetime(df["date"])
    else: df["date"] = pd.NaT
    return df[keep_cols + ["date"]].sort_values("date")

def get_calendar_prevday():
    key = os.getenv("TE_API_KEY")
    if not key: return pd.DataFrame()
    yday_wat = now_wat().date() - dt.timedelta(days=1)
    start = dt.datetime.combine(yday_wat, dt.time(0,0)).astimezone(pytz.UTC)
    end   = dt.datetime.combine(yday_wat, dt.time(23,59)).astimezone(pytz.UTC)
    url = f"https://api.tradingeconomics.com/calendar?d1={start:%Y-%m-%d}&d2={end:%Y-%m-%d}&c=United%20States,Euro%20Area,China,Japan,United%20Kingdom&importance=2,3&format=json&client={key}"
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return pd.DataFrame()
    j = r.json()
    if not isinstance(j, list):
        return pd.DataFrame()
    df = pd.DataFrame(j)
    if "Date" in df.columns: df["date"] = pd.to_datetime(df["Date"])
    elif "date" in df.columns: df["date"] = pd.to_datetime(df["date"])
    else: df["date"] = pd.NaT
    keep_cols = [c for c in df.columns if c.lower() in {"country","category","title","date","actual","previous","forecast","importance","unit"}]
    return df[keep_cols + ["date"]].sort_values("date")

# ---------- News & Geopolitics ----------
def get_newsapi_gold():
    key = os.getenv("NEWSAPI_KEY")
    if not key: return []
    q = "gold OR XAUUSD OR \"U.S. dollar\" OR DXY OR \"Treasury yields\" OR \"Federal Reserve\" OR geopolitics OR Middle East OR Israel OR Ukraine OR China"
    url = f"https://newsapi.org/v2/everything?q={requests.utils.quote(q)}&language=en&sortBy=publishedAt&pageSize=20"
    r = requests.get(url, headers={"X-Api-Key": key}, timeout=20)
    if r.status_code != 200: return []
    j = r.json()
    out = []
    for a in j.get("articles", []):
        out.append({
            "source": a.get("source",{}).get("name"),
            "title": a.get("title"),
            "url": a.get("url"),
            "publishedAt": a.get("publishedAt")
        })
    return out

# ---------- Retail sentiment (IG/Myfxbook) ----------
def get_myfxbook_xauusd_sentiment():
    url = "https://www.myfxbook.com/community/outlook/XAUUSD"
    try:
        html = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True)
        import re
        short = re.search(r"Short\s+(\d+)\s*%", text)
        long = re.search(r"Long\s+(\d+)\s*%", text)
        if short and long:
            return {"short_pct": int(short.group(1)), "long_pct": int(long.group(1)), "source": "Myfxbook (scrape)"}
    except Exception:
        pass
    return None

def make_outlook(today_cal_df, prev_cal_df, yields_10y, real_10y, dxy_val, xau_price):
    def last_value(df):
        if isinstance(df, pd.DataFrame) and not df.empty:
            return float(df.dropna(subset=["value"]).iloc[-1]["value"])
        return float("nan")
    bullets = {"yesterday": [], "current": [], "future": [], "possible": []}
    if isinstance(prev_cal_df, pd.DataFrame) and not prev_cal_df.empty:
        for _, row in prev_cal_df.sort_values(["importance","date"], ascending=[False, False]).head(3).iterrows():
            bullets["yesterday"].append(f"{row.get('country','')} {row.get('title','')}: actual {row.get('actual','?')} vs {row.get('forecast','?')} (prev {row.get('previous','?')})")
    if isinstance(today_cal_df, pd.DataFrame) and not today_cal_df.empty:
        for _, row in today_cal_df.sort_values(["importance","date"], ascending=[False, False]).head(3).iterrows():
            bullets["current"].append(f"{row.get('country','')} {row.get('title','')}: forecast {row.get('forecast','?')}")
    # Future outlook — next 3 events
    # DXY / yields
    bullets["future"].append(f"DXY ~ {dxy_val:.2f}, XAUUSD ~ {xau_price:.2f}")
    bullets["future"].append(f"10y nominal yield: {last_value(yields_10y):.2f}%, real yield: {last_value(real_10y):.2f}%")
    return bullets
