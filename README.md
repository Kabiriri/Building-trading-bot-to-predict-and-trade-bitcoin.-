# 🚀 AI-Powered Bitcoin Trading Bot

**Predicting BTC/USD Price Movements with LSTM, GRU, Transformer & XGBoost Ensembles**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Tech Stack](#-tech-stack)
4. [Data & Findings](#-data--findings)
5. [Dataset Overview](#-dataset-overview)
6. [Feature Catalog](#-feature-catalog)
7. [Model Performance](#-model-performance)
8. [Installation](#-installation)
9. [Usage](#-usage)
10. [Evaluation Metrics](#-evaluation-metrics)
11. [Conclusions & Recommendations](#-conclusions--recommendations)
12. [Contributing](#-contributing)
13. [License](#-license)
14. [Acknowledgments](#-acknowledgments)

---

## 🌟 Project Overview

### 🔍 Problem Statement

Bitcoin's extreme volatility challenges traditional trading tools. This project delivers an AI trading bot that predicts short-term BTC/USD price movements using deep learning and ensemble strategies, generating actionable multi-class signals (Strong Bullish/Bearish, Weak Bullish/Bearish, Neutral).

### 🎯 Motivation

- **Market Need**: 24/7 crypto markets demand real-time adaptive decision-making
- **Technical Edge**: Combines market microstructure analysis with modern ML
- **Profit Potential**: 73.65% accuracy in ensemble model backtests

### 🏆 Key Achievements

- Hybrid classification system capturing direction **and** strength of price moves
- Live MetaTrader 5 integration for automated trading
- 22% simulated annualized return with Sharpe Ratio >1.8

---

## 🛠 Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Timeframe Fusion** | Merged M15/H1/H4/Daily OHLCV data |
| **Smart Money Features** | BOS, CHoCH, Order Blocks, FVG detection |
| **Model Zoo** | LSTM, GRU, Transformer, XGBoost implementations |
| **Ensemble Engine** | Stacked predictions from top-performing models |
| **MLOps Pipeline** | Automated retraining & concept drift detection |

---

## 💻 Tech Stack

### Core ML
```python
Python 3.8+, TensorFlow 2.12, PyTorch 1.13, XGBoost 1.7, Scikit-learn 1.2
```

### Data Processing
```python
Pandas 2.0, NumPy 1.24, TA-Lib 0.4.24
```

### Deployment
```python
MetaTrader5, Docker, FastAPI, Prometheus (Monitoring)
```

---

## 📊 Data & Findings

### 📂 Dataset Source
- Tickstory (2017-2025 BTC/USD OHLCV)
- Size: 239k samples across 4 timeframes
- Features: 80+ technical & structural indicators

### 🔑 Key Findings

#### Data Insights:
- **Volatility metrics** (HV, ATR) and **market structure features** (BOS, FVG) were top predictors
- 15-minute charts dominated noise, while daily/weekly trends provided structural context

#### Class-Level Insights:
- **Strong Bullish/Bearish:** Precision >65%, critical for high-confidence trades
- **Neutral Class:** Rare (0.8% of data), with recall <20% across models

#### Risk Management:
- **Maximum Drawdown:** 23% (Ensemble) vs. 35% (Baseline LSTM)
- **Sharpe Ratio:** 1.8 (Ensemble), indicating strong risk-adjusted returns

---

## 📈 Dataset Overview

### Primary Sources
- Tickstory (Historical OHLCV)
- MetaTrader5 (Real-time feed)
- NewsAPI (Fundamental data - future integration)

### Key Statistics

| Metric | Value |
|--------|-------|
| Time Coverage | 2017-2025 |
| Total Samples | 239,000 |
| Base Timeframe | M15 (15-min) |
| Merged Timeframes | H1/H4/Daily |
| Original Features | 28 |
| Engineered Features | 85+ |

### Data Quality Assessment
- 0.8% missing values in H4/Daily frames (forward-filled)
- 12.3% class imbalance (Strong Bullish vs Bearish)
- 4.7% duplicated timestamps (DST transitions)

### Correlation Insights
| Feature | Target Correlation |
|---------|-------------------|
| Historical Volatility | 0.82 |
| ATR_14 | 0.78 |
| RSI_14 | 0.65 |
| MACD_Hist | 0.58 |

---

## 📋 Feature Catalog

### Core Price Data
```python
['Open', 'High', 'Low', 'Close', 'Volume',
 'H1_Open', 'H4_Close', 'Daily_High']  # Multi-timeframe OHLCV
```

### Technical Indicators
| Category | Features (Examples) |
|----------|---------------------|
| Trend | SMA_10, EMA_50, MACD_Hist |
| Momentum | RSI_14, Stoch_%K, Log_Returns |
| Volatility | ATR_14, BB_Upper, HV_30 |
| Volume | Volume_Spike, OBV, VWAP |

### Market Structure Features
```python
['Bullish_BOS', 'Bearish_CHoCH', 'FVG_Low', 'SSL',
 'OB_Mitigated', 'Swing_Leg_Count', 'Fair_Value_Mid']
```

### Smart Money Signal Validation
| Signal | Precision | Recall | F1-Score |
|--------|-----------|--------|----------|
| Bullish BOS | 0.89 | 0.72 | 0.80 |
| FVG Fill | 0.68 | 0.61 | 0.64 |
| OB Mitigation | 0.75 | 0.66 | 0.70 |
| SSL Sweep | 0.63 | 0.58 | 0.60 |

---

## 🏅 Model Performance

### Model Comparison

| Model | Accuracy | F1-Score (Macro) | Annualized Return | Training Time |
|-------|----------|------------------|-------------------|---------------|
| XGBoost (Optuna) | 70.25% | 0.71 | 17% | 18min |
| LSTM (RFE Features) | 68.15% | 0.65 | 14% | - |
| GRU | 69.14% | - | - | - |
| Transformer | 72.39% | 0.73 | 19% | 2.1hr |
| **Ensemble** | **73.65%** | **0.74** | **22%** | 3.4hr |

### Class Distribution
| Class | Percentage |
|-------|------------|
| Neutral | 0.8% |
| Weak Bullish | 34.6% |
| Strong Bearish | 15.1% |
| Weak Bearish | 34.0% |
| Strong Bullish | 15.5% |

### Target Variable Analysis
```python
def label_movement(returns):
    if abs(returns) < 0.0025: return 0  # Neutral
    elif 0.0025 <= returns < 0.005: return 1  # Weak Bull
    elif returns >= 0.005: return 4  # Strong Bull
    elif -0.005 < returns <= -0.0025: return 3  # Weak Bear
    else: return 2  # Strong Bear
```

---

## 📥 Installation

### Prerequisites

- ﻿requests~=2.32.3
- pandas~=2.2.3
- pytz~=2025.2
- metatrader5~=5.0.4993
- numpy~=2.1.3
- xgboost~=3.0.0
- scikit-learn~=1.6.1
- tensorflow~=2.19.0
- keras~=3.9.2
- joblib~=1.4.2
- referencing~=0.36.2
- pygments~=2.19.1
- defusedxml~=0.7.1
- ipython~=8.36.0
- pyside6~=6.9.0
- pillow~=11.1.0
- pip~=25.1
- attrs~=25.3.0
- wheel~=0.45.1
- pysocks~=1.7.1
- protobuf~=4.25.7
- openssl~=3.5.0
- rsa~=4.9.1
- pyasn1~=0.6.1
- absl-py~=2.2.2
- gast~=0.4.0
- grpcio~=1.71.0
- h5py~=3.13.0
- mako~=1.3.10
- babel~=2.17.0
- markupsafe~=3.0.2
- rich~=14.0.0
- colorama~=0.4.6
- yaml~=0.2.5
- pyyaml~=6.0.2
- libclang~=18.1.1
- six~=1.17.0
- scipy~=1.15.2
- wrapt~=1.14.1
- charset-normalizer~=3.4.1
- setuptools~=79.0.1
- overrides~=7.7.0
- cffi~=1.17.1
- google-pasta~=0.2.0
- threadpoolctl~=3.6.0
- matplotlib~=3.10.1
- platformdirs~=4.3.7
- jax~=0.4.30
- pyasn1-modules~=0.4.2
- cachetools~=5.5.2
- certifi~=2025.1.31
- urllib3~=2.4.0
- packaging~=24.2
- psutil~=7.0.0
- optuna~=4.3.0
- sqlalchemy~=2.0.24
- alembic~=1.14.1
- colorlog~=6.9.0
- tqdm~=4.67.1
- pyarrow~=20.0.0
- python-dateutil~=2.9.0.post0
- importlib_resources~=6.5.2
- importlib-metadata~=8.6.1
- seaborn~=0.13.2
- cycler~=0.12.1
- statsmodels~=0.14.4
- zstandard~=0.23.0
- h2~=4.2.0
- greenlet~=3.2.1
- markdown~=3.8
- oauthlib~=3.2.2
- blinker~=1.9.0
- idna~=3.10
- contourpy~=1.3.2
- fonttools~=4.57.0
- freetype~=2.13.3
- cairo~=1.18.4
- unicodedata2~=16.0.0
- pyparsing~=3.2.3
- jinja2~=3.1.6
- termcolor~=3.1.0
- ipykernel~=6.29.5
- tornado~=6.4.2
- kiwisolver~=1.4.7
- opt-einsum~=3.4.0
- tomli~=2.2.1
- zipp~=3.21.0
- tensorboard~=2.19.0
- flatbuffers~=25.2.10
- astunparse~=1.6.3
- werkzeug~=3.1.3
- google-auth-oauthlib~=1.0.0
- click~=8.1.8
- requests-oauthlib~=2.0.0
- streamlit~=1.45.0


```bash
git clone git@github.com:Kabiriri/Building-trading-bot-to-predict-and-trade-bitcoin.-.git
cd bitcoin-trading-bot
conda create -n tradingbot python=3.8
conda activate tradingbot
pip install -r requirements.txt
```

---

## 🔄 Usage

### Data Preprocessing
```python
# Run data preprocessing pipeline
python src/data/preprocess.py --timeframes M15,H1,H4,D1 --start_date 2017-01-01
```

### Model Training
```python
# Train individual models
python src/models/train.py --model transformer --epochs 100 --batch_size 64

# Train ensemble
python src/models/train_ensemble.py --models transformer,xgboost,nbeats
```

### Live Trading
```python
# Start trading bot with preferred model
python src/trading/bot.py --model ensemble --risk_level medium --account_mt5 YOUR_ACCOUNT
```

### Backtesting
```python
# Run backtest on historical data
python src/evaluation/backtest.py --model ensemble --period 2023-01-01:2024-01-01
```

---

## 📊 Evaluation Metrics

### Performance Metrics
- **Accuracy:** Percentage of correctly predicted price direction and magnitude
- **F1-Score:** Harmonic mean of precision and recall
- **Annualized Return:** Trading performance over one year
- **Sharpe Ratio:** Risk-adjusted return (1.8 for ensemble model)
- **Maximum Drawdown:** Largest peak-to-trough decline (23% for ensemble)

### Preprocessing Steps
- Timeframe alignment & synchronization
- Feature engineering (ATR, HV, BOS flags)
- Class-balanced stratified sampling
- Z-score normalization for sequential models

---

## 📝 Conclusions & Recommendations

### Conclusions:
- The ensemble model combines Transformer's sequence modeling, XGBoost's feature efficiency, and N-BEATS' interpretability for optimal performance
- Market structure features (BOS, FVG) and volatility metrics are critical for predicting BTC movements
- 15-min BOS signals have 89% precision but low recall (34%)
- Volatility features (HV, ATR) show strongest predictive power

### Recommendations:
- **Deployment:** Integrate the ensemble model into MetaTrader 5 with real-time VPS execution
- **Monitoring:** Implement drift detection (e.g., KS test) to trigger model retraining
- **Enhancements:**
  - Add macroeconomic indicators (e.g., Fed rates, ETF flows)
  - Test on altcoins (ETH, SOL) to validate generalizability
- **Risk Mitigation:**
  - Cap position sizes during low-confidence (Neutral) regimes
  - Use ATR-based dynamic stop-losses to limit drawdowns

---

## 🤝 Contributing

### High-Impact Areas
- Add alternative data sources (liquidations data, on-chain metrics)
- Implement reinforcement learning for position sizing
- Enhance MT5/Discord integration

### Workflow
1. Fork repository
2. Create feature branch
3. Submit PR with detailed test results

---

## 📜 License

MIT License - See LICENSE for details.

**Disclaimer:** This is experimental software - trade at your own risk.

---

## 🙏 Acknowledgments

- Tickstory for high-quality historical data
- MetaTrader 5 Python API developers
- Original N-BEATS & Transformer paper authors

> "Markets remain irrational longer than you can stay solvent." - Always verify signals with fundamental analysis.

---

## 📞 Contact & Support

For questions regarding this project or implementation details, please contact:
- **Email:** [MISHECK:misheck.kibunja@student.moringaschool.com],
[ZENA:zena.weru@student.moringaschool.com],
[JOSEPH:joseph.mwangi5@student.moringaschool.com],
[ACINATH:acinath.onkendi@student.moringaschool.com],
[ABDIRAHAMAN:abdirahaman.sheikh@student.moringaschool.com](mailto:data.team@example.com)
- **Project Repository:** [git@github.com:Kabiriri/Building-trading-bot-to-predict-and-trade-bitcoin.-.git](git@github.com:Kabiriri/Building-trading-bot-to-predict-and-trade-bitcoin.-.git)

---

*This README was last updated on May 4, 2025* by ALGOMINDS

*© 2025 | All Rights Reserved*
