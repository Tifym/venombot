from fastapi import APIRouter
from app.config import PAIRS
from app.database import get_connection
from app.execution import ExecutionManager

router = APIRouter()
execution = ExecutionManager()

@router.get("/health")
async def health(): return {"status": "ok"}

@router.get("/klines")
async def get_klines(pair: str, timeframe: str, limit: int = 100):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM klines WHERE pair = %s AND timeframe = %s ORDER BY time DESC LIMIT %s", (pair, timeframe, limit))
        cols = [desc[0] for desc in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close()
    return rows

@router.get("/signals")
async def get_signals(status: str = 'pending'):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM signals WHERE status = %s ORDER BY fired_at DESC", (status,))
        cols = [desc[0] for desc in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close(); return rows

@router.post("/signals/{signal_id}/approve")
async def approve_signal(signal_id: int):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM signals WHERE signal_id = %s", (signal_id,))
        col_names = [d[0] for d in cur.description]; row = cur.fetchone()
        if not row: return {"error": "Signal not found"}
        signal = dict(zip(col_names, row))
    conn.close()
    if signal['status'] != 'pending': return {"error": "Already processed"}
    s = await execution.execute_signal(signal)
    return {"status": "success" if s else "failed"}

@router.get("/positions")
async def get_positions():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM positions WHERE status = 'open' ORDER BY opened_at DESC")
        cols = [d[0] for d in cur.description]; rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close(); return rows
