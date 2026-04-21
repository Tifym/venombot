import asyncio
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS klines (
    time TIMESTAMPTZ NOT NULL,
    pair TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    quote_volume DOUBLE PRECISION,
    trade_count INT,
    PRIMARY KEY (time, pair, timeframe)
);

CREATE TABLE IF NOT EXISTS indicators (
    time TIMESTAMPTZ NOT NULL,
    pair TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    rsi DOUBLE PRECISION,
    rsi_prev_peak DOUBLE PRECISION,
    rsi_prev_trough DOUBLE PRECISION,
    macd_line DOUBLE PRECISION,
    macd_signal DOUBLE PRECISION,
    macd_hist DOUBLE PRECISION,
    macd_prev_peak DOUBLE PRECISION,
    macd_prev_trough DOUBLE PRECISION,
    bb_upper DOUBLE PRECISION,
    bb_lower DOUBLE PRECISION,
    bb_middle DOUBLE PRECISION,
    fib_0 DOUBLE PRECISION,
    fib_236 DOUBLE PRECISION,
    fib_382 DOUBLE PRECISION,
    fib_500 DOUBLE PRECISION,
    fib_618 DOUBLE PRECISION,
    fib_786 DOUBLE PRECISION,
    fib_1000 DOUBLE PRECISION,
    swing_high DOUBLE PRECISION,
    swing_low DOUBLE PRECISION,
    atr_14 DOUBLE PRECISION,
    PRIMARY KEY (time, pair, timeframe)
);

CREATE TABLE IF NOT EXISTS signal_states (
    pair TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    alfa_state TEXT,
    alfa_zone_low DOUBLE PRECISION,
    alfa_zone_high DOUBLE PRECISION,
    beta_state TEXT,
    beta_divergence_type TEXT,
    delta_state TEXT,
    gamma_longs_m DOUBLE PRECISION DEFAULT 0,
    gamma_shorts_m DOUBLE PRECISION DEFAULT 0,
    gamma_state TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (pair, timeframe)
);

CREATE TABLE IF NOT EXISTS signals (
    signal_id SERIAL PRIMARY KEY,
    fired_at TIMESTAMPTZ DEFAULT NOW(),
    pair TEXT NOT NULL,
    primary_timeframe TEXT NOT NULL,
    direction TEXT NOT NULL,
    score DOUBLE PRECISION,
    confluence_breakdown JSONB,
    entry_price DOUBLE PRECISION,
    stop_loss DOUBLE PRECISION,
    take_profit DOUBLE PRECISION,
    atr_14 DOUBLE PRECISION,
    status TEXT DEFAULT 'pending',
    human_decision TEXT,
    human_modified_entry DOUBLE PRECISION,
    human_modified_stop DOUBLE PRECISION,
    human_modified_target DOUBLE PRECISION,
    executed_price DOUBLE PRECISION,
    exit_price DOUBLE PRECISION,
    pnl_pct DOUBLE PRECISION,
    mode TEXT DEFAULT 'demo',
    closed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS positions (
    position_id SERIAL PRIMARY KEY,
    signal_id INT REFERENCES signals(signal_id),
    pair TEXT,
    direction TEXT,
    entry_price DOUBLE PRECISION,
    stop_loss DOUBLE PRECISION,
    take_profit DOUBLE PRECISION,
    size_usdt DOUBLE PRECISION,
    status TEXT,
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    pnl_pct DOUBLE PRECISION,
    close_reason TEXT,
    mode TEXT
);

CREATE TABLE IF NOT EXISTS liquidations (
    time TIMESTAMPTZ NOT NULL,
    pair TEXT,
    side TEXT,
    price DOUBLE PRECISION,
    qty DOUBLE PRECISION,
    usd_value DOUBLE PRECISION
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'klines') THEN
        PERFORM create_hypertable('klines', 'time', chunk_time_interval => INTERVAL '1 day');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'indicators') THEN
        PERFORM create_hypertable('indicators', 'time', chunk_time_interval => INTERVAL '1 day');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'liquidations') THEN
        PERFORM create_hypertable('liquidations', 'time', chunk_time_interval => INTERVAL '1 day');
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
CREATE INDEX IF NOT EXISTS idx_liquidations_pair_time ON liquidations(pair, time DESC);
"""

def init_db():
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
            conn.close()
            logger.info("VENOMTRADEBOT: Database initialized successfully.")
            return
        except Exception as e:
            retries -= 1
            logger.warning(f"VENOMTRADEBOT: Database not ready... ({10-retries}/10). Retrying in 5s...")
            import time
            time.sleep(5)
    
    logger.error("VENOMTRADEBOT: Could not connect to database after 10 attempts.")
    raise Exception("Database connection failed")

def get_connection():
    return psycopg2.connect(DATABASE_URL)
