import requests
import pandas as pd
import ta
import time
from datetime import datetime

bot_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"
api_key = "b11e3ef5e7ae49e5a3573430f1eb8958"

symbols = {
    "ETH/USD": {"last_price": None, "threshold": 1.0, "type": "percent"},
    "XAU/USD": {"last_price": None, "threshold": 5.0, "type": "absolute"},
}


def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, data=payload)
        print("📤 Telegram sent:", r.status_code)
    except Exception as e:
        print("❌ Telegram send error:", e)


def fetch_data(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey={api_key}&outputsize=30"
        resp = requests.get(url).json()
        if "values" not in resp:
            print(f"❌ Error fetching {symbol}: {resp}")
            return None, None, None

        df = pd.DataFrame(resp["values"])
        df = df.astype({"open": float, "high": float, "low": float, "close": float})
        df["RSI"] = ta.momentum.RSIIndicator(close=df["close"]).rsi()
        df["MACD"] = ta.trend.MACD(close=df["close"]).macd_diff()
        latest = df.iloc[0]
        return float(latest["close"]), float(latest["RSI"]), float(latest["MACD"])
    except Exception as e:
        print(f"❌ Exception while fetching {symbol}:", e)
        return None, None, None


send_to_telegram("✅ Bot started: ETH 1% | GOLD $5")

while True:
    for symbol, config in symbols.items():
        price, rsi, macd = fetch_data(symbol)
        if price is None:
            continue

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if config["last_price"] is None:
            config["last_price"] = price
            msg = f"💎 {symbol.split('/')[0]}: ${price:.2f}\n"
            msg += f"🔸 RSI: {rsi:.2f} | MACD: {macd:.2f}\n"
            msg += f"📊 {symbol.split('/')[0]}\n🕒 {now}"
            send_to_telegram(msg)
            continue

        # check if change meets condition
        if config["type"] == "percent":
            change = abs(price - config["last_price"]) / config["last_price"] * 100
            condition_met = change >= config["threshold"]
        else:
            change = abs(price - config["last_price"])
            condition_met = change >= config["threshold"]

        if condition_met:
            emoji = "📈" if price > config["last_price"] else "📉"
            msg = f"{emoji} {symbol.split('/')[0]}: ${price:.2f}\n"
            if config["type"] == "percent":
                msg += f"🔸 RSI: {rsi:.2f} | MACD: {macd:.2f}\n"
                msg += f"📊 {symbol.split('/')[0]}\n🕒 {now}"
            else:
                msg += f"🔸 الفرق: ${change:.2f}\nRSI: {rsi:.2f} | MACD: {macd:.2f}\n"
                msg += f"📊 {symbol.split('/')[0]}\n🕒 {now}"
            send_to_telegram(msg)
            config["last_price"] = price

    time.sleep(3)
