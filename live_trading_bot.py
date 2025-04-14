import pandas as pd
import requests
import time
import json
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD
import joblib

# إعدادات التيليجرام
TELEGRAM_TOKEN = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
CHAT_ID = "390856599"

# العملات التي سيتم تحليلها
symbols = ["BTC-USDT", "ETH-USDT", "XRP-USDT", "SOL-USDT", "DOGE-USDT",
           "ADA-USDT", "SHIB-USDT", "BNB-USDT"]

# تحميل النموذج المدرب
model = joblib.load("model.pkl")

# لتجنب التكرار
last_decisions = {}


def fetch_kucoin_price(symbol):
    url = f"https://api.kucoin.com/api/v1/market/candles?type=5min&symbol={symbol}&limit=100"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data, columns=["timestamp", "open", "close", "high", "low", "volume", "turnover"])
        df = df.iloc[::-1]
        df[["open", "close", "high", "low", "volume"]] = df[["open", "close", "high", "low", "volume"]].astype(float)
        df["close"] = pd.to_numeric(df["close"])
        df["RSI"] = RSIIndicator(close=df["close"]).rsi()
        df["MACD"] = MACD(close=df["close"]).macd_diff()
        df.dropna(inplace=True)
        return df
    else:
        print(f"❌ فشل في جلب بيانات {symbol}")
        return None


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("فشل في إرسال الرسالة:", e)


while True:
    for symbol in symbols:
        df = fetch_kucoin_price(symbol)
        if df is None or df.empty:
            continue

        latest = df.iloc[-1]
        features = latest[["close", "RSI", "MACD"]].values.reshape(1, -1)
        decision = model.predict(features)[0]

        # اسم مختصر للعملة
        name = symbol.replace("-USDT", "")

        # تجنب التكرار
        if symbol in last_decisions and last_decisions[symbol] == decision:
            continue
        last_decisions[symbol] = decision

        # تنسيق الوقت
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # إنشاء الرسالة
        emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⏳"}
        message = f"<b>🚀 توصية جديدة للعملة: {name}</b>\n"
        message += f"🕒 <b>الوقت:</b> {now}\n"
        message += f"💵 <b>السعر:</b> {latest['close']:.2f} USDT\n"
        message += f"📊 <b>RSI:</b> {latest['RSI']:.2f}\n"
        message += f"📈 <b>MACD:</b> {latest['MACD']:.2f}\n"
        message += f"✅ <b>القرار:</b> {decision} {emoji[decision]}"

        send_telegram(message)
        print(f"✅ أُرسلت توصية {symbol}: {decision}")

    time.sleep(60)  # كل دقيقة
