import ccxt
import pandas as pd
import time

exchange = ccxt.kucoin()

symbols = [
    'BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'SOL/USDT',
    'DOGE/USDT', 'ADA/USDT', 'SHIB/USDT', '1000SATS/USDT',
    'BNB/USDT', 'MATIC/USDT'
]

timeframe = '1h'
limit = 500

for symbol in symbols:
    try:
        print(f"جاري تحميل {symbol}...")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        file_name = f"{symbol.replace('/', '_')}.csv"
        df.to_csv(file_name, index=False)
        print(f"✅ تم حفظ {file_name}")
        time.sleep(1)
    except Exception as e:
        print(f"❌ خطأ في {symbol}: {e}")

