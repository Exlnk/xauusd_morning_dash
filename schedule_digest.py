import os, datetime as dt, pytz
from util import get_xauusd_price, compute_dxy_from_pairs, get_yields, get_calendar_today, get_calendar_prevday, get_newsapi_gold, get_myfxbook_xauusd_sentiment, make_outlook
import requests

WAT = pytz.timezone("Africa/Lagos")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram keys not set.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram send error:", e)

def build_digest():
    xau = get_xauusd_price()
    dxy = compute_dxy_from_pairs()
    nominal, real = get_yields()
    today_cal = get_calendar_today()
    prev_cal = get_calendar_prevday()
    news = get_newsapi_gold()
    sent = get_myfxbook_xauusd_sentiment()
    xau_price = xau['price'] if xau['price'] else float("nan")
    outlook = make_outlook(today_cal, prev_cal, nominal, real, dxy, xau_price)
    
    message = f"*XAUUSD Morning Digest — {dt.datetime.now(WAT).strftime('%Y-%m-%d %H:%M')} WAT*\n"
    message += f"Gold (XAUUSD): {xau['price']} USD ({xau['source']})\nDXY: {dxy:.2f}\n"
    if sent: message += f"Retail Sentiment — Long: {sent['long_pct']}%, Short: {sent['short_pct']}%\n"
    message += "\n*Yesterday:*\n" + "\n".join(outlook["yesterday"]) + "\n"
    message += "*Current:*\n" + "\n".join(outlook["current"]) + "\n"
    message += "*Future:*\n" + "\n".join(outlook["future"]) + "\n"
    message += "*Possible Outcomes:*\n" + "\n".join(outlook["possible"]) + "\n"
    if news:
        message += "\n*Top News:*\n"
        for n in news[:5]:
            message += f"- {n['title']} ({n['source']})\n"
    return message

if __name__ == "__main__":
    digest = build_digest()
    print(digest)
    send_telegram(digest)
