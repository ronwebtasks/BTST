import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="NSE BTST Screener", page_icon="📈", layout="wide")

st.title("📈 High-Probability NSE BTST & F&O Screener")
st.markdown("""
This app scans Indian stocks for **Buy Today, Sell Tomorrow (BTST)** opportunities. 
It targets high-momentum breakouts with institutional volume confirmations during the final hour of trade.
""")

# Organized watchlists including the highly liquid F&O stocks segment
TICKER_GROUPS = {
    "Nifty 50 Heavyweights": [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", 
        "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "LT.NS", "M&M.NS"
    ],
    "F&O Liquid Movers (High Momentum)": [
        "ADANIENT.NS", "ADANIPORTS.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS",
        "BEL.NS", "COALINDIA.NS", "DLF.NS", "GMRINFRA.NS", "HAL.NS", 
        "HINDALCO.NS", "JSWSTEEL.NS", "NTPC.NS", "ONGC.NS", "PFC.NS", 
        "RECL.NS", "SAIL.NS", "SUNPHARMA.NS", "TATASTEEL.NS", "TRENT.NS"
    ]
}

# Sidebar configuration dropdown menus
st.sidebar.header("Scanner Configurations")
selected_group = st.sidebar.selectbox("🎯 Select Stock Universe", list(TICKER_GROUPS.keys()))
tickers = TICKER_GROUPS[selected_group]

# Advanced structural filters
vol_multiplier = st.sidebar.slider("Min Volume Multiplier (vs 20-day Avg)", 1.0, 3.0, 1.5, 0.1)
rsi_min = st.sidebar.slider("Minimum RSI (14)", 50, 70, 60, 1)
price_near_high_pct = st.sidebar.slider("Max Distance from Day's High (%)", 0.1, 2.0, 0.5, 0.1)

if st.button("🚀 Scan Live Market Data"):
    st.info(f"Fetching and analyzing live data for {len(tickers)} stocks from the National Stock Exchange (NSE)... Please wait.")
    
    results = []
    
    for ticker in tickers:
        try:
            # Fetch daily historical records for calculating 20-day parameters
            stock = yf.Ticker(ticker)
            df_daily = stock.history(period="1mo", interval="1d")
            
            if len(df_daily) < 20:
                continue
                
            # Extract daily candle properties
            avg_volume = df_daily['Volume'].iloc[-21:-1].mean()  # Preceding 20 trading sessions
            current_volume = df_daily['Volume'].iloc[-1]
            current_close = df_daily['Close'].iloc[-1]
            current_high = df_daily['High'].iloc[-1]
            
            # Percentage distance away from intraday high
            dist_from_high = ((current_high - current_close) / current_high) * 100
            
            # Calculate standard Relative Strength Index (RSI-14)
            delta = df_daily['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Algorithmic conditions checklist
            vol_condition = current_volume >= (avg_volume * vol_multiplier)
            rsi_condition = current_rsi >= rsi_min
            close_condition = dist_from_high <= price_near_high_pct
            trend_condition = current_close > df_daily['Close'].iloc[-2]  # Positive close delta
            
            # Confluence metric builder
            score = 0
            if vol_condition: score += 30
            if rsi_condition: score += 30
            if close_condition: score += 20
            if trend_condition: score += 20
            
            # Assign final visual state label
            action = "STRONG BUY" if score >= 80 else "WATCH" if score >= 50 else "AVOID"
            
            results.append({
                "Stock": ticker.replace(".NS", ""),
                "Close Price (₹)": round(current_close, 2),
                "Vol vs Avg": f"{round(current_volume / avg_volume, 2)}x",
                "RSI (14)": round(current_rsi, 2),
                "Dist from High (%)": f"{round(dist_from_high, 2)}%",
                "Match Score": f"{score}/100",
                "Signal": action
            })
            
        except Exception as e:
            st.warning(f"Could not process {ticker}: {str(e)}")
            
    if results:
        res_df = pd.DataFrame(results)
        res_df = res_df.sort_values(by="Match Score", ascending=False)
        
        # Color coding renderer for dashboard UI clarity
        def style_signal(val):
            if val == "STRONG BUY": return 'background-color: #2ecc71; color: white; font-weight: bold;'
            elif val == "WATCH": return 'background-color: #f1c40f; color: black;'
            return 'background-color: #e74c3c; color: white;'
            
        st.dataframe(res_df.style.map(style_signal, subset=['Signal']), use_container_width=True)
        
        # Action planning terminal
        strong_buys = res_df[res_df['Signal'] == "STRONG BUY"]['Stock'].tolist()
        if strong_buys:
            st.success(f"🔥 **Potential F&O BTST Breakout Candidates:** {', '.join(strong_buys)}")
            st.markdown("""
            ### 🛠️ Execution Protocol for F&O Stocks:
            *   **Capital Advantage:** Since these are F&O-eligible counters, you can alternative-trade them in the cash market or buy their near-the-money Options/Futures to compound gains if liquidity permits.
            *   **Risk Mitigation:** F&O counters move rapidly overnight based on global sentiment. Maintain a tight stop loss at **1% below entry** or right below the 3:00 PM candle breakout low.
            *   **Target Exit:** Book profits mechanically during morning price discoveries (**9:15 AM to 9:30 AM IST**).
            """)
        else:
            st.warning("⚠️ No stocks met the strict high-probability BTST breakout criteria inside this cluster right now.")
    else:
        st.error("Data error encountered. Please check your active terminal configurations.")
