import pandas as pd
import ta
from datetime import datetime

# تحميل ملف البيانات
df = pd.read_csv("BTC_USDT.csv")

# تحويل الوقت لتنسيق مقروء
df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
df["date"] = df["timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S')

# حساب المؤشرات الفنية
df["RSI"] = ta.momentum.RSIIndicator(close=df["close"]).rsi()
df["MACD"] = ta.trend.MACD(close=df["close"]).macd_diff()
df["Stoch_RSI"] = ta.momentum.StochRSIIndicator(close=df["close"]).stochrsi_k()
bb = ta.volatility.BollingerBands(close=df["close"])
df["Bollinger_High"] = bb.bollinger_hband()
df["Bollinger_Low"] = bb.bollinger_lband()

# تحديد الأعمدة المهمة
df_clean = df[["date", "close", "RSI", "MACD", "Stoch_RSI", "Bollinger_High", "Bollinger_Low"]].dropna()

# حفظ البيانات الجديدة
df_clean.to_csv("btc_analysis.csv", index=False)
print("✅ تم تحليل البيانات وحفظها في btc_analysis.csv")
