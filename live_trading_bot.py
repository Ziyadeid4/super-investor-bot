import ccxt
import pandas as pd
import time
import requests
import joblib
from datetime import datetime
import csv
import os

# تحميل النموذج المدرب
model = joblib.load("model.pkl")

# إعداد Binance
exchange = ccxt.binance()
symbol = "BTC/USDT"
timeframe = "1m"

# بيانات تليجرام (غيّرها حسب بوتك)
telegram_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except:
        print("❌ فشل إرسال رسالة تليجرام")

while True:
    try:
        # جلب بيانات آخر 100 دقيقة
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

        # حساب RSI
        df["rsi"] = df["close"].rolling(window=14).apply(
            lambda x: 100 - (100 / (1 + (x.diff().clip(lower=0).mean() / (-x.diff().clip(upper=0).mean()))))
        )

        # حساب MACD
        df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
        df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = df["ema12"] - df["ema26"]
        df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        df = df.dropna()
        latest = df.iloc[-1]
        X_input = latest[["rsi", "macd", "signal"]].values.reshape(1, -1)

        # التنبؤ بالقرار
        prediction = model.predict(X_input)[0]

        # حفظ القرار في CSV
        file_exists = os.path.isfile("bot_decisions.csv")
        with open("bot_decisions.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["timestamp", "price", "rsi", "macd", "signal", "decision"])
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                round(latest["close"], 2),
                round(latest["rsi"], 2),
                round(latest["macd"], 4),
                round(latest["signal"], 4),
                prediction
            ])
        print("✅ تم حفظ القرار في CSV")

        # إرسال الرسالة لتليجرام
        message = f"""🤖 بوت المستثمر الخارق:
🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💰 السعر: {latest['close']:.2f} USDT
📊 القرار: {prediction}"""
        print(message)
        send_telegram_message(message)

    except Exception as e:
        print("❌ خطأ:", e)
        send_telegram_message(f"🚨 حصل خطأ في البوت:\n{e}")

    # الانتظار دقيقة
    time.sleep(60)
