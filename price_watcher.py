import requests
import time
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD

# توكن البوت ومعرّف الشات
bot_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"

api_key = "b11e3ef5e7ae49e5a3573430f1eb8958"
interval = "1min"
symbols = {
    "ETH/USD": {"threshold_percent": 1, "last_price": None},
    "XAU/USD": {"threshold_dollar": 5, "last_price": None}
}

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    r = requests.post(url, data=payload)
    print("📤 Telegram sent:", r.status_code)

def fetch_candles(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=100&apikey={api_key}"
    response = requests.get(url).json()
    try:
        df = pd.DataFrame(response["values"])
        df = df.rename(columns={"datetime": "time", "close": "close"})
        df["close"] = df["close"].astype(float)
        df = df.sort_values("time")
        return df
    except Exception as e:
        print(f"❌ Error fetching {symbol}:", e)
        return None

def analyze_and_alert(symbol, config):
    df = fetch_candles(symbol)
    if df is None: return

    current_price = df["close"].iloc[-1]
    rsi = RSIIndicator(close=df["close"]).rsi().iloc[-1]
    macd = MACD(close=df["close"]).macd().iloc[-1]

    # تنبيه الإيثيريوم
    if symbol == "ETH/USD":
        last = config["last_price"]
        if last is None:
            config["last_price"] = current_price
            send_to_telegram(f"📡 ETH: ${current_price:.2f}\nRSI: {rsi:.2f} | MACD: {macd:.2f}")
        else:
            change = abs((current_price - last) / last * 100)
            if change >= config["threshold_percent"]:
                emoji = "📈" if current_price > last else "📉"
                msg = f"{emoji} ETH: ${current_price:.2f} | تغير: {change:.2f}%\nRSI: {rsi:.2f} | MACD: {macd:.2f}"
                send_to_telegram(msg)
                config["last_price"] = current_price

    # تنبيه الذهب
    elif symbol == "XAU/USD":
        last = config["last_price"]
        if last is None:
            config["last_price"] = current_price
            send_to_telegram(f"📡 GOLD: ${current_price:.2f}\nRSI: {rsi:.2f} | MACD: {macd:.2f}")
        else:
            diff = abs(current_price - last)
            if diff >= config["threshold_dollar"]:
                emoji = "📈" if current_price > last else "📉"
                msg = f"{emoji} GOLD: ${current_price:.2f} | فرق: {diff:.2f} USD\nRSI: {rsi:.2f} | MACD: {macd:.2f}"
                send_to_telegram(msg)
                config["last_price"] = current_price

send_to_telegram("✅ بدأ التتبع: ETH ⬅️ 1% | GOLD ⬅️ $5")

while True:
    for symbol, config in symbols.items():
        analyze_and_alert(symbol, config)
    time.sleep(30)  # تابع كل 30 ثانية
