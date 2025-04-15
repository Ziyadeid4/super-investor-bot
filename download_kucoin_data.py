import time
import pandas as pd
from kucoin.client import Market
from datetime import datetime, timedelta

client = Market()

def fetch_klines(symbol, interval, start_date, end_date):
    all_data = []
    current = start_date
    print(f"📦 جاري تحميل {symbol} ...")

    while current < end_date:
        next_time = current + timedelta(days=7)
        start_at = int(current.timestamp())
        end_at = int(next_time.timestamp())

        try:
            data = client.get_kline(
                symbol=symbol,
                kline_type=interval,
                startAt=start_at,
                endAt=end_at
            )
            if data:
                all_data += data
        except Exception as e:
            print(f"❌ خطأ في {symbol}: {e}")
        current = next_time
        time.sleep(0.5)

    if not all_data:
        print(f"⚠️ لا توجد بيانات لـ {symbol}")
        return

    df = pd.DataFrame(all_data, columns=[
        "timestamp", "open", "close", "high", "low", "volume", "turnover"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.sort_values("timestamp")
    df.to_csv(f"{symbol.replace('-', '_')}.csv", index=False)
    print(f"✅ تم حفظ البيانات في {symbol.replace('-', '_')}.csv")

# العملات المطلوبة
symbols = ["BTC-USDT", "ETH-USDT", "XRP-USDT", "SOL-USDT", "DOGE-USDT", "ADA-USDT", "SHIB-USDT", "BNB-USDT", "1000SATS-USDT"]

# تحميل البيانات
start = datetime.utcnow() - timedelta(days=365)
end = datetime.utcnow()
interval = "5min"

for symbol in symbols:
    fetch_klines(symbol, interval, start, end)
