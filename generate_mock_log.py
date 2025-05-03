# generate_mock_log.py

"""
This script generates a realistic mock trading log simulating:
1. Trade entries and exits
2. SL/TP hits
3. Profitable and losing trades
4. Varying confidence and directions

Used to populate mock_logs/mock_trade_log.json for testing the dashboard
without running the full trading system.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Create mock trade log with entries and exits
def generate_mock_log(filename="mock_logs/mock_trade_log.json", num_trades=50):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    entries = []
    current_time = datetime.now() - timedelta(days=num_trades)
    price = 50000.0

    for i in range(num_trades):
        direction = random.choice(["buy", "sell"])
        entry_price = price + random.uniform(-2000, 2000)
        sl = entry_price - 1000 if direction == "buy" else entry_price + 1000
        tp = entry_price + 1000 if direction == "buy" else entry_price - 1000
        pnl = round(random.uniform(-500, 1000), 2)
        status = "executed"
        ticket = 1000000000 + i

        entry = {
            "status": status,
            "reason": "executed",
            "timestamp": str(current_time),
            "symbol": "BTCUSD",
            "direction": direction,
            "confidence": round(random.uniform(30, 90), 2),
            "entry_price": round(entry_price, 2),
            "sl": round(sl, 2),
            "tp": round(tp, 2),
            "lot": 0.02,
            "prediction_class": random.randint(1, 4),
            "ticket": ticket,
            "log_type": "entry"
        }

        exit_entry = {
            "ticket": ticket,
            "exit_time": str(current_time + timedelta(minutes=30)),
            "exit_price": round(entry_price + pnl if direction == "buy" else entry_price - pnl, 2),
            "exit_reason": "tp1 hit" if pnl > 0 else "sl hit",
            "pnl_usd": pnl,
            "tp1_hit": pnl > 0,
            "tp2_hit": False,
            "sl_hit": pnl <= 0,
            "log_type": "closed"
        }

        entries.append(entry)
        entries.append(exit_entry)

        current_time += timedelta(hours=3)
        price += random.uniform(-1000, 1000)

    with open(filename, "w") as f:
        json.dump(entries, f, indent=4)

    return f"{num_trades} mock trades written to {filename}"

generate_mock_log()
