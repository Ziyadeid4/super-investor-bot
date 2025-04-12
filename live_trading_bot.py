import requests
import pandas as pd
import time
import joblib
import json
from datetime import datetime
from fetch_kucoin_data import fetch_kucoin_history  # لازم ملف kucoin جاهز

TELEGRAM_TOKEN = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
CHAT_ID = "390856599"

model = joblib.load("model.pkl")
LAST_DECISIONS_FILE = "last_decisions.json"

TOP_COINS = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "TRX", "1000SATS"]

def load_last_decisions():
    try:
        with open(LAST_DECISIONS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_last_decisions(data):
    with open(LAST_DECISIONS_FILE, "w") as f:
        json.dump(data, f)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        print("فشل في إرسال الرسالة")

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, short=12, long=26, signal=9):
    short_ema = series.ewm(span=short, adjust=False).mean()
    long_ema = series.ewm(span=long, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def run_bot():
    last_decisions = load_last_decisions()

    for symbol in TOP_COINS:
        df = fetch_kucoin_history(symbol)
        if df is None or df.empty or len(df) < 35:
            continue

        df["rsi"] = compute_rsi(df["price"])
        df["macd"], df["signal"] = compute_macd(df["price"])
        df = df.dropna()
        if df.empty:
            continue

        latest = df.iloc[-1]
        features = [[latest["price"], latest["rsi"], latest["macd"]]]
        decision = model.predict(features)[0]

        if last_decisions.get(symbol) != decision:
            emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(decision, "")
            decision_text = {"BUY": "شراء", "SELL": "بيع", "HOLD": "انتظار"}.get(decision, decision)
            message = (
                f"🤖 إشعار من البوت المستثمر الخارق:\n"
                f"💎 **{symbol}** {emoji}\n"
                f"📈 RSI: {latest['rsi']:.2f} | MACD: {latest['macd']:.5f}\n"
                f"💰 السعر: {latest['price']:.2f} USD\n"
                f"🕒 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"✅ القرار: {decision_text}"
            )
            send_telegram(message)
            last_decisions[symbol] = decision

    save_last_decisions(last_decisions)

while True:
    run_bot()
    time.sleep(60)

