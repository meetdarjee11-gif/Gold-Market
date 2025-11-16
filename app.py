# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

# --- Configuration ---
# Using GLD (SPDR Gold Shares ETF) as a proxy for gold prices
TICKER = 'GLD' 

st.set_page_config(page_title="Gold Market Data App", layout="wide")

st.title("💰 Gold Market Price Tracker")
st.markdown(f"Fetching data for **{TICKER}** using `yfinance`.")

@st.cache_data
def get_historical_data(ticker_symbol, days=365):
    """Fetches historical stock data from yfinance and caches the result."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    try:
        # Download data for the specified time range
        data = yf.download(ticker_symbol, start=start_date, end=end_date)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker_symbol}: {e}")
        return pd.DataFrame()

# Fetch data for the last 1 year
df = get_historical_data(TICKER, days=365)

if not df.empty:
    st.subheader(f"Price Chart for {TICKER}")
    # Display the Closing price over time
    st.line_chart(df['Close'])

    st.subheader("Latest Price and Summary")

    latest_close = df['Close'].iloc[-1]
    previous_close = df['Close'].iloc[-2]

    # Calculate change
    price_change = latest_close - previous_close
    percent_change = (price_change / previous_close) * 100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Latest Close Price", f"${latest_close:.2f}")
    with col2:
        st.metric("Price Change (vs previous day)", f"${price_change:.2f}", f"{percent_change:.2f}%")
    with col3:
        st.metric("Data Period", f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")

    st.subheader("Raw Data Table (Last 10 Days)")
    st.dataframe(df.tail(10)) # Show last 10 rows
else:
    st.warning("Could not load financial data. Check the ticker symbol or your internet connection.")
