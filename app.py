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

# ✅ COINGECKO MAPPING (only if needed for CoinGecko features)
coingecko_ids = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "DOGEUSDT": "dogecoin",
    "LTCUSDT": "litecoin"
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    st.subheader("📊 Live Coin Selection")  # 💡 Here!
    
    selected_label = st.selectbox("Choose a coin to track:", list(coin_options.keys()))
    refresh_interval = st.slider("Refresh Interval (seconds)", 30, 90, 60)

    # ✅ Currency Converter toggle (INR)
    show_converter = st.checkbox("💱 Show INR Equivalent")

    # ✅ History Chart toggle
    show_history = st.checkbox("📅 Show 7-Day History")
   
# --- SET COIN IDs ---
coin_id = coin_options[selected_label]
cg_id = coingecko_ids[coin_id]  # 💋 this is the new line

st.title(f"📈 Real-Time {selected_label} Price Tracker")

# --- FUNCTION TO FETCH PRICE + CHANGE ---
# --- FUNCTION TO FETCH PRICE, CHANGE, HIGH, LOW, VOLUME ---
def get_price_and_change(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        # 💥 Show full data if something goes wrong
        if 'market_data' not in data:
            st.error("⚠️ CoinGecko did not return market data. Full response:")
            st.json(data)
            return None, None, None, None, None

        current_price = float(data['market_data']['current_price']['usd'])
        percent_change = float(data['market_data']['price_change_percentage_24h'])
        high = float(data['market_data']['high_24h']['usd'])
        low = float(data['market_data']['low_24h']['usd'])
        volume = float(data['market_data']['total_volume']['usd'])

        return current_price, percent_change, high, low, volume

    except Exception as e:
        st.error(f" Error fetching data from CoinGecko: {e}")
        return None, None, None, None, None


    
price, percent_change, high, low, volume = get_price_and_change(cg_id)

# --- SESSION STATE ---
if f"prices_{coin_id}" not in st.session_state:
    st.session_state[f"prices_{coin_id}"] = []
    st.session_state[f"times_{coin_id}"] = []

# --- FETCH LIVE DATA ---
price, percent_change, high, low, volume = get_price_and_change(coin_id)
if price is not None:
    st.session_state[f"prices_{coin_id}"].append(price)
    st.session_state[f"times_{coin_id}"].append(time.strftime("%H:%M:%S"))

# --- DISPLAY METRIC & CHART ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if price is not None:
        st.metric(
            label=f"{selected_label} Price (USD)",
            value=f"${price:.2f}",
            delta=f"{percent_change:.2f}%",
            delta_color="normal" if percent_change == 0 else ("inverse" if percent_change < 0 else "off")
        )

        # ✅ Show INR equivalent
        if show_converter:
            st.write(f"💸 INR Equivalent: ₹ {price * 83.2:.2f}")

        # ✅ Volume + High/Low Stats
        st.markdown(f"**🔼 24H High:** ${high}")
        st.markdown(f"**🔽 24H Low:** ${low}")
        st.markdown(f"📊 **Volume:** {volume}")

        # --- Chart ---
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
