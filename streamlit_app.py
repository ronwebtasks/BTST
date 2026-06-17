import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="NSE BTST Multi-Screener", page_icon="⚡", layout="wide")

st.title("⚡ NSE High-Probability BTST Screener")
st.markdown("""
This master scanner covers both **Nifty Top 200 Equity Stocks** (for cash market breakouts) and the **F&O Segment** with dynamic 1-Step Out-of-the-Money (OTM) Call Option mapping.
""")

# Universe 1: Standard Liquid Nifty Stocks (Cash Segment)
NIFTY_200_CASH = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "LT.NS", "M&M.NS",
    "SUNPHARMA.NS", "TATAMOTORS.NS", "AXISBANK.NS", "ASIANPAINT.NS", "HCLTECH.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "COALINDIA.NS", "TITAN.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "JIOFIN.NS", "ADANIENT.NS", "ADANIPORTS.NS", "ADANIGREEN.NS", "ADANIPOWER.NS",
    "TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "GRASIM.NS", "LTIM.NS", "TECHM.NS", "WIPRO.NS", "HINDUNILVR.NS", "BRITANNIA.NS", "CIPLA.NS",
    "DRREDDY.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BPCL.NS", "IOC.NS", "BEL.NS", "HAL.NS", "DLF.NS",
    "VBL.NS", "ZOMATO.NS", "TRENT.NS", "PIDILITIND.NS", "SIEMENS.NS", "ABB.NS", "INDIGO.NS", "TATACONSUM.NS", "SHRIRAMFIN.NS", "CHOLAFIN.NS",
    "PFC.NS", "RECL.NS", "GAIL.NS", "SAIL.NS", "NMDC.NS", "GMRINFRA.NS", "IDEA.NS", "PNB.NS", "BANKBARODA.NS", "CANBK.NS"
]

# Universe 2: F&O Segment with Lot Sizes and Option Strike Steps
FANDO_OPTIONS = {
    "RELIANCE": {"symbol": "RELIANCE.NS", "lot_size": 250, "strike_step": 20},
    "TCS": {"symbol": "TCS.NS", "lot_size": 175, "strike_step": 20},
    "INFY": {"symbol": "INFY.NS", "lot_size": 400, "strike_step": 10},
    "HDFCBANK": {"symbol": "HDFCBANK.NS", "lot_size": 550, "strike_step": 10},
    "ICICIBANK": {"symbol": "ICICIBANK.NS", "lot_size": 700, "strike_step": 5},
    "SBIN": {"symbol": "SBIN.NS", "lot_size": 1500, "strike_step": 5},
    "TATASTEEL": {"symbol": "TATASTEEL.NS", "lot_size": 5500, "strike_step": 1},
    "ADANIENT": {"symbol": "ADANIENT.NS", "lot_size": 300, "strike_step": 50},
    "AXISBANK": {"symbol": "AXISBANK.NS", "lot_size": 625, "strike_step": 10},
    "PFC": {"symbol": "PFC.NS", "lot_size": 3750, "strike_step": 2.5},
    "RECL": {"symbol": "RECL.NS", "lot_size": 2000, "strike_step": 2.5},
    "HAL": {"symbol": "HAL.NS", "lot_size": 300, "strike_step": 20},
    "TRENT": {"symbol": "TRENT.NS", "lot_size": 150, "strike_step": 50},
    "BHARTIARTL": {"symbol": "BHARTIARTL.NS", "lot_size": 950, "strike_step": 10}
}

# Sidebar Mode Selection
st.sidebar.header("🎯 Mode Selection")
scanner_mode = st.sidebar.selectbox("Choose Target Market Segment", ["Nifty Top Stocks (Cash)", "F&O Derivatives (Options Sizer)"])

# Filters
st.sidebar.header("Scanner Configurations")
vol_multiplier = st.sidebar.slider("Min Volume Multiplier (vs 20-day Avg)", 1.0, 3.0, 1.5, 0.1)
rsi_min = st.sidebar.slider("Minimum RSI (14)", 50, 70, 60, 1)
price_near_high_pct = st.sidebar.slider("Max Distance from Day's High (%)", 0.1, 2.0, 0.5, 0.1)

# Style function
def style_signal(val):
    if val == "STRONG BUY": return 'background-color: #2ecc71; color: white; font-weight: bold;'
    elif val == "WATCH": return 'background-color: #f1c40f; color: black;'
    return 'background-color: #e74c3c; color: white;'

