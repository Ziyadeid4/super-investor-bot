import ccxt
import pandas as pd
from datetime import datetime, timedelta

exchange = ccxt.kucoin()

def fetch_kucoin_history(symbol):
    try:
        since = exchange.parse8601((datetime.utcnow() - timedelta(days=30)).isoformat())
        ohlcv = exchange.fetch_ohlcv(f"{symbol}/USDT", timeframe='1h', since=since, limit=500)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "price", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        print(f"❌ خطأ في {symbol}/USDT: {e}")
        return None
