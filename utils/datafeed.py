"""
Pull fresh data (e.g., 500 candles) from MT5 for timeframes: M15, H1, H4, D1
Then merge them properly using backward timestamp alignment,
 to produce a final DataFrame suitable for feature engineering.
This final df will merge exactly what we had when we merged
 the dataset earlier before training.
"""
# utils/datafeed.py

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

#  Mapping string to MT5 timeframes
TIMEFRAME_MAP = {
    "M15": mt5.TIMEFRAME_M15,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

#  Core MT5 Lifecycle
def initialize_mt5():
    if not mt5.initialize():
        raise ConnectionError(f"MT5 initialization failed: {mt5.last_error()}")

#  Fetch OHLCV from MT5
def get_mt5_data(symbol: str, timeframe: str, num_candles: int) -> pd.DataFrame:
    tf = TIMEFRAME_MAP.get(timeframe)
    if tf is None:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    utc_from = datetime.utcnow() - timedelta(days=30)  # safety window
    initialize_mt5()
    rates = mt5.copy_rates_from(symbol, tf, utc_from, num_candles)


    if rates is None or len(rates) == 0:
        raise RuntimeError(f"No data returned for {symbol} {timeframe}")

    df = pd.DataFrame(rates)
    df['Timestamp'] = pd.to_datetime(df['time'], unit='s', utc=True)
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'tick_volume': 'Volume'
    })
    df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
    return df

#  Rename columns to reflect timeframe source
def rename_ohlcv_columns(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    renamed = df.copy()
    renamed.columns = ['Timestamp'] + [f"{prefix}_{col}" for col in ['Open', 'High', 'Low', 'Close', 'Volume']]
    return renamed

#  Merge logic (replicates your analysis step-by-step)
def get_merged_ohlcv(symbol: str, num_candles: int = 200) -> pd.DataFrame:
    print(" Fetching data from MT5...")

    # Step 1: Pull from MT5
    m15_df = get_mt5_data(symbol, "M15", num_candles)
    h1_df = get_mt5_data(symbol, "H1", num_candles)
    h4_df = get_mt5_data(symbol, "H4", num_candles)
    d1_df = get_mt5_data(symbol, "D1", num_candles)

    # Step 2: Rename OHLCV columns for non-M15 timeframes
    h1_df = rename_ohlcv_columns(h1_df, "H1")
    h4_df = rename_ohlcv_columns(h4_df, "H4")
    d1_df = rename_ohlcv_columns(d1_df, "Daily")

    # Step 3: Sort before merge_asof
    m15_df.sort_values("Timestamp", inplace=True)
    h1_df.sort_values("Timestamp", inplace=True)
    h4_df.sort_values("Timestamp", inplace=True)
    d1_df.sort_values("Timestamp", inplace=True)

    # Step 4: Merge in stages
    merged = pd.merge_asof(m15_df, h1_df, on="Timestamp", direction="backward")
    merged = pd.merge_asof(merged, h4_df, on="Timestamp", direction="backward")
    merged = pd.merge_asof(merged, d1_df, on="Timestamp", direction="backward")

    # Step 5: Validate
    if len(merged) != len(m15_df):
        raise ValueError(f" Row mismatch after merging: expected {len(m15_df)}, got {len(merged)}")

    print(f" Merged data shape: {merged.shape}")
    return merged
