"""
We will use this folder to test all the utilities one by one
TO make sure they are working as expected before we proceed.

# Testing Feature_engineer.py

import pandas as pd
from utils.datafeed import get_merged_ohlcv
from utils.feature_engineer import engineer_features

# Step 1: Get merged OHLCV data
df_raw = get_merged_ohlcv("BTCUSD", num_candles=500)

# Step 2: Apply feature engineering
df_features = engineer_features(df_raw)

# Step 3: Print available columns
print("Columns produced by feature_engineer.py:")
print(df_features.columns.tolist())
print(f"\nTotal columns: {len(df_features.columns)}")


# Testing predict.py

import pandas as pd
from utils.datafeed import get_merged_ohlcv
from utils.feature_engineer import engineer_features
from utils.predict import predict_ensemble

# Step 1: Fetch and engineer features
df_raw = get_merged_ohlcv("BTCUSD", num_candles=500)
df_features = engineer_features(df_raw)

# Step 2: Get the most recent row (latest data point)
latest = df_features.tail(1)

# Step 3: Run prediction
predicted_class, model_probs = predict_ensemble(latest)

# Step 4: Show results
print(f"Predicted class: {predicted_class}")
print("Model Probabilities Breakdown:")
for model, probs in model_probs.items():
    print(f"{model}: {['{:.3f}'.format(p) for p in probs]}")


# testing newpredict.py


from utils.newpredict import predict_with_ensemble

symbol = "BTCUSD"  # or your broker-specific symbol
prediction, probs = predict_with_ensemble(symbol)

print(f"\n Final Prediction: {prediction}")
print(" Probabilities:")
for model, prob in probs.items():
    print(f"  {model}: {prob}")

# confirming mt5 connection

import MetaTrader5 as mt5

def check_mt5_connection():
    print("🔌 Initializing MT5...")
    if not mt5.initialize():
        print(f"❌ Initialization failed: {mt5.last_error()}")
        return

    print("✅ MT5 Initialized.")

    account_info = mt5.account_info()
    if account_info is None or account_info.login == 0:
        print("❌ Not logged into a trading account.")
    else:
        print("✅ Logged in successfully.")
        print(f"👤 Account Login: {account_info.login}")
        print(f"💰 Balance: {account_info.balance}")
        print(f"💹 Equity: {account_info.equity}")
        print(f"📈 Margin Level: {account_info.margin_level:.2f}%")

    mt5.shutdown()

if __name__ == "__main__":
    check_mt5_connection()

# debugging poor market conditions
import MetaTrader5 as mt5
from time import sleep

# === Configuration ===
SYMBOL = "BTCUSD"  # Adjust if needed
SPREAD_THRESHOLD = 100.0  # Must match what's used in trader.py

def check_market_conditions(symbol):
    info = mt5.symbol_info_tick(symbol)
    if not info:
        print(f"❌ No tick data returned for {symbol}.")
        return False

    spread = abs(info.ask - info.bid)
    print(f"🔍 Ask: {info.ask}")
    print(f"🔍 Bid: {info.bid}")
    print(f"📊 Spread: {spread:.2f} USD")

    if spread > SPREAD_THRESHOLD:
        print(f"❌ Spread exceeds threshold of {SPREAD_THRESHOLD}")
        return False

    print("✅ Market conditions OK.")
    return True

def main():
    print("🔌 Initializing MT5...")
    if not mt5.initialize():
        print("❌ Failed to initialize MT5.")
        return

    print("✅ MT5 Initialized.")
    print(f"🔍 Checking market conditions for {SYMBOL}...\n")
    check_market_conditions(SYMBOL)

    mt5.shutdown()
    print("\n🔌 MT5 shutdown complete.")

if __name__ == "__main__":
    main()

# finding out the filling mode to sort filling mode error
import MetaTrader5 as mt5

symbol = "BTCUSD"

print("🔌 Initializing MT5...")
if not mt5.initialize():
    raise RuntimeError("❌ MT5 initialization failed.")

info = mt5.symbol_info(symbol)
if info is None:
    print(f"❌ Symbol '{symbol}' not found.")
    mt5.shutdown()
    exit()

# Map known filling modes
filling_mode_map = {
    mt5.ORDER_FILLING_FOK: "FOK",
    mt5.ORDER_FILLING_IOC: "IOC",
    mt5.ORDER_FILLING_RETURN: "RETURN"
}

filling_mode = info.filling_mode
filling_mode_name = filling_mode_map.get(filling_mode, f"Unknown ({filling_mode})")

print(f"✅ Default filling mode for {symbol}: {filling_mode_name} (code {filling_mode})")

mt5.shutdown()
print("🔌 MT5 shutdown complete.")
"""

# getting the acceptable filling mode

import MetaTrader5 as mt5

symbol = "BTCUSD"
lot = 0.01

# Initialize
print("🔌 Connecting to MT5...")
if not mt5.initialize():
    raise RuntimeError("❌ Failed to connect to MT5")

info = mt5.symbol_info(symbol)
tick = mt5.symbol_info_tick(symbol)

if not info or not tick:
    print("❌ Failed to get symbol or tick info.")
    mt5.shutdown()
    exit()

price = tick.bid
print(f"💡 Current Bid Price: {price}")

# Try all filling modes
modes = [mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_RETURN]
mode_names = {mt5.ORDER_FILLING_FOK: "FOK", mt5.ORDER_FILLING_IOC: "IOC", mt5.ORDER_FILLING_RETURN: "RETURN"}

for mode in modes:
    print(f"\n🧪 Trying filling mode: {mode_names.get(mode, mode)} ({mode})")

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price + 500,
        "tp": price - 1000,
        "deviation": 100,
        "magic": 123456,
        "comment": "FILLMODE_TEST",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mode,
    }

    result = mt5.order_send(request)
    print(f"➡️ Retcode: {result.retcode}, Comment: {result.comment}")

# Done
mt5.shutdown()

"""
# getting the acceptable stop levels
import MetaTrader5 as mt5

SYMBOL = "BTCUSD"

print("🔌 Connecting to MT5...")
if not mt5.initialize():
    raise RuntimeError("❌ Failed to initialize MT5.")

info = mt5.symbol_info(SYMBOL)
tick = mt5.symbol_info_tick(SYMBOL)

if info is None or tick is None:
    print("❌ Failed to retrieve symbol info or tick data.")
    mt5.shutdown()
    exit()

print(f"\n📊 Diagnostics for {SYMBOL}")
print(f"  ➤ Bid: {tick.bid}")
print(f"  ➤ Ask: {tick.ask}")
print(f"  ➤ Point: {info.point}")
print(f"  ➤ Stops Level (points): {info.stops_level}")
print(f"  ➤ Stops Level (price): {info.stops_level * info.point}")
print(f"  ➤ Freeze Level: {info.freeze_level}")
print(f"  ➤ Trade Contract Size: {info.trade_contract_size}")
print(f"  ➤ Min Volume: {info.volume_min}")
print(f"  ➤ Max Volume: {info.volume_max}")
print(f"  ➤ Volume Step: {info.volume_step}")
print(f"  ➤ Filling Mode: {info.filling_mode}")

mt5.shutdown()
print("\n✅ MT5 shutdown complete.")
"""