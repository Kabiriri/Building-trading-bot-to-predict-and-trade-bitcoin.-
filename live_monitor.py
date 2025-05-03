"""
Continuously monitors open BTCUSD trades to dynamically adjust
stop-loss levels (e.g., move SL to breakeven after TP1 hit) and detect trade exits.
Upon closure, it logs detailed exit information —
including exit price, time, reason, PnL, and hit flags — by updating the centralized
trade log. This module ensures accurate,
real-time tracking of trade lifecycle for analytics and dashboard reporting.
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
from utils.logger import update_trade_exit

# === Parameters ===
SYMBOL = "BTCUSD"
TP1_PROFIT = 1000       # USD
TRAILING_DISTANCE = 200  # USD
CHECK_INTERVAL = 30     # seconds

def fetch_open_positions():
    return mt5.positions_get(symbol=SYMBOL)

def get_current_price(direction):
    tick = mt5.symbol_info_tick(SYMBOL)
    return tick.bid if direction == "sell" else tick.ask

def monitor_trades():
    print(" Starting live trade monitor...")
    while True:
        positions = fetch_open_positions()
        if positions:
            for p in positions:
                ticket = p.ticket
                direction = "buy" if p.type == mt5.ORDER_TYPE_BUY else "sell"
                entry_price = p.price_open
                sl = p.sl
                volume = p.volume
                current_price = get_current_price(direction)

                # === Check TP1 hit ===
                if direction == "buy":
                    tp1_hit = current_price >= entry_price + TP1_PROFIT
                    breakeven = entry_price + 30  # small buffer
                    new_sl = max(sl, current_price - TRAILING_DISTANCE)
                else:
                    tp1_hit = current_price <= entry_price - TP1_PROFIT
                    breakeven = entry_price - 30
                    new_sl = min(sl, current_price + TRAILING_DISTANCE)

                # === If TP1 hit, move SL to breakeven ===
                if tp1_hit:
                    modify_request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": ticket,
                        "sl": round(breakeven, 2),
                        "tp": p.tp,
                    }
                    result = mt5.order_send(modify_request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f" SL moved to breakeven for ticket {ticket}")
                    else:
                        print(f" Failed to move SL for ticket {ticket}: {result.comment}")

                # === Check for exit ===
                pnl = p.profit
                if pnl <= -500 or pnl >= TP1_PROFIT:
                    update_trade_exit(ticket, {
                        "exit_time": str(datetime.utcnow()),
                        "exit_price": current_price,
                        "exit_reason": "tp1 hit" if pnl >= TP1_PROFIT else "sl hit",
                        "pnl_usd": pnl,
                        "tp1_hit": pnl >= TP1_PROFIT,
                        "tp2_hit": False,
                        "sl_hit": pnl <= -500
                    })
        else:
            print(" No open trades.")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if not mt5.initialize():
        raise RuntimeError(" Failed to initialize MT5.")
    try:
        monitor_trades()
    finally:
        mt5.shutdown()
