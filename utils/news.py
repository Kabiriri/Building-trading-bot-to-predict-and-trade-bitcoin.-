# utils/news.py

"""
Fetches upcoming high-impact economic events using the FMP API.
Filters for USD-only and high-impact events within a defined lookahead window.
Includes a utility to detect whether any news event overlaps with the current time (news block logic).
Adapted specifically for BTCUSD to suppress trades around macroeconomic volatility.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# === Configuration ===
FMP_API_KEY = "ucGufh0Tg85Df2AAiVm4V23UyQQ2t1r9"
FMP_URL = "https://financialmodelingprep.com/api/v3/economic_calendar"

# === Parameters ===
USD_ONLY = True
IMPACT_LEVEL = "High"
TIMEZONE = "UTC"  # Assumes all logic in UTC
NEWS_LOOKAHEAD_MINUTES = 60


def get_upcoming_news(minutes_ahead=NEWS_LOOKAHEAD_MINUTES):
    """
    Fetch upcoming economic events within the next `minutes_ahead` minutes.
    Filters for high-impact USD news only.
    """
    now = datetime.now(pytz.utc)
    later = now + timedelta(minutes=minutes_ahead)

    params = {
        "from": now.strftime("%Y-%m-%d"),
        "to": later.strftime("%Y-%m-%d"),
        "apikey": FMP_API_KEY
    }

    try:
        response = requests.get(FMP_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Warning: Failed to fetch news from FMP: {e}")
        return []

    upcoming = []
    for event in data:
        try:
            event_time = datetime.strptime(event["date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
            if now <= event_time <= later:
                if (not USD_ONLY or event.get("country", "") == "US") and \
                   event.get("impact", "") == IMPACT_LEVEL:
                    upcoming.append({
                        "event": event.get("event"),
                        "time": event_time,
                        "impact": event.get("impact"),
                        "currency": event.get("country")
                    })
        except Exception:
            continue

    return upcoming


def is_news_block_now(news_list, window_minutes=30):
    """
    Determine if any news is within ±window_minutes of now.
    Returns True if a news block is active.
    """
    now = datetime.now(pytz.utc)
    for event in news_list:
        delta = abs((event["time"] - now).total_seconds()) / 60
        if delta <= window_minutes:
            return True
    return False
