import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="NSE Comprehensive BTST Screener", page_icon="⚡", layout="wide")

st.title("⚡ Comprehensive NSE F&O & Cash BTST Multi-Screener")
st.markdown("""
This production scanner covers both **Nifty Top Stocks** and **F&O Derivatives**. 
It strictly targets high-momentum breakout stocks and structures a high-probability **OTM+1 Call Option (CE)** strategy with dynamic Stop-Loss rules.
""")

# Universe 1: Standard Liquid Nifty Stocks (Cash Segment)
NIFTY_200_CASH = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "LT.NS", "M&M.NS",
    "SUNPHARMA.NS", "TATAMOTORS.NS", "AXISBANK.NS", "ASIANPAINT.NS", "HCLTECH.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "COALINDIA.NS", "TITAN.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "JIOFIN.NS", "ADANIENT.NS", "ADANIPORTS.NS", "TATASTEEL.NS", "HINDALCO.NS", 
    "JSWSTEEL.NS", "GRASIM.NS", "LTIM.NS", "TECHM.NS", "WIPRO.NS", "HINDUNILVR.NS", "BRITANNIA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", 
    "APOLLOHOSP.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BPCL.NS", "IOC.NS", "BEL.NS", "HAL.NS", "DLF.NS", "VBL.NS", "ZOMATO.NS", 
    "TRENT.NS", "PIDILITIND.NS", "SIEMENS.NS", "ABB.NS", "INDIGO.NS", "TATACONSUM.NS", "SHRIRAMFIN.NS", "CHOLAFIN.NS", "PFC.NS", "RECL.NS"
]

# Universe 2: Mapped Lot Sizes and Strike Steps for Liquid F&O Counters
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
    "BHARTIARTL": {"symbol": "BHARTIARTL.NS", "lot_size": 950, "strike_step": 10},
    "AARTIIND": {"symbol": "AARTIIND.NS", "lot_size": 1000, "strike_step": 10},
    "ABB": {"symbol": "ABB.NS", "lot_size": 125, "strike_step": 100},
    "ACC": {"symbol": "ACC.NS", "lot_size": 300, "strike_step": 20},
    "AMBUJACEM": {"symbol": "AMBUJACEM.NS", "lot_size": 800, "strike_step": 10},
    "ASHOKLEY": {"symbol": "ASHOKLEY.NS", "lot_size": 2500, "strike_step": 2.5},
    "BHEL": {"symbol": "BHEL.NS", "lot_size": 2625, "strike_step": 2.5},
    "BANKBARODA": {"symbol": "BANKBARODA.NS", "lot_size": 2425, "strike_step": 2.5},
    "CANBK": {"symbol": "CANBK.NS", "lot_size": 2250, "strike_step": 1},
    "COALINDIA": {"symbol": "COALINDIA.NS", "lot_size": 2100, "strike_step": 5},
    "DLF": {"symbol": "DLF.NS", "lot_size": 1650, "strike_step": 10},
    "FEDERALBNK": {"symbol": "FEDERALBNK.NS", "lot_size": 5000, "strike_step": 2.5},
    "GAIL": {"symbol": "GAIL.NS", "lot_size": 4550, "strike_step": 2.5},
    "GMRINFRA": {"symbol": "GMRINFRA.NS", "lot_size": 11250, "strike_step": 1},
    "HINDALCO": {"symbol": "HINDALCO.NS", "lot_size": 1400, "strike_step": 5},
    "ITC": {"symbol": "ITC.NS", "lot_size": 1600, "strike_step": 5},
    "JINDALSTEL": {"symbol": "JINDALSTEL.NS", "lot_size": 1250, "strike_step": 10},
    "LT": {"symbol": "LT.NS", "lot_size": 300, "strike_step": 20},
    "NATIONALUM": {"symbol": "NATIONALUM.NS", "lot_size": 3750, "strike_step": 2.5},
    "NTPC": {"symbol": "NTPC.NS", "lot_size": 1500, "strike_step": 5},
    "ONGC": {"symbol": "ONGC.NS", "lot_size": 3850, "strike_step": 2.5},
    "PNB": {"symbol": "PNB.NS", "lot_size": 4000, "strike_step": 1},
    "POWERGRID": {"symbol": "POWERGRID.NS", "lot_size": 3600, "strike_step": 2.5},
    "SAIL": {"symbol": "SAIL.NS", "lot_size": 4000, "strike_step": 2.5},
    "TATAMOTORS": {"symbol": "TATAMOTORS.NS", "lot_size": 1425, "strike_step": 5},
    "TATAPOWER": {"symbol": "TATAPOWER.NS", "lot_size": 1350, "strike_step": 2.5},
    "VEDL": {"symbol": "VEDL.NS", "lot_size": 2300, "strike_step": 5},
    "WIPRO": {"symbol": "WIPRO.NS", "lot_size": 1500, "strike_step": 2.5}
}

# Sidebar Configurations
st.sidebar.header("🎯 Universe Selection")
scanner_mode = st.sidebar.selectbox("Choose Target Segment", ["Nifty Top Stocks (Cash)", "F&O Option Sizer (OTM+1 Only)"])

st.sidebar.header("Momentum Configurations")
vol_multiplier = st.sidebar.slider("Min Volume Multiplier", 1.0, 3.0, 1.5, 0.1)
rsi_min = st.sidebar.slider("Minimum RSI", 50, 70, 60, 1)
price_near_high_pct = st.sidebar.slider("Max Distance from Day High (%)", 0.1, 2.0, 0.5, 0.1)

def style_signal(val):
    if val == "STRONG BUY": return 'background-color: #2ecc71; color: white; font-weight: bold;'
    elif val == "WATCH": return 'background-color: #f1c40f; color: black;'
    return 'background-color: #e74c3c; color: white;'

if st.button("🚀 Run Live BTST Scan"):
    results = []
    
    if scanner_mode == "Nifty Top Stocks (Cash)":
        st.info(f"Scanning {len(NIFTY_200_CASH)} cash stocks... Please wait.")
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
                
                results.append({
                    "Stock": ticker.replace(".NS", ""),
                    "Close (₹)": round(current_close, 2),
                    "Vol Multiplier": f"{round(current_volume / avg_volume, 1)}x",
                    "RSI (14)": round(rsi, 1),
                    "Dist from High": f"{round(dist_from_high, 2)}%",
                    "Score": score,
                    "Signal": action
                })
            except Exception: continue
                
        if results:
            res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
            st.dataframe(res_df.style.map(style_signal, subset=['Signal']), use_container_width=True)
            
    else:
        st.info(f"Scanning F&O chains and sizing optimal **OTM+1** contracts... Please wait.")
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
                
                # STRICT OTM+1 Strike Calculator
                atm_strike = round(current_close / meta["strike_step"]) * meta["strike_step"]
                otm_1_strike = int(atm_strike + meta["strike_step"]) if current_close >= atm_strike else int(atm_strike)
                if otm_1_strike <= current_close: 
                    otm_1_strike += int(meta["strike_step"])
                
                # Premium & Stop Loss Sizer Math
                est_premium = round(current_close * 0.016, 2)
                capital_needed = round(est_premium * meta["lot_size"], 2)
                strict_premium_sl = round(est_premium * 0.75, 2) # Strict 25% Stop-loss on option price
                
                results.append({
                    "Stock": name,
                    "Spot (₹)": round(current_close, 2),
                    "Lot Size": meta["lot_size"],