if st.button("🚀 Run Live BTST Scan"):
    results = []
    
    if scanner_mode == "Nifty Top Stocks (Cash)":
        st.info(f"Scanning {len(NIFTY_200_CASH)} liquid cash market stocks... Please wait.")
        
        for ticker in NIFTY_200_CASH:
            try:
                stock = yf.Ticker(ticker)
                df_daily = stock.history(period="1mo", interval="1d")
                if len(df_daily) < 20: continue
                
                avg_volume = df_daily['Volume'].iloc[-21:-1].mean()
                current_volume = df_daily['Volume'].iloc[-1]
                current_close = df_daily['Close'].iloc[-1]
                current_high = df_daily['High'].iloc[-1]
                
                dist_from_high = ((current_high - current_close) / current_high) * 100
                
                # RSI-14
                delta = df_daily['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / (loss + 1e-10)
                rsi = 100 - (100 / (1 + rs)).iloc[-1]
                
                # Scoring
                score = 0
                if current_volume >= (avg_volume * vol_multiplier): score += 30
                if rsi >= rsi_min: score += 30
                if dist_from_high <= price_near_high_pct: score += 20
                if current_close > df_daily['Close'].iloc[-2]: score += 20
                
                action = "STRONG BUY" if score >= 80 else "WATCH" if score >= 50 else "AVOID"
                
                results.append({
                    "Stock": ticker.replace(".NS", ""),
                    "Close Price (₹)": round(current_close, 2),
                    "Vol vs Avg": f"{round(current_volume / avg_volume, 1)}x",
                    "RSI (14)": round(rsi, 1),
                    "Dist from High": f"{round(dist_from_high, 2)}%",
                    "Score": score,
                    "Signal": action
                })
            except Exception:
                continue
                
        if results:
            res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
            st.dataframe(res_df.style.map(style_signal, subset=['Signal']), use_container_width=True)
            
    else:
        st.info(f"Scanning F&O chains and calculating lot exposures... Please wait.")
        
        for name, meta in FANDO_OPTIONS.items():
            try:
                stock = yf.Ticker(meta["symbol"])
                df_daily = stock.history(period="1mo", interval="1d")
                if len(df_daily) < 20: continue
                
                avg_volume = df_daily['Volume'].iloc[-21:-1].mean()
                current_volume = df_daily['Volume'].iloc[-1]
                current_close = df_daily['Close'].iloc[-1]
                current_high = df_daily['High'].iloc[-1]
                
                dist_from_high = ((current_high - current_close) / current_high) * 100
                
                delta = df_daily['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / (loss + 1e-10)
                rsi = 100 - (100 / (1 + rs)).iloc[-1]
                
                score = 0
                if current_volume >= (avg_volume * vol_multiplier): score += 30
                if rsi >= rsi_min: score += 30
                if dist_from_high <= price_near_high_pct: score += 20
                if current_close > df_daily['Close'].iloc[-2]: score += 20
                
                action = "STRONG BUY" if score >= 80 else "WATCH" if score >= 50 else "AVOID"
                
                # Strike calculations
                atm_strike = round(current_close / meta["strike_step"]) * meta["strike_step"]
                otm_strike = int(atm_strike + meta["strike_step"]) if current_close >= atm_strike else int(atm_strike)
                if otm_strike <= current_close: otm_strike += int(meta["strike_step"])
                
                # Estimated option premium (1.8% of spot as a safe proxy benchmark)
                est_premium = round(current_close * 0.018, 2)
                capital_needed = round(est_premium * meta["lot_size"], 2)
                
                results.append({
                    "Stock": name,
                    "Spot Price (₹)": round(current_close, 2),
                    "Lot Size": meta["lot_size"],
                    "Recommended OTM": f"{otm_strike} CE",
                    "Est. Premium (₹)": est_premium,
                    "Margin Required": f"₹{capital_needed:,}",
                    "Vol vs Avg": f"{round(current_volume / avg_volume, 1)}x",
                    "RSI": round(rsi, 1),
                    "Signal": action,
                    "Score": score
                })
            except Exception:
                continue
                
        if results:
            res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
            st.dataframe(res_df.style.map(style_signal, subset=['Signal']), use_container_width=True)

    # Dynamic Strategy Guidance
    if results:
        st.markdown("### 🏁 BTST Risk Protocol")
        st.info("💡 **Entry Window:** 3:15 PM - 3:25 PM IST. **Exit Window:** Tomorrow 9:15 AM - 9:30 AM IST.")
