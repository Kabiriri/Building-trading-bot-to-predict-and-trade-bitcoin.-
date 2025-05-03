# utils/feature_engineer.py

"""
Generates advanced technical and structural features from OHLCV data,
including indicators (SMA, EMA, ATR, MACD, Bollinger Bands),
 market structure (swing points, BOS, order blocks), and volatility/volume patterns.
 It produces a final engineered DataFrame used for model inference and training.
"""

import pandas as pd
import numpy as np

# === Technical Indicators ===
def add_moving_averages(df):
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    return df

def add_atr(df):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift(1))
    low_close = np.abs(df['Low'] - df['Close'].shift(1))
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR_14'] = tr.rolling(window=14, min_periods=1).mean()
    return df

def add_bollinger_bands(df):
    df['BB_Mid'] = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Mid'] + (2 * std)
    df['BB_Lower'] = df['BB_Mid'] - (2 * std)
    return df

def add_macd(df):
    short_ema = df['Close'].ewm(span=12, adjust=False).mean()
    long_ema = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = short_ema - long_ema
    return df

# === Market Structure ===
def add_market_structure_features(df):
    df['Swing_Low'] = df['Low'][(df['Low'].shift(3) > df['Low']) & (df['Low'].shift(-3) > df['Low'])]
    df['Rolling_High'] = df['High'].rolling(window=20).max()
    df['Rolling_Low'] = df['Low'].rolling(window=20).min()
    return df

def detect_bos(df):
    df['Swing_High'] = np.nan
    df['Swing_Low'] = np.nan
    for i in range(5, len(df)-5):
        if df.loc[i, 'High'] > max(df.loc[i-5:i-1, 'High']) and df.loc[i, 'High'] > max(df.loc[i+1:i+5, 'High']):
            df.loc[i, 'Swing_High'] = df.loc[i, 'High']
        if df.loc[i, 'Low'] < min(df.loc[i-5:i-1, 'Low']) and df.loc[i, 'Low'] < min(df.loc[i+1:i+5, 'Low']):
            df.loc[i, 'Swing_Low'] = df.loc[i, 'Low']
    df['Prev_Swing_High'] = df['Swing_High'].ffill().shift(1)
    df['Prev_Swing_Low'] = df['Swing_Low'].ffill().shift(1)
    df['Prev_Highs'] = df['High'].rolling(window=20).max().shift(1)
    df['Prev_Lows'] = df['Low'].rolling(window=20).min().shift(1)
    return df

def detect_fvg(df):
    df['FVG_Low'] = np.nan
    df['FVG_High'] = np.nan
    for i in range(2, len(df)):
        c1, c3 = i - 2, i
        if df.loc[c1, 'High'] < df.loc[c3, 'Low']:
            df.loc[c3, 'FVG_Low'] = df.loc[c1, 'High']
            df.loc[c3, 'FVG_High'] = df.loc[c3, 'Low']
        elif df.loc[c1, 'Low'] > df.loc[c3, 'High']:
            df.loc[c3, 'FVG_Low'] = df.loc[c3, 'High']
            df.loc[c3, 'FVG_High'] = df.loc[c1, 'Low']
    return df

def detect_order_blocks(df):
    df['Bullish_OB'] = 0
    df['Bearish_OB'] = 0
    df['OB_Low'] = np.nan
    df['OB_High'] = np.nan
    for i in range(len(df) - 5):
        body = abs(df.loc[i, 'Close'] - df.loc[i, 'Open'])
        rng = df.loc[i, 'High'] - df.loc[i, 'Low']
        if rng == 0 or (body / rng) < 0.6:
            continue
        if df.loc[i, 'Close'] < df.loc[i, 'Open'] and df.loc[i+1:i+5, 'High'].max() > df.loc[i, 'High']:
            df.loc[i, 'Bullish_OB'] = 1
            df.loc[i, 'OB_Low'] = df.loc[i, 'Low']
            df.loc[i, 'OB_High'] = df.loc[i, 'High']
        if df.loc[i, 'Close'] > df.loc[i, 'Open'] and df.loc[i+1:i+5, 'Low'].min() < df.loc[i, 'Low']:
            df.loc[i, 'Bearish_OB'] = 1
            df.loc[i, 'OB_Low'] = df.loc[i, 'Low']
            df.loc[i, 'OB_High'] = df.loc[i, 'High']
    df['OB_Mitigated'] = 0
    for i in range(1, len(df)):
        if df.loc[i, 'Bullish_OB'] == 0 and df.loc[i, 'Low'] <= df.loc[i - 1, 'OB_High'] and df.loc[i - 1, 'Bullish_OB'] == 1:
            df.loc[i, 'OB_Mitigated'] = 1
        elif df.loc[i, 'Bearish_OB'] == 0 and df.loc[i, 'High'] >= df.loc[i - 1, 'OB_Low'] and df.loc[i - 1, 'Bearish_OB'] == 1:
            df.loc[i, 'OB_Mitigated'] = 1
    return df

