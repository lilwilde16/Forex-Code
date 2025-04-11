import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- Currency and Pair Settings ---
currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']
pairs = ['EURJPY', 'GBPUSD', 'USDCHF', 'AUDJPY', 'NZDCAD']

# --- Simulate Currency Strength ---
def simulate_strength():
    return {cur: random.randint(20, 90) for cur in currencies}

# --- Simulate BB Breakout ---
def simulate_bb_breakout():
    return random.choice([0, 1, 2, 3])  # 1–3 means breakout

# --- Get Trading Session (EST) ---
def get_session():
    hour = datetime.utcnow().hour - 5  # Convert UTC to EST
    if 2 <= hour < 5:
        return "London"
    elif 8 <= hour < 11:
        return "New York"
    return "OFF"

# --- Generate Setup Logic ---
def generate_setups(strength):
    session = get_session()
    valid = []

    for pair in pairs:
        base, quote = pair[:3], pair[3:]
        if base in strength and quote in strength:
            base_val, quote_val = strength[base], strength[quote]
            bb = simulate_bb_breakout()

            if base_val >= 70 and quote_val <= 30 and bb >= 1 and session != "OFF":
                valid.append({
                    "Pair": pair,
                    "Signal": "CALL",
                    "Strength": f"{base} {base_val}% / {quote} {quote_val}%",
                    "BB Status": f"{bb}x BB Close 🔼",
                    "Expiry": "1M" if bb == 1 else "2M"
                })
            elif quote_val >= 70 and base_val <= 30 and bb >= 1 and session != "OFF":
                valid.append({
                    "Pair": pair,
                    "Signal": "PUT",
                    "Strength": f"{base} {base_val}% / {quote} {quote_val}%",
                    "BB Status": f"{bb}x BB Close 🔽",
                    "Expiry": "1M" if bb == 1 else "2M"
                })
    return valid

# --- Streamlit App Layout ---
st.set_page_config(page_title="Pocket Options Sniper", layout="centered")
st.title("🎯 Pocket Options Sniper Dashboard")

st.markdown("""
This dashboard shows **only** high-probability sniper setups:
- ✅ Strong vs Weak currencies
- ✅ BB(10,1) breakout (1–3 candles)
- ✅ Active sessions only (London or NY)
""")

st.markdown("---")
session = get_session()
st.markdown(f"**Current Session:** `{session}`")
st.markdown(f"**Last Updated:** `{datetime.now().strftime('%I:%M:%S %p')}`")

strength_data = simulate_strength()
setups = generate_setups(strength_data)

if setups:
    df = pd.DataFrame(setups)
    st.success(f"📈 {len(setups)} sniper setup(s) found!")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No valid sniper setups right now. Come back during session hours or after new candles.")
