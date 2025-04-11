import requests
import pandas as pd
import time
import joblib
import json
from datetime import datetime

# بيانات التليجرام
TELEGRAM_TOKEN = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
CHAT_ID = "390856599"

# تحميل النموذج
model = joblib.load("model.pkl")

# ملف القرارات السابقة
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
        print("فشل إرسال رسالة تليجرام")

def get_coin_list():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    data = response.json()
    
    if isinstance(data, dict) and "coins" in data:
        coins = data["coins"]  # إذا كان فيه مفتاح "coins" داخل dict
    elif isinstance(data, list):
        coins = data  # إذا كان data عبارة عن list مباشرة
    else:
        coins = []  # حالة الطوارئ

    return [coin["id"] for coin in coins[:10]]  # خذ أول 10 عملات


def get_ohlc(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=hourly"
    res = requests.get(url)
    data = res.json()
    prices = data.get("prices", [])
    if len(prices) < 26:
        return None
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices):
    exp1 = prices.ewm(span=12, adjust=False).mean()
    exp2 = prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def make_decision(rsi, macd, signal):
    if rsi < 30 and macd.iloc[-1] > signal.iloc[-1]:
        return "شراء"
    elif rsi > 70 and macd.iloc[-1] < signal.iloc[-1]:
        return "بيع"
    else:
        return "انتظار"

def run_bot():
    last_decisions = load_last_decisions()
    coin_ids = get_coin_list()

    for coin_id in coin_ids:
        df = get_ohlc(coin_id)
        if df is None:
            continue

        prices = df["price"]
        rsi = calculate_rsi(prices).iloc[-1]
        macd, signal = calculate_macd(prices)
        decision = make_decision(rsi, macd, signal)

        previous = last_decisions.get(coin_id)
        if previous != decision:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = (
                f"العملة: {coin_id}\n"
                f"التاريخ: {now}\n"
                f"السعر: {prices.iloc[-1]:.2f} $\n"
                f"RSI: {rsi:.2f}\n"
                f"MACD: {macd.iloc[-1]:.5f}\n"
                f"Signal: {signal.iloc[-1]:.5f}\n"
                f"القرار: {decision}"
            )
            send_telegram(message)
            last_decisions[coin_id] = decision

    save_last_decisions(last_decisions)

# تشغيل البوت كل دقيقة
while True:
    run_bot()
    time.sleep(60)