def detect_breaker_blocks(df):
    df['Breaker_Block'] = 0
    for i in range(1, len(df)):
        if df.loc[i-1, 'Bullish_OB'] == 1 and df.loc[i, 'Close'] < df.loc[i-1, 'OB_Low']:
            df.loc[i, 'Breaker_Block'] = 1
        elif df.loc[i-1, 'Bearish_OB'] == 1 and df.loc[i, 'Close'] > df.loc[i-1, 'OB_High']:
            df.loc[i, 'Breaker_Block'] = 1
    return df

def add_premium_discount_zone(df):
    df['Fair_Value_Mid'] = (df['Rolling_High'] + df['Rolling_Low']) / 2
    df['Is_Premium'] = (df['Close'] > df['Fair_Value_Mid']).astype(int)
    df['Is_Discount'] = (df['Close'] < df['Fair_Value_Mid']).astype(int)
    return df

def add_volume_volatility_features(df):
    df['Avg_Volume'] = df['Volume'].rolling(window=20).mean()
    df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
    df['HV'] = df['Log_Returns'].rolling(window=20).std() * 100
    df['HV_lag1'] = df['HV'].shift(1)
    return df

def add_candle_patterns(df):
    body = abs(df['Close'] - df['Open'])
    wick_top = df['High'] - df[['Close', 'Open']].max(axis=1)
    wick_bottom = df[['Close', 'Open']].min(axis=1) - df['Low']
    rng = df['High'] - df['Low']
    df['Doji'] = (body / rng < 0.1).astype(int)
    return df

# === Main Pipeline ===
def engineer_features(df):
    df = add_moving_averages(df)
    df = add_atr(df)
    df = add_bollinger_bands(df)
    df = add_macd(df)
    df = add_market_structure_features(df)
    df = detect_bos(df)
    df = detect_fvg(df)
    df = detect_order_blocks(df)
    df = detect_breaker_blocks(df)
    df = add_premium_discount_zone(df)
    df = add_volume_volatility_features(df)
    df = add_candle_patterns(df)

    # Handle missing values
    df.bfill(inplace=True)
    df.ffill(inplace=True)

    # Trim to final 49 features
    final_columns = [
        "Open", "High", "Low", "Close", "H1_Open", "H1_Low", "H1_Close", "H1_Volume",
        "H4_High", "H4_Low", "H4_Close", "H4_Volume", "Daily_Open", "Daily_High",
        "Daily_Low", "Daily_Close", "Daily_Volume", "SMA_10", "SMA_200", "EMA_10",
        "EMA_50", "EMA_200", "ATR_14", "BB_Upper", "BB_Lower", "MACD", "Swing_Low",
        "Rolling_High", "Rolling_Low", "Prev_Swing_High", "Prev_Swing_Low", "Prev_Highs",
        "Prev_Lows", "FVG_Low", "FVG_High", "Bullish_OB", "Bearish_OB", "OB_Low",
        "OB_High", "OB_Mitigated", "Breaker_Block", "Fair_Value_Mid", "Is_Premium",
        "Is_Discount", "Avg_Volume", "Log_Returns", "HV", "Doji", "HV_lag1"
    ]
    df = df[final_columns]

    return df
