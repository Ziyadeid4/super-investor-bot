import requests
import time
from datetime import datetime
import ta
import pandas as pd

bot_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"

gold_symbol = "XAU/USD"
eth_symbol = "ETH/USD"

gold_last_price = None
eth_last_price = None

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, data=payload)
        print("📤 Telegram sent:", r.status_code)
    except Exception as e:
        print("❌ Telegram send error:", e)

def fetch_price(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey=b11e3ef5e7ae49e5a3573430f1eb8958"
        response = requests.get(url).json()
        values = response['values']
        df = pd.DataFrame(values)
        df = df.iloc[::-1]  # ترتيب تصاعدي
        df['close'] = df['close'].astype(float)
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
        df['macd'] = ta.trend.MACD(df['close']).macd_diff()
        latest = df.iloc[-1]
        return float(latest['close']), round(latest['rsi'], 2), round(latest['macd'], 2)
    except Exception as e:
        print(f"❌ Error fetching {symbol}:", e)
        return None, None, None

send_to_telegram("✅ بدأ التتبع: ETH ⬅️ 1٪ | GOLD ⬅️ $5 ✅")

while True:
    # ETH
    eth_price, eth_rsi, eth_macd = fetch_price(eth_symbol)
    if eth_price:
        if eth_last_price is None:
            eth_last_price = eth_price
            send_to_telegram(f"📡 ETH: ${eth_price:.2f}\nRSI: {eth_rsi} | MACD: {eth_macd}")
        else:
            diff_percent = abs(eth_price - eth_last_price) / eth_last_price * 100
            if diff_percent >= 1:
                emoji = "📈" if eth_price > eth_last_price else "📉"
                send_to_telegram(f"{emoji} ETH ${eth_price:.2f} | نسبة التغير: {diff_percent:.2f}%\nRSI: {eth_rsi} | MACD: {eth_macd}")
                eth_last_price = eth_price

    # GOLD
    gold_price, gold_rsi, gold_macd = fetch_price(gold_symbol)
    if gold_price:
        if gold_last_price is None:
            gold_last_price = gold_price
            send_to_telegram(f"📡 GOLD: ${gold_price:.2f}\nRSI: {gold_rsi} | MACD: {gold_macd}")
        else:
            diff_usd = abs(gold_price - gold_last_price)
            if diff_usd >= 5:
                emoji = "📈" if gold_price > gold_last_price else "📉"
                send_to_telegram(f"{emoji} GOLD: ${gold_price:.2f} | فرق: {diff_usd:.2f} USD\nRSI: {gold_rsi} | MACD: {gold_macd}")
                gold_last_price = gold_price

    time.sleep(10)
