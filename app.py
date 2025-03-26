import requests
import pandas as pd
import streamlit as st

API_URL = "https://api.hyperliquid.xyz/info"

def fetch_all_state():
    try:
        response = requests.post(API_URL, json={"type": "allStateLite"})
        response.raise_for_status()
        data = response.json()
        return data["universe"]
    except Exception as e:
        st.error(f"Error fetching asset state: {e}")
        return []

def process_asset_data(data):
    records = []
    for item in data:
        asset = item.get("name")
        mid_price = float(item.get("mid", 0))
        oi = float(item.get("openInterest", 0))
        funding = float(item.get("fundingRate", 0))
        long_weight = float(item.get("longWeight", 0))
        short_weight = float(item.get("shortWeight", 0))

        records.append({
            "asset": asset,
            "mid_price": mid_price,
            "open_interest": oi,
            "funding_rate": funding,
            "long_weight": long_weight,
            "short_weight": short_weight
        })
    return pd.DataFrame(records)

st.set_page_config(page_title="Hyperliquid Market Overview", layout="wide")
st.title("📊 Hyperliquid Market Signal Tracker")

with st.spinner("Fetching live market state..."):
    data = fetch_all_state()

if data:
    df = process_asset_data(data)
    selected = st.multiselect("Select Assets", options=df["asset"].unique(), default=["ETH", "BTC", "ARB", "PENDLE"])
    df_filtered = df[df["asset"].isin(selected)]

    st.subheader("🔍 Asset Stats")
    st.dataframe(df_filtered.sort_values("open_interest", ascending=False), use_container_width=True)

    st.subheader("📈 Funding Rate vs Open Interest")
    st.bar_chart(df_filtered.set_index("asset")[["funding_rate", "open_interest"]])
else:
    st.warning("No data received.")
