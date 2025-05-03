# dashboard.py

"""
This is the main performance dashboard for the live BTCUSD AI trading system, built with Streamlit.
It reads real trade logs (logs/trade_log.json) and provides:
1. Live trade history
2. Trade outcome stats
3. Cumulative PnL curve
4.Filters by symbol and status
5.Visual charts for direction, outcomes, and PnL distribution
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# === App Config ===
st.set_page_config(page_title="BTCUSD Dashboard", layout="wide")
st.title("📈 BTCUSD AI Trading Performance Dashboard")

LOG_PATH = "logs/trade_log.json"

@st.cache_data
def load_trade_log(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    with open(path, "r") as f:
        raw = json.load(f)
    df = pd.DataFrame(raw)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    if "exit_time" in df.columns:
        df["exit_time"] = pd.to_datetime(df["exit_time"])
    return df

df = load_trade_log(LOG_PATH)

if df.empty:
    st.warning("⚠️ No trades logged yet.")
    st.stop()

# === Sidebar Filters ===
symbols = df["symbol"].dropna().unique().tolist()
selected_symbols = st.sidebar.multiselect("🔍 Filter by Symbol", symbols, default=symbols)
df = df[df["symbol"].isin(selected_symbols)]
df.sort_values("timestamp", ascending=False, inplace=True)

# === Summary Metrics ===
st.subheader("📊 Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Trades", len(df))
col2.metric("Executed Trades", (df["status"] == "executed").sum())
col3.metric("Closed Trades", (df["log_type"] == "closed").sum())

# === Trade Table ===
st.subheader("📜 Trade History")
st.dataframe(df, use_container_width=True)

# === Cumulative PnL Curve ===
closed = df[df["log_type"] == "closed"].copy()
if not closed.empty:
    closed.sort_values("exit_time", inplace=True)
    closed["cumulative_pnl"] = closed["pnl_usd"].cumsum()

    st.subheader("📈 Cumulative PnL Over Time")
    st.line_chart(closed.set_index("exit_time")["cumulative_pnl"])

# === Additional Insights ===
with st.expander("📌 Performance Breakdown"):
    if "tp1_hit" in closed.columns:
        st.write("✅ TP1 Hits:", closed["tp1_hit"].sum())
        st.write("❌ SL Hits:", closed["sl_hit"].sum())
    st.write("📈 Mean PnL:", f"${closed['pnl_usd'].mean():.2f}")
    st.bar_chart(closed["direction"].value_counts())
