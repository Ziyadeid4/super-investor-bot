import requests
import pandas as pd
import time
import joblib
import json
from datetime import datetime

# بيانات التليجرام (توكينك و Chat ID)
TELEGRAM_TOKEN = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
CHAT_ID = "390856599"

# تحميل النموذج المدرب
model = joblib.load("model.pkl")

# ملف تخزين آخر القرارات
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
        print("❌ فشل إرسال الرسالة")

def get_coin_list():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    coins = response.json()
    
    # تأكد إن البيانات قائمة
    if isinstance(coins, list):
        return [coin["id"] for coin in coins[:10]]
    else:
        return []


def get_price_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "minute"}
    res = requests.get(url)
    data = res.json()
    prices = data.get("prices", [])
    if len(prices) < 30:
        return None
    df = pd.DataFrame(prices, columns=["timestamp", "close"])
    df["close"] = df["close"]
    return df

def add_indicators(df):
    df["rsi"] = df["close"].rolling(window=14).apply(
        lambda x: 100 - (100 / (1 + (x.diff().clip(lower=0).mean() / (-x.diff().clip(upper=0).mean()))))
    )
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    return df.dropna()

# تشغيل البوت
last_decisions = load_last_decisions()

while True:
    coins = get_coin_list()

    for coin in coins:
        try:
            df = get_price_data(coin)
            if df is None:
                continue
            df = add_indicators(df)
            latest = df.iloc[-1]
            X = latest[["rsi", "macd", "signal"]].values.reshape(1, -1)
            prediction = model.predict(X)[0]

            last_decision = last_decisions.get(coin)
            if prediction != last_decision:
                message = f"""🔔 توصية جديدة للعملة: {coin.upper()}
🕒 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💰 السعر الحالي: {latest['close']:.3f} USD

📊 القرار الجديد: *{prediction.upper()}*

📈 المؤشرات الفنية:
- RSI: {latest['rsi']:.2f}
- MACD: {latest['macd']:.4f}
- Signal Line: {latest['signal']:.4f}
"""
                print(message)
                send_telegram(message)
                last_decisions[coin] = prediction

        except Exception as e:
            print(f"❌ خطأ في {coin}: {e}")

    save_last_decisions(last_decisions)
    time.sleep(60)

