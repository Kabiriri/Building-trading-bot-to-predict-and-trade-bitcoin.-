# utils/trader.py

"""
This script handles live trade execution logic for the BTCUSD AI trading system.
It performs:
1. Market condition checks (e.g. spread, cooldown, opposing trades)
2. SL/TP calculation based on predefined USD values
3. Trade execution via MetaTrader5 using a confirmed filling mode (FOK)
4. Trade logging through the logger module
"""
import MetaTrader5 as mt5
import datetime
from utils import logger

# === Configuration ===
MAX_OPEN_TRADES = 5
SPREAD_THRESHOLD = 70.0  # in USD
COOLDOWN_MINUTES = 15
FIXED_LOT_SIZE = 0.02
SL_USD = 1000
TP_USD = 1000

# === Trade Trackers ===
last_trade_time = {}

# === Market Condition Check ===
def check_market_conditions(symbol):
    info = mt5.symbol_info_tick(symbol)
    if not info:
        return False
    spread = abs(info.ask - info.bid)
    print(f"📊 Spread: {spread:.2f} USD")
    return spread <= SPREAD_THRESHOLD

def check_open_trades(symbol):
    positions = mt5.positions_get(symbol=symbol)
    return len(positions or []) >= MAX_OPEN_TRADES

def cooldown_check(symbol):
    now = datetime.datetime.now()
    if symbol not in last_trade_time:
        return False
    elapsed = (now - last_trade_time[symbol]).total_seconds() / 60
    return elapsed < COOLDOWN_MINUTES

def is_opposing_trade(symbol, new_direction):
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return False
    for p in positions:
        if (p.type == mt5.ORDER_TYPE_BUY and new_direction == "sell") or \
           (p.type == mt5.ORDER_TYPE_SELL and new_direction == "buy"):
            return True
    return False

# === Execute Trade ===
def execute_trade(symbol, direction, lot, sl, tp, price):
    order_type = mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 100,
        "magic": 20250426,
        "comment": "BTC_AI_TRADE",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,  # ✅ Confirmed to work
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return {"status": "failed", "reason": result.comment}

    last_trade_time[symbol] = datetime.datetime.now()
    return {"status": "executed", "ticket": result.order}

# === Main Entry Point ===
def smart_trade(pred_class, confidence, symbol_data, symbol="BTCUSD"):
    now = datetime.datetime.now()

    if pred_class == 0:
        logger.create_trade_entry({
            "status": "skipped", "reason": "Neutral prediction", "timestamp": str(now)
        })
        return

    direction = "buy" if pred_class in [1, 4] else "sell"

    # === Safety Checks
    if check_open_trades(symbol):
        logger.create_trade_entry({
            "status": "skipped", "reason": "Max trades open", "timestamp": str(now)
        })
        return

    if cooldown_check(symbol):
        logger.create_trade_entry({
            "status": "skipped", "reason": "Cooldown in effect", "timestamp": str(now)
        })
        return

    if not check_market_conditions(symbol):
        logger.create_trade_entry({
            "status": "skipped", "reason": "Poor market conditions", "timestamp": str(now)
        })
        return

    if is_opposing_trade(symbol, direction):
        logger.create_trade_entry({
            "status": "skipped", "reason": "Opposing trade exists", "timestamp": str(now)
        })
        return

    # === Live Price Reference
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        logger.create_trade_entry({
            "status": "failed", "reason": "No tick data", "timestamp": str(now)
        })
        return

    entry_price = tick.ask if direction == "buy" else tick.bid
    sl = round(entry_price - SL_USD, 2) if direction == "buy" else round(entry_price + SL_USD, 2)
    tp = round(entry_price + TP_USD, 2) if direction == "buy" else round(entry_price - TP_USD, 2)

    print(f"🧾 Price: {entry_price} | SL: {sl} | TP: {tp}")

    # === Send Order
    result = execute_trade(symbol, direction, FIXED_LOT_SIZE, sl, tp, entry_price)
    result.update({
        "timestamp": str(now),
        "symbol": symbol,
        "direction": direction,
        "confidence": confidence,
        "entry_price": entry_price,
        "sl": sl,
        "tp": tp,
        "lot": FIXED_LOT_SIZE,
        "prediction_class": pred_class,
        "log_type": "entry"
    })

    logger.create_trade_entry(result)
