import requests
import pandas as pd
import time
import joblib
import json
from datetime import datetime

TELEGRAM_TOKEN = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
CHAT_ID = "390856599"
MODEL_PATH = "model.pkl"
LAST_DECISIONS_FILE = "last_decisions.json"

model = joblib.load(MODEL_PATH)

coin_ids = [
    "bitcoin", "ethereum", "tether", "ripple", "binancecoin",
    "cardano", "solana", "dogecoin", "polkadot", "tron", "1000sats"
]

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
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram error:", e)

def fetch_market_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30"
    try:
        response = requests.get(url)
        data = response.json()
        prices = [x[1] for x in data["prices"]]
        df = pd.DataFrame(prices, columns=["price"])
        df["rsi"] = compute_rsi(df["price"])
        df["macd"], df["signal"] = compute_macd(df["price"])
        return df
    except:
        return None

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

def fetch_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get(coin_id, {}).get("usd", 0)
    except:
        return 0

def emoji_for_decision(decision):
    return {
        "BUY": "🟢",
        "SELL": "🔴",
        "HOLD": "🟡"
    }.get(decision, "❓")

def run_bot():
    last_decisions = load_last_decisions()

    for coin_id in coin_ids:
        df = fetch_market_data(coin_id)
        if df is None or df.dropna().empty:
            continue

        latest = df.dropna().iloc[-1]
        price = fetch_price(coin_id)
        features = [[latest["price"], latest["rsi"], latest["macd"], latest["signal"]]]
        decision = model.predict(features)[0]

        if last_decisions.get(coin_id) != decision:
            emoji = emoji_for_decision(decision)
            name = coin_id.upper()
            message = f"""<b>** {name} ** {emoji}</b>

<b>✅ القرار:</b> {{"BUY":"شراء","SELL":"بيع","HOLD":"انتظار"}.get(decision, decision)}
<b>📊 RSI:</b> {latest['rsi']:.2f} | <b>MACD:</b> {latest['macd']:.5f}
<b>📈 Signal:</b> {latest['signal']:.5f}
<b>💰 السعر:</b> {price:.2f} USD
<b>🕒 الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            send_telegram(message)
            last_decisions[coin_id] = decision

    save_last_decisions(last_decisions)

while True:
    run_bot()
    time.sleep(60)
