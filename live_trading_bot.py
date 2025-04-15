# ✅ live_trading_bot.py - نسخة محدثة بحساب الربح ومنع التكرار

import requests
import pandas as pd
import ta
import time
import joblib
from datetime import datetime
import csv

model = joblib.load("xgb_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")

symbols = [
    "BTC-USDT", "ETH-USDT", "BNB-USDT", "SOL-USDT", "XRP-USDT", "ADA-USDT",
    "AVAX-USDT", "DOT-USDT", "LTC-USDT", "DOGE-USDT", "SHIB-USDT", "PEPE-USDT",
    "FLOKI-USDT", "BONK-USDT", "WIF-USDT", "SUI-USDT", "INJ-USDT",
    "APT-USDT", "OP-USDT", "ARB-USDT"
]

positions = {}  # لمتابعة الصفقات المفتوحة
last_decisions = {}  # لحفظ آخر توصية تم إرسالها
log_file = "trade_log.csv"

bot_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, data=payload)
        print(f"📤 تم الإرسال إلى تليجرام: {r.status_code}")
    except Exception as e:
        print("❌ فشل إرسال تليجرام:", e)

def fetch_kucoin_data(symbol, limit=100):
    try:
        url = f"https://api.kucoin.com/api/v1/market/candles?type=1min&symbol={symbol}"
        response = requests.get(url).json()
        raw_data = response['data'][:limit]
        raw_data.reverse()
        df = pd.DataFrame(raw_data, columns=[
            "timestamp", "open", "close", "high", "low", "volume", "turnover"
        ])
        df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
        latest_price = float(df.iloc[-1]["close"])
        return df, latest_price
    except Exception as e:
        print(f"❌ خطأ في {symbol}: {e}")
        return None, None

send_to_telegram("✅ تم تشغيل البوت - التحليل مع تتبع الصفقات والتغيير فقط 🔁")

while True:
    for symbol in symbols:
        print(f"🔄 جاري تحليل: {symbol}")
        df, price = fetch_kucoin_data(symbol)
        if df is None or len(df) < 30:
            print(f"⚠️ بيانات غير كافية لـ {symbol}")
            continue

        df["rsi"] = ta.momentum.RSIIndicator(close=df["close"]).rsi()
        df["macd"] = ta.trend.MACD(close=df["close"]).macd_diff()
        df = df.dropna()

        if df.empty:
            print(f"⚠️ فشل حساب المؤشرات لـ {symbol}")
            continue

        latest = df.iloc[-1]
        features = [[latest["close"], latest["rsi"], latest["macd"]]]
        prediction = model.predict(features)
        decision = label_encoder.inverse_transform(prediction)[0]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symbol_clean = symbol.replace("-USDT", "")

        # متابعة تغير القرار فقط
        if symbol_clean in last_decisions and last_decisions[symbol_clean] == decision:
            print(f"⏩ {symbol} لم يتغير القرار ({decision}) - تجاهل الإشعار")
            continue

        last_decisions[symbol_clean] = decision

        # التبديل بين BUY/SELL لحساب الربح
        if symbol_clean in positions:
            prev = positions[symbol_clean]
            if decision != prev["type"] and decision in ["BUY", "SELL"]:
                entry = prev["price"]
                exit = price
                direction = prev["type"]
                profit = ((exit - entry) / entry * 100) if direction == "BUY" else ((entry - exit) / entry * 100)

                trade_message = f"""
🔁 {symbol_clean} | {direction} → {decision}
💸 السعر من: {round(entry, 4)} → {round(exit, 4)}
📈 نسبة الربح: {round(profit, 2)}%
⏰ الدخول: {prev['time']} | الخروج: {now}
"""
                send_to_telegram(trade_message)

                with open(log_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([symbol_clean, direction, prev["time"], entry, decision, now, exit, round(profit, 3)])

                del positions[symbol_clean]

        if decision in ["BUY", "SELL"]:
            positions[symbol_clean] = {"type": decision, "price": price, "time": now}

        message = f"""
📊 {symbol}
💰 السعر الحالي: {round(price, 4)}
📈 RSI: {round(latest['rsi'],2)}
📉 MACD: {round(latest['macd'],4)}
📥 التوصية: {decision}
⏰ التوقيت: {now}
"""
        send_to_telegram(message)
        print(message)

    print("⏱️ انتظار 60 ثانية قبل التكرار...\n")
    time.sleep(60)
