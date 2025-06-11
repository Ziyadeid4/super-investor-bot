import requests
import pandas as pd
import ta
import time

# إعدادات البوت
bot_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"
api_key = "b11e3ef5e7ae49e5a3573430f1eb8958"

# الرموز
eth_symbol = "ETH/USD"
gold_symbol = "XAU/USD"

# تتبع آخر سعر
last_price_eth = None
last_price_gold = None

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, data=payload)
        print("📤 Telegram sent:", r.status_code)
    except Exception as e:
        print("❌ Telegram error:", e)

def fetch_data(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=30&apikey={api_key}"
        response = requests.get(url).json()
        if "values" not in response:
            raise Exception(response.get("message", "No data"))

        df = pd.DataFrame(response["values"])
        df = df.iloc[::-1]  # ترتيب تصاعدي
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
        df["RSI"] = ta.momentum.RSIIndicator(close=df["close"]).rsi()
        df["MACD"] = ta.trend.MACD(close=df["close"]).macd_diff()
        latest = df.iloc[-1]
        return latest["close"], latest["RSI"], latest["MACD"]
    except Exception as e:
        print(f"❌ Error fetching {symbol}:", e)
        return None, None, None

# بدء التتبع
send_to_telegram("✅ تم بدء التتبع - ETH (تغير 1٪) | GOLD (تغير 5$)")

while True:
    # -------- ETH --------
    price_eth, rsi_eth, macd_eth = fetch_data(eth_symbol)
    if price_eth is not None:
        if last_price_eth is None:
            last_price_eth = price_eth
            send_to_telegram(f"📡 ETH: ${price_eth:.2f}\nRSI: {rsi_eth:.2f} | MACD: {macd_eth:.2f}")
        else:
            change_eth = abs(price_eth - last_price_eth) / last_price_eth * 100
            if change_eth >= 1:
                emoji = "📈" if price_eth > last_price_eth else "📉"
                send_to_telegram(f"{emoji} ETH السعر الجديد: ${price_eth:.2f}\nتغير: %{change_eth:.2f}\nRSI: {rsi_eth:.2f} | MACD: {macd_eth:.2f}")
                last_price_eth = price_eth

    # -------- GOLD --------
    price_gold, rsi_gold, macd_gold = fetch_data(gold_symbol)
    if price_gold is not None:
        if last_price_gold is None:
            last_price_gold = price_gold
            send_to_telegram(f"📡 GOLD: ${price_gold:.2f}\nRSI: {rsi_gold:.2f} | MACD: {macd_gold:.2f}")
        else:
            change_gold = abs(price_gold - last_price_gold)
            if change_gold >= 5:
                emoji = "📈" if price_gold > last_price_gold else "📉"
                send_to_telegram(f"{emoji} GOLD السعر الجديد: ${price_gold:.2f}\nفرق: ${change_gold:.2f}\nRSI: {rsi_gold:.2f} | MACD: {macd_gold:.2f}")
                last_price_gold = price_gold

    time.sleep(10)
