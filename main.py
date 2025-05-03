# main.py

"""
Main trading script for BTCUSD using ensemble model (Transformer + N-BEATS + XGBoost).
Handles:
- Live OHLCV data retrieval from MT5
- Feature engineering
- Ensemble prediction
- Trading logic via smart_trade
"""

import warnings
warnings.filterwarnings("ignore")

import MetaTrader5 as mt5
import numpy as np
from utils.datafeed import get_merged_ohlcv
from utils.feature_engineer import engineer_features
from utils.news import get_upcoming_news
from utils.newpredict import predict_with_ensemble
from utils.trader import smart_trade

# === Configuration ===
BAR_COUNT = 200
SYMBOL = "BTCUSD"

def get_account_balance():
    info = mt5.account_info()
    if info is None:
        raise RuntimeError(" Could not retrieve account info. Is MT5 running and logged in?")
    return info.balance

def main():
    print("Starting BTCUSD AI Trading...")

    if not mt5.initialize():
        raise RuntimeError(" MT5 initialization failed.")
    print(" MT5 connection established.")

    # 1. Fetch upcoming news (optional)
    news_events = get_upcoming_news()

    # 2. Pull and merge price data
    print(" Fetching market data...")
    raw_df = get_merged_ohlcv(SYMBOL, num_candles=BAR_COUNT)

    # 3. Engineer features
    print(" Engineering features...")
    feat_df = engineer_features(raw_df)

    # 4. Make prediction
    print(" Running ensemble prediction...")
    prediction, probs = predict_with_ensemble(SYMBOL)
    confidence = float(np.max(probs['ensemble'])) * 100
    print(f" Prediction Class: {prediction} | Confidence: {confidence:.2f}%")

    # 5. Print account balance
    balance = get_account_balance()
    print(f"💰 Account Balance: ${balance:.2f}")

    # 6. Execute trade
    print(" Executing smart trade...")
    smart_trade(
        pred_class=prediction,
        confidence=confidence,
        symbol_data=raw_df,
        symbol=SYMBOL
    )

    # 7. Shutdown MT5 session
    mt5.shutdown()
    print(" Trade attempt complete. MT5 shutdown successful.")

if __name__ == "__main__":
    main()
