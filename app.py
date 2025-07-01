import streamlit as st
import plotly.graph_objects as go
import requests
import time
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import json

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
    selected_coins = st.multiselect(
        "💹 Select coins to compare:",
        options=list(coin_options.keys()),
        default=["Bitcoin (BTC)", "Ethereum (ETH)"]
    )
    refresh_interval = st.slider("Refresh Interval (seconds)", 30, 90, 60)
    show_converter = st.checkbox("💱 Show INR Equivalent")
    show_history = st.checkbox("🗕️ Show 7-Day History")

coin_id = coin_options[selected_label]
cg_id = coingecko_ids[coin_id]

# --- SESSION STATE INIT ---
if f"prices_{coin_id}" not in st.session_state:
    st.session_state[f"prices_{coin_id}"] = []
if f"times_{coin_id}" not in st.session_state:
    st.session_state[f"times_{coin_id}"] = []

st.title(f"📈 Real-Time {selected_label} Price Tracker")

# --- LIVE PRICE FUNCTION ---
def get_price_and_change(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if coin_id not in data:
            st.error("⚠️ CoinGecko did not return valid data.")
            st.json(data)
            return None, None
        return float(data[coin_id]['usd']), float(data[coin_id]['usd_24h_change'])
    except Exception as e:
        st.error(f"💥 Error fetching data: {e}")
        return None, None

# --- COMPARISON TABLE ---
coin_data = []
for label in selected_coins:
    coin_id_loop = coin_options[label]
    cg_id_loop = coingecko_ids[coin_id_loop]
    price, change = get_price_and_change(cg_id_loop)
    if price is not None:
        coin_data.append({"label": label, "price": price, "change": change})

if coin_data:
    df = pd.DataFrame(coin_data)
    df["Price (USD)"] = df["price"].map(lambda x: f"${x:.2f}")
    df["24h Change (%)"] = df["change"].map(lambda x: f"{x:.2f}%")
    df = df[["label", "Price (USD)", "24h Change (%)"]]
    df.columns = ["Coin", "Price (USD)", "24h Change (%)"]

    st.subheader("📊 Coin Comparison")
    st.dataframe(df)

    st.download_button(
        label="⬇️ Download Data as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="crypto_data.csv",
        mime='text/csv'
    )

# --- MULTICOIN LIVE CHART ---
fig = go.Figure()
alert_threshold = 5
for coin in coin_data:
    label = coin["label"]
    coin_id_loop = coin_options[label]
    if f"prices_{coin_id_loop}" not in st.session_state:
        st.session_state[f"prices_{coin_id_loop}"] = []
        st.session_state[f"times_{coin_id_loop}"] = []
    st.session_state[f"prices_{coin_id_loop}"].append(coin["price"])
    st.session_state[f"times_{coin_id_loop}"].append(time.strftime("%H:%M:%S"))
    fig.add_trace(go.Scatter(
        x=st.session_state[f"times_{coin_id_loop}"],
        y=st.session_state[f"prices_{coin_id_loop}"],
        mode='lines+markers',
        name=label
    ))
    if abs(coin['change']) >= alert_threshold:
        st.warning(f"🚨 {coin['label']} is on the move! 24h change: {coin['change']:.2f}%")

fig.update_layout(
    title="📈 Multi-Coin Price Comparison",
    xaxis_title="Time",
    yaxis_title="Price (USD)",
    template="plotly_dark",
    margin=dict(l=20, r=20, t=40, b=20),
)
st.plotly_chart(fig, use_container_width=True)

# --- SINGLE COIN HISTORY ---
def get_7_day_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "daily"}
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if "prices" not in data:
            st.error("⚠️ CoinGecko did not return price history.")
            st.json(data)
            return [], []
        prices = data["prices"]
        dates = [time.strftime("%b %d", time.gmtime(p[0] / 1000)) for p in prices]
        values = [p[1] for p in prices]
        return dates, values
    except Exception as e:
        st.error(f"💥 Error fetching 7-day history: {e}")
        return [], []

# --- FETCH & DISPLAY SELECTED COIN ---
price, percent_change = get_price_and_change(cg_id)
if price is not None:
    st.session_state[f"prices_{coin_id}"].append(price)
    st.session_state[f"times_{coin_id}"].append(time.strftime("%H:%M:%S"))

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(
            label=f"{selected_label} Price (USD)",
            value=f"${price:.2f}",
            delta=f"{percent_change:.2f}%",
            delta_color="normal" if percent_change == 0 else ("inverse" if percent_change < 0 else "off")
        )
        if show_converter:
            st.write(f"💸 INR Equivalent: ₹ {price * 83.2:.2f}")
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

# --- HISTORY CHART ---
if show_history:
    st.subheader("🗕️ 7-Day Price History")
    history_dates, history_prices = get_7_day_history(cg_id)
    if history_prices:
        fig_history = go.Figure()
        fig_history.add_trace(go.Scatter(
            x=history_dates,
            y=history_prices,
            mode='lines+markers',
            line=dict(color='deepskyblue'),
            marker=dict(size=6),
            name='7-Day History'
        ))
        fig_history.update_layout(
            title=f"{selected_label} - Last 7 Days",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_history, use_container_width=True)
        
# --- CRYPTO NEWS SECTION WITH FALLBACK ---
def get_crypto_news():
    url = "https://cryptonews-api.com/api/v1?tickers=BTC,ETH,DOGE,LTC&items=5&token=YOUR_REAL_API_KEY"

    try:
        res = requests.get(url, timeout=10)
        clean_text = res.text.strip().split("\n")[0]
        data = json.loads(clean_text)

        if "data" in data and isinstance(data["data"], list):
            return data["data"]
        else:
            return FALLBACK_NEWS
    except Exception as e:
        st.warning(f"💥 Couldn't fetch live news. Showing fallback.")
        return FALLBACK_NEWS

FALLBACK_NEWS = [
    {
        "title": "Welcome to Your Crypto Dashboard! 🚀",
        "news_url": "#",
        "source_name": "CryptoBot",
        "date": time.strftime("%Y-%m-%d"),
        "description": "Your dashboard is live — more news will appear here when available."
    },
    {
        "title": "Pro Tip: Check Volume & Volatility Next!",
        "news_url": "#",
        "source_name": "Dashboard Guide",
        "date": time.strftime("%Y-%m-%d"),
        "description": "Traders often watch volume spikes to catch big moves."
    }
]

# --- DISPLAY NEWS ---
st.markdown("---")
st.subheader("📰 Latest Crypto News")

news_items = get_crypto_news()

if news_items:
    for article in news_items:
        title = article.get("title", "No Title")
        link = article.get("news_url", "#")
        source = article.get("source_name", "Unknown Source")
        date = article.get("date", "Unknown Date")
        description = article.get("description", "")

        st.markdown(
            f'<a href="{link}" target="_blank" style="text-decoration: none; color: #1f77b4;"><strong>🔗 {title}</strong></a>',
            unsafe_allow_html=True
        )
        st.caption(f"{source} – {date}")
        if description:
            st.write(description)
else:
    st.info("No news found at the moment.")

# --- AUTO REFRESH ---
st_autorefresh(interval=refresh_interval * 1000, key="auto_refresh")

# --- FOOTER ---
st.markdown("---")
st.caption("Made using Python + Streamlit + CoinGecko API")
