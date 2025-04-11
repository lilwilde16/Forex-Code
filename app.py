import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

def calculate_forex_profit_supreme(prices_data, pairs, currencies, period=60):
    """
    For each currency pair:
      - Computes the pip change (current close minus close from 'period' days ago),
        scaled by 10,000 to approximate pip movement.
      - If a currency appears as the base (the first three characters of the pair symbol),
        its raw value is increased; if it appears as the quote (characters 3–6),
        its raw value is decreased.
    
    After processing all pairs, the raw values for each currency are normalized to a 0–100 scale.
    
    The overall pair percentage is then calculated as:
        (Normalized(Base) - Normalized(Quote) + 100) / 2
    
    Returns:
        normalized_values: dict mapping each currency to its normalized strength (0-100)
        pair_percents: dict mapping each forex pair to its computed percentage (0-100)
    """
    raw_values = {currency: 0.0 for currency in currencies}
    scaling_factor = 10000

    for symbol in pairs:
        price_array = prices_data.get(symbol)
        if price_array is None or len(price_array) < period + 1:
            continue

        # Compute the pip change: difference between the latest close and the close 'period' days ago.
        pips = price_array[-1] - price_array[-(period + 1)]
        pip_change = pips * scaling_factor

        # If currency is base (first 3 letters), add; if quote (letters 3-6), subtract.
        for cur in currencies:
            if symbol.startswith(cur):
                raw_values[cur] += pip_change
            elif symbol[3:6] == cur:
                raw_values[cur] -= pip_change

    # Normalize the raw values to a 0–100 scale.
    vals = list(raw_values.values())
    if vals:
        min_val, max_val = min(vals), max(vals)
    else:
        min_val, max_val = 0, 0

    normalized_values = {}
    if max_val == min_val:
        for cur in currencies:
            normalized_values[cur] = 50.0
    else:
        for cur in currencies:
            normalized_values[cur] = (raw_values[cur] - min_val) / (max_val - min_val) * 100

    # Calculate the pair percentages using the formula:
    # (Normalized(Base) - Normalized(Quote) + 100) / 2
    pair_percents = {}
    for symbol in pairs:
        base = symbol[:3]
        quote = symbol[3:6]
        if base in normalized_values and quote in normalized_values:
            pair_percents[symbol] = (normalized_values[base] - normalized_values[quote] + 100) / 2.0

    return normalized_values, pair_percents

def fetch_real_data(period_data="1y", interval="1d"):
    """
    Downloads real forex data from Yahoo Finance using the specified period and interval.
    
    Returns:
        prices_data: dict mapping each forex pair symbol (Yahoo Finance format) to its numpy array of closing prices.
        pairs: list of forex pair symbols.
        currencies: list of individual 3-letter currency codes.
    """
    currencies = ["USD", "EUR", "GBP", "CHF", "JPY", "CAD", "AUD", "NZD"]
    pairs = [
        "EURUSD=X", "GBPUSD=X", "USDCHF=X", "USDJPY=X",
        "AUDUSD=X", "NZDUSD=X", "EURJPY=X", "GBPJPY=X"
    ]
    
    # Download data via yfinance.
    df = yf.download(tickers=pairs, period=period_data, interval=interval,
                     group_by='ticker', progress=False)
    prices_data = {}
    for symbol in pairs:
        try:
            # When downloading multiple symbols, df is a dict-like structure
            close_prices = df[symbol]['Close'].to_numpy()
        except Exception:
            # If grouping by ticker doesn't work, fallback to the default 'Close' column.
            close_prices = df['Close'].to_numpy()
        prices_data[symbol] = close_prices

    return prices_data, pairs, currencies

def main():
    st.title("ForexProfitSupreme Meter")
    st.markdown("This app calculates individual currency strengths and pair percentages based on recent forex data from Yahoo Finance.")
    
    if st.button("Refresh"):
        with st.spinner("Fetching data and calculating metrics..."):
            # Fetch real data
            prices_data, pairs, currencies = fetch_real_data(period_data="1y", interval="1d")
            # Calculate currency strengths and pair percentages.
            normalized_values, pair_percents = calculate_forex_profit_supreme(prices_data, pairs, currencies, period=60)
        
        st.subheader("Currency Strengths (0-100)")
        for cur in currencies:
            st.write(f"**{cur}**: {normalized_values.get(cur, 0):.2f}")
        
        st.subheader("Pair Percentages (0-100)")
        for sym in pairs:
            st.write(f"**{sym}**: {pair_percents.get(sym, 0):.2f}")
    else:
        st.write("Press the **Refresh** button to fetch data and calculate the Forex meter metrics.")

if __name__ == "__main__":
    main()