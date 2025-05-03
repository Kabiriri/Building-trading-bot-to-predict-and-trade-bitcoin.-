# live_loop.py

"""
Master loop for BTCUSD algorithmic trading.
- Executes main.py every 15 minutes (prediction + trading)
- Runs live_monitor.py every 30 seconds (manage SL/TP, log updates)
"""

import subprocess
import threading
import time
import traceback

# === Configurations ===
MAIN_INTERVAL_MINUTES = 15
MONITOR_INTERVAL_SECONDS = 30

def run_main_trading():
    while True:
        try:
            print(f" Running main.py at {time.ctime()}...")
            subprocess.run(["python", "main.py"])
        except Exception as e:
            print(" Error in main.py:", e)
            traceback.print_exc()
        time.sleep(MAIN_INTERVAL_MINUTES * 60)

def run_monitoring():
    while True:
        try:
            print(f" Running live_monitor.py at {time.ctime()}...")
            subprocess.run(["python", "live_monitor.py"])
        except Exception as e:
            print(" Error in live_monitor.py:", e)
            traceback.print_exc()
        time.sleep(MONITOR_INTERVAL_SECONDS)

if __name__ == "__main__":
    print(" Starting BTCUSD Live Trading System...")

    monitor_thread = threading.Thread(target=run_monitoring, daemon=True)
    monitor_thread.start()

    run_main_trading()  # Main thread handles trading
