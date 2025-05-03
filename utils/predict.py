# utils/predict.py

"""
Performs live inference using the latest trained models (Transformer, N-BEATS, XGBoost)
on real-time data from MT5. It loads the saved scaler and RFE-selected features,
 applies ensemble logic with custom weights,
 and returns both the final prediction and class probabilities
"""

import numpy as np
import pandas as pd
import json
import os
import xgboost as xgb
from xgboost import Booster
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from keras import layers, models

# === Load saved components ===
BASE_DIR = "models"

# Load RFE feature list
with open(os.path.join(BASE_DIR, "rfe_features.json"), "r") as f:
    RFE_FEATURES = json.load(f)

# Load scaler manually from JSON
with open(os.path.join(BASE_DIR, "scaler.json"), "r") as f:
    scaler_dict = json.load(f)

scaler = StandardScaler()
scaler.mean_ = np.array(scaler_dict['mean_'])
scaler.scale_ = np.array(scaler_dict['scale_'])
scaler.var_ = np.array(scaler_dict['var_'])
scaler.n_features_in_ = scaler_dict['n_features_in_']

# Load ensemble weights
with open(os.path.join(BASE_DIR, "ensemble_weights.json"), "r") as f:
    ENSEMBLE_WEIGHTS = json.load(f)

# === Model architectures ===
def build_advanced_transformer(input_dim):
    def TransformerEncoderBlock(embed_dim, num_heads=8, ff_dim=512, rate=0.1):
        inputs = layers.Input(shape=(embed_dim,))
        x = layers.Reshape((1, embed_dim))(inputs)
        attn_output = layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)(x, x)
        attn_output = layers.Dropout(rate)(attn_output)
        out1 = layers.LayerNormalization(epsilon=1e-6)(x + attn_output)
        ffn = layers.Dense(ff_dim, activation='relu')(out1)
        ffn = layers.Dense(embed_dim)(ffn)
        ffn = layers.Dropout(rate)(ffn)
        out2 = layers.LayerNormalization(epsilon=1e-6)(out1 + ffn)
        out2 = layers.Flatten()(out2)
        return models.Model(inputs, out2)

    inputs = layers.Input(shape=(input_dim,))
    x = TransformerEncoderBlock(input_dim)(inputs)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(5, activation='softmax')(x)
    return models.Model(inputs, outputs)

def build_improved_nbeats(input_dim):
    def ImprovedNBeatsBlock(input_dim, hidden_dim=256):
        x = layers.Input(shape=(input_dim,))
        y = layers.Dense(hidden_dim, activation='relu')(x)
        y = layers.BatchNormalization()(y)
        y = layers.Dropout(0.3)(y)
        y = layers.Dense(hidden_dim, activation='relu')(y)
        y = layers.BatchNormalization()(y)
        y = layers.Dense(input_dim, activation='linear')(y)
        return models.Model(inputs=x, outputs=y)

    input_layer = layers.Input(shape=(input_dim,))
    x = ImprovedNBeatsBlock(input_dim)(input_layer)
    x = ImprovedNBeatsBlock(input_dim)(x)
    x = ImprovedNBeatsBlock(input_dim)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(128, activation='relu')(x)
    output_layer = layers.Dense(5, activation='softmax')(x)
    return models.Model(inputs=input_layer, outputs=output_layer)

# Load models (weights only)
transformer_model = build_advanced_transformer(input_dim=len(RFE_FEATURES))
transformer_model.load_weights(os.path.join(BASE_DIR, "transformer_model.h5"))

nbeats_model = build_improved_nbeats(input_dim=len(RFE_FEATURES))
nbeats_model.load_weights(os.path.join(BASE_DIR, "nbeats_model.h5"))

xgb_model = Booster()
xgb_model.load_model(os.path.join(BASE_DIR, "xgboost_model.json"))

# Wrapper for XGBoost to predict proba with raw Booster
class XGBWrapper:
    def __init__(self, booster):
        self.booster = booster

    def predict_proba(self, X):
        dmatrix = xgb.DMatrix(X)
        return self.booster.predict(dmatrix)

xgb_wrapper = XGBWrapper(xgb_model)

# === Prediction Function ===
def predict_ensemble(df):
    df_input = df.copy()
    df_selected = df_input[RFE_FEATURES]
    df_scaled = scaler.transform(df_selected)

    transformer_probs = transformer_model.predict(df_scaled)
    nbeats_probs = nbeats_model.predict(df_scaled)
    xgb_probs = xgb_wrapper.predict_proba(df_scaled)

    ensemble_probs = (
        ENSEMBLE_WEIGHTS['transformer'] * transformer_probs +
        ENSEMBLE_WEIGHTS['nbeats'] * nbeats_probs +
        ENSEMBLE_WEIGHTS['xgboost'] * xgb_probs
    )

    final_pred = np.argmax(ensemble_probs, axis=1)[0]
    return final_pred, {
        "transformer": transformer_probs[0].tolist(),
        "nbeats": nbeats_probs[0].tolist(),
        "xgboost": xgb_probs[0].tolist(),
        "ensemble": ensemble_probs[0].tolist()
    }
