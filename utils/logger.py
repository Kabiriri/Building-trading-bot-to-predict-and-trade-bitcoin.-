# utils/logger.py
"""
This module handles structured logging of all trading activity.
It appends trade events (executions, failures, exits) to a centralized JSON file (trade_log.json)
located in the logs/ directory. Each log entry is a dictionary that includes:
Trade status (e.g., executed, failed, skipped)
Timestamps for entries and exits
Trade details (e.g., symbol, direction, confidence, SL/TP, PnL)
Optional reason for failures or exits (e.g., "Invalid stops", "sl hit")
"""
import os
import json
from datetime import datetime

# === Path Configuration ===
LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "trade_log.json")
os.makedirs(LOG_FOLDER, exist_ok=True)


# === Create a new log entry (called by trader.py) ===
def create_trade_entry(entry: dict):
    """
    Appends a new trade entry to the trade log.
    """
    entry["log_type"] = "entry"
    _append_to_log(entry)


# === Update an existing trade entry with exit info (called by live_monitor.py) ===
def update_trade_exit(ticket: int, exit_data: dict):
    """
    Updates an existing trade entry with exit info based on ticket number.
    """
    log = _load_log()
    updated = False

    for entry in log:
        if entry.get("ticket") == ticket and "exit_time" not in entry:
            entry.update({
                "exit_time": exit_data.get("exit_time", str(datetime.utcnow())),
                "exit_price": exit_data["exit_price"],
                "exit_reason": exit_data["exit_reason"],
                "pnl_usd": exit_data["pnl_usd"],
                "tp1_hit": exit_data.get("tp1_hit", False),
                "tp2_hit": exit_data.get("tp2_hit", False),
                "sl_hit": exit_data.get("sl_hit", False),
                "log_type": "closed"
            })
            updated = True
            break

    if updated:
        with open(LOG_FILE, "w") as f:
            json.dump(log, f, indent=4)
        print(f" Trade ticket {ticket} updated in log.")
    else:
        print(f" Trade ticket {ticket} not found or already closed.")


# === Internal: Load and Append Helpers ===
def _load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def _append_to_log(entry: dict):
    log = _load_log()
    log.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)
