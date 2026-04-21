import asyncio, logging, uvicorn
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import HOST, PORT
from app.database import init_db
from app.redis_client import redis_client
from app.api.routes import router
from app.api.websocket import sio
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

# Wrap FastAPI with Socket.IO ASGI app at construction for reliable routing
combined_app = socketio.ASGIApp(sio, other_asgi_app=app)

async def startup():
    print("VENOMTRADEBOT: INITIALIZING...")
    init_db()
    await redis_client.connect()
    
    su = StateUpdater(sio)
    ae = AggregationEngine(su)
    
    asyncio.create_task(WSSpotManager(ae).start())
    asyncio.create_task(WSFuturesManager().start())
    print("VENOMTRADEBOT: ALL SYSTEMS ONLINE.")

@app.on_event("startup")
async def s():
    asyncio.create_task(startup())

@app.on_event("shutdown")
async def h():
    await redis_client.disconnect()

if __name__ == "__main__":
    uvicorn.run(combined_app, host=HOST, port=PORT)
