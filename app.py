import streamlit as st
import matplotlib.pyplot as plt
import requests
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="💹 Real-Time Crypto Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

coin_options = {
    "Bitcoin (BTC)": "BTCUSDT",
    "Ethereum (ETH)": "ETHUSDT",
    "Dogecoin (DOGE)": "DOGEUSDT",
    "Litecoin (LTC)": "LTCUSDT"
}


# In sidebar
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    selected_label = st.selectbox("Choose a coin to track:", list(coin_options.keys()))
    refresh_interval = st.slider("Refresh Interval (seconds)", 30, 90, 60)


coin_id = coin_options[selected_label]

st.title(f"📈 Real-Time {selected_label} Price Tracker")
# Function to get BTC price
def get_price(coin_id):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin_id}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        st.write("🔍 API Response:", data)  # optional debug
        return float(data["price"])
    except Exception as e:
        st.error(f"Failed to fetch price for {coin_id}: {e}")
        return None



# Session State to store data
if f"prices_{coin_id}" not in st.session_state:
    st.session_state[f"prices_{coin_id}"] = []
    st.session_state[f"times_{coin_id}"] = []

price = get_price(coin_id)
if price is not None:
    st.session_state[f"prices_{coin_id}"].append(price)
    st.session_state[f"times_{coin_id}"].append(time.strftime("%H:%M:%S"))

# --- DISPLAY PRICE + GRAPH ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if price is not None:
        st.metric(label=f"{selected_label} Price (USD)", value=f"${price}")

        fig, ax = plt.subplots()
        ax.plot(
            st.session_state[f"times_{coin_id}"],
            st.session_state[f"prices_{coin_id}"],
            color='gold', marker='o'
        )
        ax.set_xlabel("Time")
        ax.set_ylabel("Price (USD)")
        ax.set_title(f"{selected_label} Price Over Time")
        plt.xticks(rotation=45)
        st.pyplot(fig)
# Auto-refresh every 10 seconds (10000 ms)
st_autorefresh(interval=refresh_interval * 1000, key="auto_refresh")

st.markdown("---")
st.caption("Made with 💖 by My Sweetheart using Python + Streamlit + CoinGecko API")
