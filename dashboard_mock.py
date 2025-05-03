# dashboard_mock.py
"""
A development version of the main dashboard.
It reads from a mock trade log (mock_logs/mock_trade_log.json)
to simulate how the live dashboard will behave once real trades accumulate.
Functionality is identical to dashboard.py — only the data source is different.
"""

from datetime import datetime, timedelta
import json
import pandas as pd
import random
import os

# === Create mock_logs directory ===
os.makedirs("mock_logs", exist_ok=True)

# === Parameters ===
NUM_TRADES = 50
base_time = datetime(2025, 3, 14, 9, 0, 0)
symbols = ["BTCUSD"]
directions = ["buy", "sell"]

entries = []
closes = []

for i in range(NUM_TRADES):
    symbol = random.choice(symbols)
    direction = random.choice(directions)
    entry_price = round(random.uniform(45000, 60000), 2)
    sl = entry_price - 1000 if direction == "buy" else entry_price + 1000
    tp = entry_price + 1000 if direction == "buy" else entry_price - 1000
    confidence = round(random.uniform(30, 90), 2)
    ticket = 1000000000 + i
    timestamp = base_time + timedelta(hours=i * 3)

    entry = {
        "status": "executed",
        "reason": "executed",
        "timestamp": timestamp.isoformat(),
        "symbol": symbol,
        "direction": direction,
        "confidence": confidence,
        "entry_price": entry_price,
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "lot": 0.02,
        "prediction_class": random.randint(1, 4),
        "ticket": ticket,
        "log_type": "entry"
    }
    entries.append(entry)

    # Randomize if trade hit TP or SL
    exit_time = timestamp + timedelta(minutes=30)
    tp_hit = random.choice([True, False])
    sl_hit = not tp_hit

    exit_price = tp if tp_hit else sl
    pnl_usd = round((exit_price - entry_price) * (1 if direction == "buy" else -1), 2)

    close = {
        "ticket": ticket,
        "exit_time": exit_time.isoformat(),
        "exit_price": round(exit_price, 2),
        "exit_reason": "tp1 hit" if tp_hit else "sl hit",
        "pnl_usd": pnl_usd,
        "tp1_hit": tp_hit,
        "tp2_hit": False,
        "sl_hit": sl_hit,
        "log_type": "closed"
    }
    closes.append(close)

# === Write to JSON ===
mock_data = entries + closes
with open("mock_logs/mock_trade_log.json", "w") as f:
    json.dump(mock_data, f, indent=4)

# Return sample for inspection
#df_sample = pd.DataFrame(mock_data).head()
#import ace_tools as tools; tools.display_dataframe_to_user(name="Sample Mock Trade Log", dataframe=df_sample)
