# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

# --- Configuration ---
TICKER = 'GLD'  # SPDR Gold Shares ETF (A common gold proxy)

st.set_page_config(page_title="Gold Market Data App", layout="wide")

st.title("💰 Gold Market Price Tracker")
st.markdown(f"Fetching data for **{TICKER}** using `yfinance`.")

@st.cache_data
def get_historical_data(ticker_symbol, days=365):
    """Fetches historical stock data from yfinance and caches the result."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    try:
        # Download data, using adjusted close prices
        data = yf.download(ticker_symbol, start=start_date, end=end_date, auto_adjust=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker_symbol}: {e}")
        return pd.DataFrame()

# Fetch data
df = get_historical_data(TICKER, days=365)

if not df.empty:
    st.subheader(f"Price Chart for {TICKER}")
    st.line_chart(df['Close'])

    st.subheader("Latest Price and Summary")

    # Filter the 'Close' column to ensure only valid, non-NaN prices are used
    valid_closes = df['Close'].dropna()

    if len(valid_closes) >= 2:
        # Get the latest and previous valid closing price
        latest_close = valid_closes.iloc[-1]
        previous_close = valid_closes.iloc[-2]
        
        # --- CRITICAL FIX FOR TYPEERROR ---
        # Explicitly check if the latest price is a number before attempting formatting.
        if isinstance(latest_close, (int, float, pd.Series, pd.DataFrame)) and not isinstance(latest_close, (pd.Series, pd.DataFrame)):
            
            # Calculate change
            price_change = latest_close - previous_close
            percent_change = (price_change / previous_close) * 100

            col1, col2, col3 = st.columns(3)

            with col1:
                # This line is now safe due to the explicit numeric check
                st.metric("Latest Close Price", f"${latest_close:.2f}")
            with col2:
                st.metric("Price Change (vs previous day)", f"${price_change:.2f}", f"{percent_change:.2f}%")
            with col3:
                st.metric("Data Period", f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")

            st.subheader("Raw Data Table (Last 10 Days)")
            st.dataframe(df.tail(10)) 
        else:
            st.warning(f"The latest close price ({latest_close}) is not a valid number. Cannot display metrics.")
            st.dataframe(df)

    else:
        st.warning("Not enough valid closing price data available (need at least 2 days) to calculate metrics.")
        st.dataframe(df)
        
else:
    st.error("Could not load financial data. Please check the ticker symbol or the data source.")
