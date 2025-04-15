from kucoin.client import Client
import pandas as pd
import time
from datetime import datetime, timedelta

client = Client(api_key="", api_secret="", passphrase="")

def fetch_klines(symbol, start, end, interval="1min"):
    try:
        data = client.get_kline_data(symbol, interval, start, end)
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "close", "high", "low", "volume", "turnover"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
        return df
    except Exception as e:
        print(f"❌ خطأ أثناء جلب البيانات: {e}")
        return pd.DataFrame()

def fetch_full_history(symbol, days=180, chunk_size=20):
    all_data = pd.DataFrame()
    end_time = datetime.utcnow()

    for i in range(0, days, chunk_size):
        start = end_time - timedelta(days=i + chunk_size)
        end = end_time - timedelta(days=i)
        print(f"📦 تحميل البيانات من {start.date()} إلى {end.date()}...")

        df = fetch_klines(symbol, int(start.timestamp()), int(end.timestamp()))
        all_data = pd.concat([df, all_data])
        time.sleep(1)  # تأخير بسيط لعدم الحظر من API

    all_data.to_csv(f"{symbol.replace('/', '_')}.csv", index=False)
    print(f"✅ تم حفظ البيانات في {symbol.replace('/', '_')}.csv")

# مثال:
fetch_full_history("BTC/USDT", days=180)
