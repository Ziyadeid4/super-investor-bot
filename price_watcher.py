import requests
import time
from datetime import datetime
import pandas as pd
import ta

bot_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"

twelve_api_key = "b11e3ef5e7ae49e5a3573430f1eb8958"

eth_symbol = "ETH/USD"
gold_symbol = "XAU/USD"

last_price_eth = None
last_price_gold = None


def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, data=payload)
        print(f"📤 Telegram sent: {r.status_code}")
    except Exception as e:
        print("❌ Telegram error:", e)


def fetch_price_and_indicators(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey={twelve_api_key}&outputsize=30"
        response = requests.get(url).json()
        if "values" not in response:
            raise ValueError("No 'values' in response")
        df = pd.DataFrame(response["values"])
        df = df.iloc[::-1].copy()
        df["close"] = df["close"].astype(float)
        df.set_index("datetime", inplace=True)

        rsi = ta.momentum.RSIIndicator(close=df["close"]).rsi()
        macd = ta.trend.MACD(close=df["close"]).macd_diff()

        current_price = df["close"].iloc[-1]
        latest_rsi = rsi.iloc[-1]
        latest_macd = macd.iloc[-1]

        return current_price, latest_rsi, latest_macd
    except Exception as e:
        print(f"❌ Error fetching {symbol}:", e)
        return None, None, None


send_to_telegram("✅ بدأ التتبع: ETH ⬅️ 1% | GOLD ⬅️ $5")

while True:
    # ETH check
    eth_price, eth_rsi, eth_macd = fetch_price_and_indicators(eth_symbol)
    if eth_price:
        if last_price_eth is None:
            last_price_eth = eth_price
            send_to_telegram(f"📡 ETH: ${eth_price:.2f}\nRSI: {eth_rsi:.2f} | MACD: {eth_macd:.2f}")
        else:
            diff_eth = abs(eth_price - last_price_eth) / last_price_eth * 100
            if diff_eth >= 1:
                emoji = "📈" if eth_price > last_price_eth else "📉"
                send_to_telegram(f"{emoji} ETH ${eth_price:.2f} | نسبة التغير: {diff_eth:.2f}%\nRSI: {eth_rsi:.2f} | MACD: {eth_macd:.2f}")
                last_price_eth = eth_price
            else:
                last_price_eth = eth_price

    # GOLD check
    gold_price, gold_rsi, gold_macd = fetch_price_and_indicators(gold_symbol)
    if gold_price:
        if last_price_gold is None:
            last_price_gold = gold_price
            send_to_telegram(f"📡 GOLD: ${gold_price:.2f}\nRSI: {gold_rsi:.2f} | MACD: {gold_macd:.2f}")
        else:
            diff_gold = abs(gold_price - last_price_gold)
            if diff_gold >= 5:
                emoji = "📈" if gold_price > last_price_gold else "📉"
                send_to_telegram(f"{emoji} GOLD: ${gold_price:.2f} | فرق: {diff_gold:.2f} USD\nRSI: {gold_rsi:.2f} | MACD: {gold_macd:.2f}")
                last_price_gold = gold_price
            else:
                last_price_gold = gold_price

    time.sleep(60)
