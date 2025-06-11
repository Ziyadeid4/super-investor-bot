import requests
import time
import pandas as pd
import ta
from datetime import datetime

bot_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"

twelve_data_api_key = "b11e3ef5e7ae49e5a3573430f1eb8958"
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


def fetch_twelvedata(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey={twelve_data_api_key}&outputsize=30"
        response = requests.get(url)
        data = response.json()
        values = data['values']
        df = pd.DataFrame(values)
        df = df.astype(float)
        df = df.sort_values("datetime")

        df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
        df['macd'] = ta.trend.MACD(close=df['close']).macd_diff()

        latest = df.iloc[-1]
        return float(latest['close']), float(latest['rsi']), float(latest['macd'])
    except Exception as e:
        print(f"❌ Error fetching {symbol}:", e)
        return None, None, None


send_to_telegram("✅ بدأ التتبع: ETH ↔️ 1% | GOLD ↔️ $5")

while True:
    # تتبع الإيثيريوم
    price_eth, rsi_eth, macd_eth = fetch_twelvedata(eth_symbol)
    if price_eth:
        if last_price_eth is None:
            last_price_eth = price_eth
            send_to_telegram(f"📡 ETH: ${price_eth:.2f}\nRSI: {rsi_eth:.2f} | MACD: {macd_eth:.2f}")
        else:
            diff_percent = abs((price_eth - last_price_eth) / last_price_eth * 100)
            if diff_percent >= 1:
                direction = "📈" if price_eth > last_price_eth else "📉"
                send_to_telegram(f"{direction} ETH ${price_eth:.2f} | نسبة التغير: {diff_percent:.2f}%\nRSI: {rsi_eth:.2f} | MACD: {macd_eth:.2f}")
                last_price_eth = price_eth

    # تتبع الذهب
    price_gold, rsi_gold, macd_gold = fetch_twelvedata(gold_symbol)
    if price_gold:
        if last_price_gold is None:
            last_price_gold = price_gold
            send_to_telegram(f"📡 GOLD: ${price_gold:.2f}\nRSI: {rsi_gold:.2f} | MACD: {macd_gold:.2f}")
        else:
            diff_usd = abs(price_gold - last_price_gold)
            if diff_usd >= 5:
                direction = "📈" if price_gold > last_price_gold else "📉"
                send_to_telegram(f"{direction} GOLD: ${price_gold:.2f} | فرق: ${diff_usd:.2f}\nRSI: {rsi_gold:.2f} | MACD: {macd_gold:.2f}")
                last_price_gold = price_gold

    time.sleep(10)
