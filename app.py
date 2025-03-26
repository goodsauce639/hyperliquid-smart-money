import requests
import pandas as pd
from datetime import datetime
import streamlit as st

API_URL = "https://api.hyperliquid.xyz/info"

def fetch_top_traders(n=20):
    try:
        response = requests.post(API_URL, json={"type": "leaderboard", "n": n})
        response.raise_for_status()
        data = response.json()
        return [entry['username'] for entry in data['traders']]
    except Exception as e:
        st.error(f"Error fetching top traders: {e}")
        return []

def fetch_user_positions(username):
    try:
        payload = {"type": "userState", "user": username}
        r = requests.post(API_URL, json=payload)
        r.raise_for_status()
        data = r.json()
        results = []
        for pos in data.get("assetPositions", []):
            szi = float(pos["position"]["szi"])
            entry_px = float(pos["position"]["entryPx"])
            results.append({
                "username": username,
                "asset": pos["asset"],
                "side": "LONG" if szi > 0 else "SHORT",
                "size": abs(szi),
                "entry_price": entry_px,
                "uPnL": float(pos["position"]["uPnL"]),
                "timestamp": datetime.utcnow()
            })
        return results
    except Exception as e:
        st.warning(f"Error fetching user {username} positions: {e}")
        return []

def fetch_all_positions(n=20):
    top_traders = fetch_top_traders(n)
    all_data = []
    for user in top_traders:
        positions = fetch_user_positions(user)
        all_data.extend(positions)
    return pd.DataFrame(all_data)

st.set_page_config(page_title="Hyperliquid Smart Money Tracker", layout="wide")
st.title("🧠 Hyperliquid Smart Money Tracker")

num_traders = st.slider("Number of Top Traders to Track", 5, 50, 20)
selected_asset = st.text_input("Filter by Asset (e.g., ETH, ARB, PENDLE):", "")

with st.spinner("Fetching data from Hyperliquid..."):
    df = fetch_all_positions(num_traders)

if selected_asset:
    df = df[df["asset"].str.upper() == selected_asset.upper()]

st.subheader("Top Trader Positions")
st.dataframe(df.sort_values("uPnL", ascending=False), use_container_width=True)

if not df.empty:
    st.subheader("🔍 Position Stats")
    long_count = (df["side"] == "LONG").sum()
    short_count = (df["side"] == "SHORT").sum()
    total = long_count + short_count

    st.metric("LONG Positions", f"{long_count} ({long_count/total:.1%})")
    st.metric("SHORT Positions", f"{short_count} ({short_count/total:.1%})")

    long_uPnl = df[df["side"] == "LONG"]["uPnL"].sum()
    short_uPnl = df[df["side"] == "SHORT"]["uPnL"].sum()

    st.metric("LONG uPnL", f"${long_uPnl:,.2f}")
    st.metric("SHORT uPnL", f"${short_uPnl:,.2f}")
else:
    st.warning("No positions found for this asset.")
