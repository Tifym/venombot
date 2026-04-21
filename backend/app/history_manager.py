import requests, logging
from datetime import datetime, timezone
from app.config import PAIRS, TIMEFRAMES
from app.database import get_connection

logger = logging.getLogger(__name__)

class HistoryManager:
    def __init__(self, aggregation_engine):
        self.agg_engine = aggregation_engine
        self.base_url = "https://api.binance.com/api/v3/klines"

    def prefill_all(self):
        print("VENOMTRADEBOT: PRE-FILLING HISTORY...")
        for pair in PAIRS:
            self.fetch_history(pair, '1m', 500)
        print("VENOMTRADEBOT: HISTORY READY.")

    def fetch_history(self, pair, timeframe, limit):
        try:
            params = {'symbol': pair, 'interval': timeframe, 'limit': limit}
            r = requests.get(self.base_url, params=params, timeout=10)
            data = r.json()
            
            conn = get_connection()
            with conn.cursor() as cur:
                print(f"  > Loading {len(data)} candles for {pair}...")
                for k in data:
                    c = {
                        'time': datetime.fromtimestamp(k[0]/1000, tz=timezone.utc),
                        'pair': pair, 'timeframe': timeframe,
                        'open': float(k[1]), 'high': float(k[2]), 'low': float(k[3]), 'close': float(k[4]),
                        'volume': float(k[5]), 'quote_volume': float(k[7]), 'trade_count': int(k[8])
                    }
                    cur.execute("""
                        INSERT INTO klines (time, pair, timeframe, open, high, low, close, volume, quote_volume, trade_count) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                        ON CONFLICT (time, pair, timeframe) DO NOTHING
                    """, (c['time'], c['pair'], c['timeframe'], c['open'], c['high'], c['low'], c['close'], c['volume'], c['quote_volume'], c['trade_count']))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to fetch history for {pair}: {e}")
