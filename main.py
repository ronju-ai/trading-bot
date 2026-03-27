import yfinance as yf
import pandas_ta as ta
import requests
import time
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "SureShot Alpha Bot is Active"

# আপনার সঠিক তথ্য
BOT_TOKEN = "8544115249:AAF0x33M2EcojgKjrRdTCV4eFpeoaZjT0Lo"
CHAT_ID = "8325386840"

# রিয়েল মার্কেট পেয়ার
PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "EURJPY=X", "GBPJPY=X"]
BD_TIMEZONE = pytz.timezone('Asia/Dhaka')

def analyze_market():
    now = datetime.now(BD_TIMEZONE)
    entry_time = now.replace(minute=((now.minute // 5) + 1) * 5 % 60, second=0).strftime('%I:%M %p')

    for pair in PAIRS:
        try:
            df = yf.download(pair, interval="5m", period="2d", progress=False)
            if df.empty: continue

            df['EMA8'] = ta.ema(df['Close'], length=8)
            df['EMA21'] = ta.ema(df['Close'], length=21)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            
            last = df.iloc[-1]
            is_strong = abs(last['Close'] - last['Open']) > (last['High'] - last['Low']) * 0.5

            msg = None
            if last['EMA8'] > last['EMA21'] and last['RSI'] > 55 and adx['ADX_14'].iloc[-1] > 25 and is_strong:
                msg = f"🚀 *QUOTEX CALL* 🟢\n✅ *SURESHOT SIGNAL*\n\n📊 Pair: {pair.replace('=X','')}\n📈 Direction: UP\n⏰ Entry: {entry_time}\n💡 Analysis: Strong Bullish Pattern"

            elif last['EMA8'] < last['EMA21'] and last['RSI'] < 45 and adx['ADX_14'].iloc[-1] > 25 and is_strong:
                msg = f"🚀 *QUOTEX PUT* 🔴\n✅ *SURESHOT SIGNAL*\n\n📊 Pair: {pair.replace('=X','')}\n📉 Direction: DOWN\n⏰ Entry: {entry_time}\n💡 Analysis: Strong Bearish Pattern"

            if msg:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        except: continue

def main_loop():
    while True:
        now = datetime.now(BD_TIMEZONE)
        if now.minute % 5 == 4 and now.second == 45:
            analyze_market()
            time.sleep(60)
        time.sleep(1)

def run_web(): app.run(host='0.0.0.0', port=8080)
Thread(target=run_web).start()
main_loop()
