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

# Expansive Universe 2: Over 140+ active F&O stocks with mapped Lot Sizes and Strike Increments
FANDO_OPTIONS = {
    "AARTIIND": {"symbol": "AARTIIND.NS", "lot_size": 1000, "strike_step": 10},
    "ABB": {"symbol": "ABB.NS", "lot_size": 125, "strike_step": 100},
    "ABBOTINDIA": {"symbol": "ABBOTINDIA.NS", "lot_size": 20, "strike_step": 200},
    "ABCAPITAL": {"symbol": "ABCAPITAL.NS", "lot_size": 2700, "strike_step": 2.5},
    "ABFRL": {"symbol": "ABFRL.NS", "lot_size": 1300, "strike_step": 5},
    "ACC": {"symbol": "ACC.NS", "lot_size": 300, "strike_step": 20},
    "ADANIENT": {"symbol": "ADANIENT.NS", "lot_size": 300, "strike_step": 50},
    "ADANIPORTS": {"symbol": "ADANIPORTS.NS", "lot_size": 400, "strike_step": 20},
    "ALKEM": {"symbol": "ALKEM.NS", "lot_size": 100, "strike_step": 100},
    "AMBUJACEM": {"symbol": "AMBUJACEM.NS", "lot_size": 800, "strike_step": 10},
    "APOLLOHOSP": {"symbol": "APOLLOHOSP.NS", "lot_size": 125, "strike_step": 100},
    "APOLLOTYRE": {"symbol": "APOLLOTYRE.NS", "lot_size": 1700, "strike_step": 5},
    "ASHOKLEY": {"symbol": "ASHOKLEY.NS", "lot_size": 2500, "strike_step": 2.5},
    "ASIANPAINT": {"symbol": "ASIANPAINT.NS", "lot_size": 200, "strike_step": 20},
    "ASTRAL": {"symbol": "ASTRAL.NS", "lot_size": 361, "strike_step": 20},
    "ATUL": {"symbol": "ATUL.NS", "lot_size": 75, "strike_step": 100},
    "AUBANK": {"symbol": "AUBANK.NS", "lot_size": 1000, "strike_step": 10},
    "AUROPHARMA": {"symbol": "AUROPHARMA.NS", "lot_size": 550, "strike_step": 10},
    "AXISBANK": {"symbol": "AXISBANK.NS", "lot_size": 625, "strike_step": 10},
    "BAJAJ-AUTO": {"symbol": "BAJAJ-AUTO.NS", "lot_size": 125, "strike_step": 100},
    "BAJAJFINSV": {"symbol": "BAJAJFINSV.NS", "lot_size": 500, "strike_step": 20},
    "BAJFINANCE": {"symbol": "BAJFINANCE.NS", "lot_size": 125, "strike_step": 100},
    "BALRAMCHIN": {"symbol": "BALRAMCHIN.NS", "lot_size": 1600, "strike_step": 5},
    "BANDHANBNK": {"symbol": "BANDHANBNK.NS", "lot_size": 2500, "strike_step": 2.5},
    "BANKBARODA": {"symbol": "BANKBARODA.NS", "lot_size": 2425, "strike_step": 2.5},
    "BATAINDIA": {"symbol": "BATAINDIA.NS", "lot_size": 375, "strike_step": 20},
    "BEL": {"symbol": "BEL.NS", "lot_size": 2850, "strike_step": 2.5},
    "BERGEPAINT": {"symbol": "BERGEPAINT.NS", "lot_size": 1100, "strike_step": 5},
    "BHARATFORG": {"symbol": "BHARATFORG.NS", "lot_size": 500, "strike_step": 20},
    "BHARTIARTL": {"symbol": "BHARTIARTL.NS", "lot_size": 950, "strike_step": 10},
    "BHEL": {"symbol": "BHEL.NS", "lot_size": 2625, "strike_step": 2.5},
    "BIOCON": {"symbol": "BIOCON.NS", "lot_size": 1600, "strike_step": 5},
    "BOSCHLTD": {"symbol": "BOSCHLTD.NS", "lot_size": 20, "strike_step": 200},
    "BPCL": {"symbol": "BPCL.NS", "lot_size": 1800, "strike_step": 5},
    "BRITANNIA": {"symbol": "BRITANNIA.NS", "lot_size": 200, "strike_step": 50},
    "BSOFT": {"symbol": "BSOFT.NS", "lot_size": 1000, "strike_step": 10},
    "CANFINHOME": {"symbol": "CANFINHOME.NS", "lot_size": 975, "strike_step": 10},
    "CANBK": {"symbol": "CANBK.NS", "lot_size": 2250, "strike_step": 1},
    "CHAMBLFERT": {"symbol": "CHAMBLFERT.NS", "lot_size": 1900, "strike_step": 5},
    "CHOLAFIN": {"symbol": "CHOLAFIN.NS", "lot_size": 625, "strike_step": 20},
    "CIPLA": {"symbol": "CIPLA.NS", "lot_size": 650, "strike_step": 10},
    "COALINDIA": {"symbol": "COALINDIA.NS", "lot_size": 2100, "strike_step": 5},
    "COFORGE": {"symbol": "COFORGE.NS", "lot_size": 150, "strike_step": 100},
    "COLPAL": {"symbol": "COLPAL.NS", "lot_size": 350, "strike_step": 20},
    "CONCOR": {"symbol": "CONCOR.NS", "lot_size": 1000, "strike_step": 10},
    "COROMANDEL": {"symbol": "COROMANDEL.NS", "lot_size": 700, "strike_step": 20},
    "CROMPTON": {"symbol": "CROMPTON.NS", "lot_size": 1800, "strike_step": 5},
    "CUMMINSIND": {"symbol": "CUMMINSIND.NS", "lot_size": 300, "strike_step": 20},
    "DABUR": {"symbol": "DABUR.NS", "lot_size": 1250, "strike_step": 5},
    "DALBHARAT": {"symbol": "DALBHARAT.NS", "lot_size": 250, "strike_step": 20},
    "DEEPAKNTR": {"symbol": "DEEPAKNTR.NS", "lot_size": 300, "strike_step": 20},
    "DELTACORP": {"symbol": "DELTACORP.NS", "lot_size": 3000, "strike_step": 2.5},
    "DIVISLAB": {"symbol": "DIVISLAB.NS", "lot_size": 200, "strike_step": 50},
    "DIXON": {"symbol": "DIXON.NS", "lot_size": 100, "strike_step": 100},
    "DLF": {"symbol": "DLF.NS", "lot_size": 1650, "strike_step": 10},
    "DRREDDY": {"symbol": "DRREDDY.NS", "lot_size": 125, "strike_step": 50},
    "EICHERMOT": {"symbol": "EICHERMOT.NS", "lot_size": 175, "strike_step": 50},
    "ESCORTS": {"symbol": "ESCORTS.NS", "lot_size": 275, "strike_step": 50},
    "EXIDEIND": {"symbol": "EXIDEIND.NS", "lot_size": 1800, "strike_step": 5},
    "FEDERALBNK": {"symbol": "FEDERALBNK.NS", "lot_size": 5000, "strike_step": 2.5},
    "GAIL": {"symbol": "GAIL.NS", "lot_size": 4550, "strike_step": 2.5},
    "GLENMARK": {"symbol": "GLENMARK.NS", "lot_size": 725, "strike_step": 10},
    "GMRINFRA": {"symbol": "GMRINFRA.NS", "lot_size": 11250, "strike_step": 1},
    "GNFC": {"symbol": "GNFC.NS", "lot_size": 1300, "strike_step": 10},
    "GODREJCP": {"symbol": "GODREJCP.NS", "lot_size": 500, "strike_step": 10},
    "GODREJPROP": {"symbol": "GODREJPROP.NS", "lot_size": 325, "strike_step": 20},
    "GRANULES": {"symbol": "GRANULES.NS", "lot_size": 2000, "strike_step": 5},
    "GRASIM": {"symbol": "GRASIM.NS", "lot_size": 250, "strike_step": 20},
    "GUJGASLTD": {"symbol": "GUJGASLTD.NS", "lot_size": 1250, "strike_step": 10},
    "HAL": {"symbol": "HAL.NS", "lot_size": 300, "strike_step": 20},
    "HAVELLS": {"symbol": "HAVELLS.NS", "lot_size": 500, "strike_step": 20},
    "HCLTECH": {"symbol": "HCLTECH.NS", "lot_size": 700, "strike_step": 10},
    "HDFCBANK": {"symbol": "HDFCBANK.NS", "lot_size": 550, "strike_step": 10},
    "HDFCLIFE": {"symbol": "HDFCLIFE.NS", "lot_size": 1100, "strike_step": 5},
    "HEROMOTOCO": {"symbol": "HEROMOTOCO.NS", "lot_size": 150, "strike_step": 50},
    "HINDALCO": {"symbol": "HINDALCO.NS", "lot_size": 1400, "strike_step": 5},
    "HINDCOPPER": {"symbol": "HINDCOPPER.NS", "lot_size": 2800, "strike_step": 5},
    "HINDPETRO": {"symbol": "HINDPETRO.NS", "lot_size": 1350, "strike_step": 5},
    "HINDUNILVR": {"symbol": "HINDUNILVR.NS", "lot_size": 300, "strike_step": 20},
    "ICICIBANK": {"symbol": "ICICIBANK.NS", "lot_size": 700, "strike_step": 5},
    "ICICIGI": {"symbol": "ICICIGI.NS", "lot_size": 500, "strike_step": 20},
    "ICICIPRULI": {"symbol": "ICICIPRULI.NS", "lot_size": 1500, "strike_step": 10},
    "IDEA": {"symbol": "IDEA.NS", "lot_size": 40000, "strike_step": 0.5},
    "IDFCFIRSTB": {"symbol": "IDFCFIRSTB.NS", "lot_size": 7500, "strike_step": 1},
    "IEX": {"symbol": "IEX.NS", "lot_size": 3750, "strike_step": 2.5},
    "IGL": {"symbol": "IGL.NS", "lot_size": 1375, "strike_step": 5},
    "INDHOTEL": {"symbol": "INDHOTEL.NS", "lot_size": 1000, "strike_step": 5},
    "INDIACEM": {"symbol": "INDIACEM.NS", "lot_size": 2900, "strike_step": 2.5},
    "INDIAMART": {"symbol": "INDIAMART.NS", "lot_size": 150, "strike_step": 50},
    "INDIGO": {"symbol": "INDIGO.NS", "lot_size": 150, "strike_step": 50},
    "INDUSINDBK": {"symbol": "INDUSINDBK.NS", "lot_size": 500, "strike_step": 10},
    "INDUSTOWER": {"symbol": "INDUSTOWER.NS", "lot_size": 1700, "strike_step": 5},
    "INFY": {"symbol": "INFY.NS", "lot_size": 400, "strike_step": 10},
    "IOC": {"symbol": "IOC.NS", "lot_size": 3375, "strike_step": 2.5},
    "IPCALAB": {"symbol": "IPCALAB.NS", "lot_size": 650, "strike_step": 10},
    "IRCTC": {"symbol": "IRCTC.NS", "lot_size": 875, "strike_step": 10},
    "ITC": {"symbol": "ITC.NS", "lot_size": 1600, "strike_step": 5},
    "JINDALSTEL": {"symbol": "JINDALSTEL.NS", "lot_size": 1250, "strike_step": 10},
    "JKCEMENT": {"symbol": "JKCEMENT.NS", "lot_size": 250, "strike_step": 50},
    "JSWSTEEL": {"symbol": "JSWSTEEL.NS", "lot_size": 675, "strike_step": 10},
    "JUBLFOOD": {"symbol": "JUBLFOOD.NS", "lot_size": 1250, "strike_step": 5},
    "KOTAKBANK": {"symbol": "KOTAKBANK.NS", "lot_size": 400, "strike_step": 20},
    "L&TFH": {"symbol": "L&TFH.NS", "lot_size": 4444, "strike_step": 2.5},
    "LALPATHLAB": {"symbol": "LALPATHLAB.NS", "lot_size": 300, "strike_step": 50},
    "LICHSGFIN": {"symbol": "LICHSGFIN.NS", "lot_size": 1000, "strike_step": 10},
    "LT": {"symbol": "LT.NS", "lot_size": 300, "strike_step": 20},
    "LTIM": {"symbol": "LTIM.NS", "lot_size": 150, "strike_step": 50},
"LTTS": {"symbol": "LTTS.NS", "lot_size": 200, "strike_step": 50},
"LUPIN": {"symbol": "LUPIN.NS", "lot_size": 400, "strike_step": 10},
"M&M": {"symbol": "M&M.NS", "lot_size": 350, "strike_step": 20},
"M&MFIN": {"symbol": "M&MFIN.NS", "lot_size": 2000, "strike_step": 5},
"MANAPPURAM": {"symbol": "MANAPPURAM.NS", "lot_size": 3000, "strike_step": 2.5},
"MARUTI": {"symbol": "MARUTI.NS", "lot_size": 50, "strike_step": 100},
"MCDOWELL-N": {"symbol": "MCDOWELL-N.NS", "lot_size": 700, "strike_step": 10},
"MCX": {"symbol": "MCX.NS", "lot_size": 400, "strike_step": 20},
"METROPOLIS": {"symbol": "METROPOLIS.NS", "lot_size": 400, "strike_step": 20},
"MFSL": {"symbol": "MFSL.NS", "lot_size": 800, "strike_step": 10},
"MGL": {"symbol": "MGL.NS", "lot_size": 400, "strike_step": 20},
"MOTHERSON": {"symbol": "MOTHERSON.NS", "lot_size": 3400, "strike_step": 2.5},
"MPHASIS": {"symbol": "MPHASIS.NS", "lot_size": 275, "strike_step": 20},
"MRF": {"symbol": "MRF.NS", "lot_size": 10, "strike_step": 500},
"MUTHOOTFIN": {"symbol": "MUTHOOTFIN.NS", "lot_size": 550, "strike_step": 20},
"NATIONALUM": {"symbol": "NATIONALUM.NS", "lot_size": 3750, "strike_step": 2.5},
"NAVINFLUOR": {"symbol": "NAVINFLUOR.NS", "lot_size": 175, "strike_step": 50},
"NESTLEIND": {"symbol": "NESTLEIND.NS", "lot_size": 200, "strike_step": 10},
"NMDC": {"symbol": "NMDC.NS", "lot_size": 4500, "strike_step": 2.5},
"NTPC": {"symbol": "NTPC.NS", "lot_size": 1500, "strike_step": 5},
"OBEROIRLTY": {"symbol": "OBEROIRLTY.NS", "lot_size": 300, "strike_step": 20},
"ONGC": {"symbol": "ONGC.NS", "lot_size": 3850, "strike_step": 2.5},
"PAGEIND": {"symbol": "PAGEIND.NS", "lot_size": 15, "strike_step": 250},
"PEL": {"symbol": "PEL.NS", "lot_size": 750, "strike_step": 10},
"PERSISTENT": {"symbol": "PERSISTENT.NS", "lot_size": 175, "strike_step": 20},
"PETRONET": {"symbol": "PETRONET.NS", "lot_size": 3000, "strike_step": 5},
"PFC": {"symbol": "PFC.NS", "lot_size": 3750, "strike_step": 2.5},
"PIDILITIND": {"symbol": "PIDILITIND.NS", "lot_size": 250, "strike_step": 20},
"PIIND": {"symbol": "PIIND.NS", "lot_size": 250, "strike_step": 50},
"PNB": {"symbol": "PNB.NS", "lot_size": 4000, "strike_step": 1},
"POLYCAB": {"symbol": "POLYCAB.NS", "lot_size": 150, "strike_step": 50},
"POWERGRID": {"symbol": "POWERGRID.NS", "lot_size": 3600, "strike_step": 2.5},
"PVRINOX": {"symbol": "PVRINOX.NS", "lot_size": 407, "strike_step": 20},
"RAMCOCEM": {"symbol": "RAMCOCEM.NS", "lot_size": 850, "strike_step": 10},
"RBLBANK": {"symbol": "RBLBANK.NS", "lot_size": 2500, "strike_step": 5},
"RECL": {"symbol": "RECL.NS", "lot_size": 2000, "strike_step": 2.5},
"RELIANCE": {"symbol": "RELIANCE.NS", "lot_size": 250, "strike_step": 20},
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
