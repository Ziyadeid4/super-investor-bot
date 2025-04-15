import pandas as pd
import os
from datetime import datetime

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, short=12, long=26, signal=9):
    short_ema = series.ewm(span=short, adjust=False).mean()
    long_ema = series.ewm(span=long, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def make_decision(rsi, macd, signal):
    if rsi < 30 and macd > signal:
        return "BUY"
    elif rsi > 70 and macd < signal:
        return "SELL"
    else:
        return "HOLD"

def generate_training_data():
    folder_path = "."  # مجلد الملفات
    all_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv") and "_USDT" in filename:
            coin_name = filename.replace(".csv", "")
            try:
                df = pd.read_csv(os.path.join(folder_path, filename))
                df["rsi"] = compute_rsi(df["close"])
                df["macd"], df["signal"] = compute_macd(df["close"])
                df["decision"] = df.apply(lambda row: make_decision(row["rsi"], row["macd"], row["signal"]), axis=1)
                df["coin"] = coin_name
                df["datetime"] = pd.to_datetime(df["timestamp"], unit='ms')
                all_data.append(df[["coin", "datetime", "close", "rsi", "macd", "signal", "decision"]])
            except Exception as e:
                print(f"❌ خطأ في {coin_name}: {e}")

    if all_data:
        result = pd.concat(all_data)
        result.to_csv("training_data.csv", index=False)
        print("✅ تم حفظ بيانات التدريب في training_data.csv")
    else:
        print("❌ لم يتم العثور على بيانات صالحة.")

generate_training_data()

