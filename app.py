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

coingecko_ids = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "DOGEUSDT": "dogecoin",
    "LTCUSDT": "litecoin"
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    st.subheader("📊 Live Coin Selection")

    selected_label = st.selectbox("Choose a coin to track:", list(coin_options.keys()))
    refresh_interval = st.slider("Refresh Interval (seconds)", 30, 90, 60)
    show_converter = st.checkbox("💱 Show INR Equivalent")
    show_history = st.checkbox("📅 Show 7-Day History")

# --- SET COIN IDs ---
coin_id = coin_options[selected_label]
cg_id = coingecko_ids[coin_id]

st.title(f"📈 Real-Time {selected_label} Price Tracker")

# --- PRICE FUNCTION ---
def get_price_and_change(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        if coin_id not in data:
            st.error("⚠️ CoinGecko did not return valid data.")
            st.json(data)
            return None, None

        current_price = float(data[coin_id]['usd'])
        percent_change = float(data[coin_id]['usd_24h_change'])
        return current_price, percent_change

    except Exception as e:
        st.error(f"💥 Error fetching data: {e}")
        return None, None

# --- SESSION STATE ---
if f"prices_{coin_id}" not in st.session_state:
    st.session_state[f"prices_{coin_id}"] = []
    st.session_state[f"times_{coin_id}"] = []

# --- FETCH LIVE DATA ---
price, percent_change = get_price_and_change(cg_id)
if price is not None:
    st.session_state[f"prices_{coin_id}"].append(price)
    st.session_state[f"times_{coin_id}"].append(time.strftime("%H:%M:%S"))

# --- DISPLAY ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if price is not None:
        st.metric(
            label=f"{selected_label} Price (USD)",
            value=f"${price:.2f}",
            delta=f"{percent_change:.2f}%",
            delta_color="normal" if percent_change == 0 else ("inverse" if percent_change < 0 else "off")
        )

        if show_converter:
            st.write(f"💸 INR Equivalent: ₹ {price * 83.2:.2f}")

        # Chart
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
st.caption("Made using Python + Streamlit + CoinGecko API")
