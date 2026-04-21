import redis.asyncio as redis
from app.config import REDIS_URL

class RedisClient:
    def __init__(self): self.client = None
    async def connect(self):
        retries = 10
        while retries > 0:
            try:
                self.client = await redis.from_url(REDIS_URL, decode_responses=True)
                await self.client.ping()
                print("VENOMTRADEBOT: Redis connected successfully.")
                return
            except Exception as e:
                retries -= 1
                print(f"VENOMTRADEBOT: Redis not ready... ({10-retries}/10). Retrying in 5s...")
                import asyncio
                await asyncio.sleep(5)
        raise Exception("Redis connection failed")
    async def disconnect(self):
        if self.client: await self.client.close()
    async def push_liquidation(self, pair, side, price, qty, usd_value):
        await self.client.lpush("liquidations:raw", f"{pair}:{side}:{price}:{qty}:{usd_value}")
    async def get_liquidations(self, count=100):
        pipe = self.client.pipeline()
        pipe.lrange("liquidations:raw", 0, count - 1)
        pipe.ltrim("liquidations:raw", count, -1)
        results = await pipe.execute()
        return results[0]
    async def add_gamma_counter(self, pair, timeframe, side, value):
        await self.client.incrbyfloat(f"gamma:{pair}:{timeframe}:{side}", value)
    async def get_gamma_counters(self, pair, timeframe):
        l = await self.client.get(f"gamma:{pair}:{timeframe}:longs")
        s = await self.client.get(f"gamma:{pair}:{timeframe}:shorts")
        return float(l or 0), float(s or 0)
    async def reset_gamma_counters(self, pair, timeframe):
        await self.client.set(f"gamma:{pair}:{timeframe}:longs", 0)
        await self.client.set(f"gamma:{pair}:{timeframe}:shorts", 0)

redis_client = RedisClient()
