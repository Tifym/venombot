import asyncio, logging, uvicorn, os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import HOST, PORT, PAIRS
from app.database import init_db
from app.redis_client import redis_client
from app.api.routes import router
from app.api.websocket import sio_app, sio
from app.state_updater import StateUpdater
from app.aggregation_engine import AggregationEngine
from app.ws_spot_manager import WSSpotManager
from app.ws_futures_manager import WSFuturesManager

logging.basicConfig(level=logging.INFO)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.mount("/", sio_app)

async def startup_logic():
    try:
        # 1. Connect to Redis (Async)
        await redis_client.connect()
        
        # 2. Start Confluence Engine
        print("VENOMTRADEBOT: Starting Confluence Engine...")
        su = StateUpdater(sio)
        ae = AggregationEngine(su)
        
        # 3. Start Websocket Workers
        print(f"VENOMTRADEBOT: Connected to {len(PAIRS)} Trading Pairs.")
        asyncio.create_task(WSSpotManager(ae).start())
        asyncio.create_task(WSFuturesManager().start())
        
        print("\n" + "="*40)
        print("VENOMTRADEBOT: ALL SYSTEMS GO!")
        print("="*40 + "\n")
    except Exception as e:
        print(f"CRITICAL ERROR IN BACKGROUND SERVICES: {e}")
        os._exit(1)

@app.on_event("startup")
async def startup_event():
    # Only run pure async tasks here
    asyncio.create_task(startup_logic())

@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.disconnect()

if __name__ == "__main__":
    # CRITICAL: Run synchronous database initialization BEFORE starting Uvicorn.
    # This prevents blocking the async event loop during retries.
    print("\n" + "="*40)
    print("VENOMTRADEBOT: BOOTING SYSTEM...")
    print("="*40)
    
    try:
        init_db()
    except Exception as e:
        print(f"FATAL: Database failed to initialize: {e}")
        os._exit(1)
        
    # Start the server
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
