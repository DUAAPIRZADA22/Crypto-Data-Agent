import streamlit as st
from main import run_crypto_agent

st.set_page_config(page_title="💰 Live Crypto Prices", page_icon="💸", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Quicksand', sans-serif;
        background-color: #0f172a;
        color: #f1f5f9;
    }

    .title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        color: #f472b6;
        margin-bottom: 2rem;
    }

    .card {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 2px 4px 12px rgba(0,0,0,0.2);
        color: #f8fafc;
    }

    .footer {
        margin-top: 3rem;
        text-align: center;
        font-size: 0.9rem;
        color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">💰 Live Crypto Prices</div>', unsafe_allow_html=True)

top_coins = {
    "Bitcoin (BTC)": "BTC",
    "Ethereum (ETH)": "ETH",
    "Dogecoin (DOGE)": "DOGE",
    "Solana (SOL)": "SOL",
    "Ripple (XRP)": "XRP",
    "Litecoin (LTC)": "LTC"
}

selected = st.multiselect("🔽 Select one or more cryptocurrencies", options=list(top_coins.keys()))

if st.button("Show Prices"):
    if selected:
        with st.spinner("Fetching prices..."):
            for coin_name in selected:
                symbol = top_coins[coin_name]
                prompt = f"Get me the live price of {symbol}"
                result = run_crypto_agent(prompt)
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)
    else:
        st.warning("Please select at least one coin.")

st.markdown('<div class="footer">Developed with 💖 by Duaa Pirzada</div>', unsafe_allow_html=True)



