import asyncio, logging, os
import socketio
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

# CRITICAL: Initialize Database at the module level.
# When running as 'uvicorn app.main:app', the __main__ block is skipped.
# This ensures init_db() runs before the FastAPI app is even created.
print("\n" + "="*40)
print("VENOMTRADEBOT: BOOTING SYSTEM...")
print("="*40)
try:
    init_db()
except Exception as e:
    print(f"FATAL: Database failed to initialize: {e}")
    os._exit(1)

app = FastAPI(title="VENOMTRADEBOT Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/api/health")
async def health():
    return {"status": "ONLINE", "version": "1.0.0"}

app.include_router(router, prefix="/api")
app.mount("/", sio_app)

async def startup_logic():
    try:
        await redis_client.connect()
        print("VENOMTRADEBOT: Starting Confluence Engine...")
        su = StateUpdater(sio)
        ae = AggregationEngine(su)
        print(f"VENOMTRADEBOT: Tracking {len(PAIRS)} Trading Pairs.")
        asyncio.create_task(WSSpotManager(ae).start())
        asyncio.create_task(WSFuturesManager().start())
        print("\n" + "="*40 + "\nVENOMTRADEBOT: ALL SYSTEMS ONLINE!\n" + "="*40 + "\n")
    except Exception as e:
        print(f"CRITICAL ERROR IN BACKGROUND SERVICES: {e}")
        os._exit(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(startup_logic())

@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.disconnect()

if __name__ == "__main__":
    # Local dev run
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
