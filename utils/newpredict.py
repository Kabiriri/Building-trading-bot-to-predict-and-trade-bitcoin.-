# utils/newpredict.py

"""
Performs live inference using the latest trained models (Transformer, N-BEATS, XGBoost)
on real-time data from MT5. It loads the saved scaler and RFE-selected features,
 applies ensemble logic with custom weights,
 and returns both the final prediction and class probabilities
"""

import numpy as np
import pandas as pd
import joblib
import json
import os
import xgboost as xgb
from tensorflow import keras
from keras import layers, models
from utils.datafeed import get_merged_ohlcv
from utils.feature_engineer import engineer_features

# === Paths ===
BASE_DIR = "newmodels"
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "rfe_features.json")
TRANSFORMER_PATH = os.path.join(BASE_DIR, "transformer_model.keras")
NBEATS_PATH = os.path.join(BASE_DIR, "nbeats_model.keras")
XGB_PATH = os.path.join(BASE_DIR, "xgboost_model.json")

# === Load Components ===
scaler = joblib.load(SCALER_PATH)
with open(FEATURES_PATH, "r") as f:
    rfe_features = json.load(f)

transformer_model = keras.models.load_model(TRANSFORMER_PATH)
nbeats_model = keras.models.load_model(NBEATS_PATH)

xgb_booster = xgb.Booster()
xgb_booster.load_model(XGB_PATH)

class XGBWrapper:
    def __init__(self, booster):
        self.booster = booster

    def predict_proba(self, X):
        dmatrix = xgb.DMatrix(X)
        raw_preds = self.booster.predict(dmatrix)
        return raw_preds

xgb_wrapper = XGBWrapper(xgb_booster)

# === Ensemble Logic ===
ENSEMBLE_WEIGHTS = {
    "transformer": 0.5,
    "nbeats": 0.3,
    "xgboost": 0.2
}

def predict_with_ensemble(symbol: str):
    # Pull and process latest market data
    raw_df = get_merged_ohlcv(symbol)
    features_df = engineer_features(raw_df)

    latest = features_df[rfe_features].tail(1)

    # Scale features and preserve names
    scaled_array = scaler.transform(latest)
    scaled = pd.DataFrame(scaled_array, columns=latest.columns)

    # Predict from each model
    transformer_probs = transformer_model.predict(scaled)[0]
    nbeats_probs = nbeats_model.predict(scaled)[0]
    xgb_probs = xgb_wrapper.predict_proba(scaled)[0]

    # Ensemble
    ensemble_probs = (
        ENSEMBLE_WEIGHTS['transformer'] * transformer_probs +
        ENSEMBLE_WEIGHTS['nbeats'] * nbeats_probs +
        ENSEMBLE_WEIGHTS['xgboost'] * xgb_probs
    )

    final_class = int(np.argmax(ensemble_probs))
    return final_class, {
        "transformer": transformer_probs.tolist(),
        "nbeats": nbeats_probs.tolist(),
        "xgboost": xgb_probs.tolist(),
        "ensemble": ensemble_probs.tolist()
    }
