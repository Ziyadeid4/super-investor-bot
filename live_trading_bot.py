import requests
import pandas as pd
import time
import joblib
import json
from datetime import datetime

TELEGRAM_TOKEN = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
CHAT_ID = "390856599"

model = joblib.load("model.pkl")
LAST_DECISIONS_FILE = "last_decisions.json"

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

def get_coin_list():
    # جلب أشهر 10 عملات فقط
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    response = requests.get(url)
    return response.json()

def fetch_market_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30"
    response = requests.get(url)
    data = response.json()
    try:
        prices = [x[1] for x in data["prices"]]
        df = pd.DataFrame(prices, columns=["price"])
        df["rsi"] = compute_rsi(df["price"])
        df["macd"] = compute_macd(df["price"])
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
    return macd - signal_line

def run_bot():
    last_decisions = load_last_decisions()
    coins = get_coin_list()

    for coin in coins:
        coin_id = coin["id"]
        symbol = coin.get("symbol", "").upper()
        price = coin.get("current_price", 0)

        df = fetch_market_data(coin_id)
        if df is None or df.dropna().empty:
            continue

        latest = df.dropna().iloc[-1]
        features = [[latest["price"], latest["rsi"], latest["macd"]]]
        decision = model.predict(features)[0]

        if last_decisions.get(coin_id) != decision:
            emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(decision, "")
            decision_text = {"BUY": "شراء", "SELL": "بيع", "HOLD": "انتظار"}.get(decision, decision)

            message = (
                f"** {symbol} ** {emoji}\n"
                f"القرار: {decision_text}\n"
                f"RSI: {latest['rsi']:.2f} | MACD: {latest['macd']:.5f}\n"
                f"السعر: {price:.2f} USD\n"
                f"الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            send_telegram(message)
            last_decisions[coin_id] = decision

    save_last_decisions(last_decisions)

while True:
    run_bot()
    time.sleep(60)
