import streamlit as st
import plotly.graph_objects as go
import requests
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="💹 Real-Time Crypto Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- COIN OPTIONS ---
coin_options = {
    "Bitcoin (BTC)": "BTCUSDT",
    "Ethereum (ETH)": "ETHUSDT",
    "Dogecoin (DOGE)": "DOGEUSDT",
    "Litecoin (LTC)": "LTCUSDT"
}

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    selected_label = st.selectbox("Choose a coin to track:", list(coin_options.keys()))
    refresh_interval = st.slider("Refresh Interval (seconds)", 30, 90, 60)

coin_id = coin_options[selected_label]
st.title(f"📈 Real-Time {selected_label} Price Tracker")

# --- GET PRICE FROM BINANCE ---
def get_price(coin_id):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin_id}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        return float(data["price"])
    except Exception as e:
        st.error(f"Failed to fetch price for {coin_id}: {e}")
        return None

# --- SESSION STATE ---
if f"prices_{coin_id}" not in st.session_state:
    st.session_state[f"prices_{coin_id}"] = []
    st.session_state[f"times_{coin_id}"] = []

# --- FETCH AND STORE PRICE ---
price = get_price(coin_id)
if price is not None:
    st.session_state[f"prices_{coin_id}"].append(price)
    st.session_state[f"times_{coin_id}"].append(time.strftime("%H:%M:%S"))

# --- DISPLAY METRIC AND CHART ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if price is not None:
        st.metric(label=f"{selected_label} Price (USD)", value=f"${price}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=st.session_state[f"times_{coin_id}"],
            y=st.session_state[f"prices_{coin_id}"],
            mode='lines+markers',
            line=dict(color='gold'),
            marker=dict(size=8),
            name='Price'
        ))

        fig.update_layout(
            title=f"{selected_label} Price Over Time",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            autosize=True,
            margin=dict(l=20, r=20, t=40, b=20),
        )

        st.plotly_chart(fig, use_container_width=True)

# --- AUTO REFRESH ---
st_autorefresh(interval=refresh_interval * 1000, key="auto_refresh")

# --- FOOTER ---
st.markdown("---")
st.caption("Made using Python + Streamlit + Binance API")
