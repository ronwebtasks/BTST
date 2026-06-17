import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="NSE BTST Screener", page_icon="📈", layout="wide")

st.title("📈 High-Probability NSE BTST Screener")
st.markdown("""
This app scans Indian stocks for **Buy Today, Sell Tomorrow (BTST)** opportunities. 
It targets high-momentum breakouts with institutional volume confirmations during the final hour of trade.
""")

# Default highly liquid Nifty watchlists to prevent settlement auction risk
TICKER_GROUPS = {
    "Nifty 50 Top Liquid": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "LT.NS", "M&M.NS"],
    "High Beta / Momentum": ["TATASTEEL.NS", "ADANIENT.NS", "JSWSTEEL.NS", "HINDALCO.NS", "PFC.NS", "RECL.NS", "AXISBANK.NS"]
}

# Sidebar configuration
st.sidebar.header("Scanner Configurations")
selected_group = st.sidebar.selectbox("Select Watchlist", list(TICKER_GROUPS.keys()))
tickers = TICKER_GROUPS[selected_group]

vol_multiplier = st.sidebar.slider("Min Volume Multiplier (vs 20-day Avg)", 1.0, 3.0, 1.5, 0.1)
rsi_min = st.sidebar.slider("Minimum RSI (14)", 50, 70, 60, 1)
price_near_high_pct = st.sidebar.slider("Max Distance from Day's High (%)", 0.1, 2.0, 0.5, 0.1)

if st.button("🚀 Scan Live Market Data"):
    st.info("Fetching and analyzing data from National Stock Exchange (NSE)... Please wait.")
    
    results = []
    
    for ticker in tickers:
        try:
            # Fetch daily data for 20-day volume average and trend
            stock = yf.Ticker(ticker)
            df_daily = stock.history(period="1mo", interval="1d")
            
            if len(df_daily) < 20:
                continue
                
            # Calculate Daily technicals
            avg_volume = df_daily['Volume'].iloc[-21:-1].mean() # Exclude today
            current_volume = df_daily['Volume'].iloc[-1]
            current_close = df_daily['Close'].iloc[-1]
            current_high = df_daily['High'].iloc[-1]
            current_low = df_daily['Low'].iloc[-1]
            
            # Distance from high criteria
            dist_from_high = ((current_high - current_close) / current_high) * 100
            
            # Simple RSI-14 Calculation
            delta = df_daily['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # High-accuracy condition checks
            vol_condition = current_volume >= (avg_volume * vol_multiplier)
            rsi_condition = current_rsi >= rsi_min
            close_condition = dist_from_high <= price_near_high_pct
            trend_condition = current_close > df_daily['Close'].iloc[-2] # Higher close than yesterday
            
            # Score calculations
            score = 0
            if vol_condition: score += 30
            if rsi_condition: score += 30
            if close_condition: score += 20
            if trend_condition: score += 20
            
            # Determine Action
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
        # Sort by Match Score descending
        res_df = res_df.sort_values(by="Match Score", ascending=False)
        
        # Display styled output
        def style_signal(val):
            if val == "STRONG BUY": return 'background-color: #2ecc71; color: white; font-weight: bold;'
            elif val == "WATCH": return 'background-color: #f1c40f; color: black;'
            return 'background-color: #e74c3c; color: white;'
            
        st.dataframe(res_df.style.applymap(style_signal, subset=['Signal']), use_container_width=True)
        
        # Dynamic advice section
        strong_buys = res_df[res_df['Signal'] == "STRONG BUY"]['Stock'].tolist()
        if strong_buys:
            st.success(f"🔥 **Potential BTST Candidates Found:** {', '.join(strong_buys)}")
            st.markdown("""
            ### 🛠️ How to execute these trades right now:
            1. **Stop Loss (SL):** Set a strict system stop loss at today's day low or **1.5% below entry**, whichever is tighter.
            2. **Target:** Look for an overnight gap up of **2% to 2.5%**. 
            3. **Execution Window:** Enter between **3:15 PM and 3:25 PM** today, and sell tomorrow morning between **9:15 AM and 9:45 AM**.
            """)
        else:
            st.warning("⚠️ No stocks met the strict high-probability BTST criteria right now. Standard advice: Cash is a position. Do not force trades.")
    else:
        st.error("No data fetched. Check your internet connection or ticker symbols.")
