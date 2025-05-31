import requests
import time
from datetime import datetime

bot_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"

symbol = "ETH-USDT"
last_price = None

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Telegram send error:", e)

def fetch_price(symbol):
    try:
        url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}"
        response = requests.get(url).json()
        return float(response['data']['price'])
    except:
        return None

# أول إشعار
send_to_telegram("✅ بدأ تتبع ETH - الإشعار فقط عند تغيّر السعر بنسبة 1٪")

while True:
    price = fetch_price(symbol)
    if price:
        if last_price is None:
            last_price = price
            send_to_telegram(f"📡 ETH الآن: {price:.2f} USDT")
        else:
            diff = abs(price - last_price) / last_price * 100
            if diff >= 1:
                emoji = "📈" if price > last_price else "📉"
                send_to_telegram(f"{emoji} ETH السعر الجديد: {price:.2f} USDT\nنسبة التغير: {diff:.2f}%")
                last_price = price
    time.sleep(5)
