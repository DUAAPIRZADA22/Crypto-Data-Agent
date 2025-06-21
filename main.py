import streamlit as st
import os
import requests
import asyncio
from dotenv import load_dotenv

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, function_tool

# Load API key from .env
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Set up Gemini-compatible client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Gemini model setup
model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=external_client
)

# Agent run configuration
config = RunConfig(
    model=model,
    tracing_disabled=True
)

# Tool to get crypto price from CoinLore API
@function_tool
def get_crypto_price(symbol: str) -> str:
    """
    Gets live crypto price for a given symbol like BTC, ETH.
    """
    try:
        url = "https://api.coinlore.net/api/tickers/"
        response = requests.get(url)
        coins = response.json()["data"]

        for coin in coins:
            if coin["symbol"].upper() == symbol.upper():
                return f"""
### {coin['name']} ({coin['symbol']})
💲 **Price:** `${coin['price_usd']}`
📈 **Change (24h):** `{coin['percent_change_24h']}%`
🔢 **Market Cap:** `${float(coin['market_cap_usd']):,.2f}`
📊 **Volume (24h):** `${float(coin['volume24']):,.2f}`
"""
        return f"❌ Symbol '{symbol}' not found. Try BTC, ETH, etc."
    
    except Exception as e:
        return f"❌ Error fetching data: {str(e)}"

# Define the agent
crypto_agent = Agent(
    name="CryptoDataAgent",
    instructions="You are a crypto assistant. When user mentions a symbol like BTC, ETH, etc., always use the get_crypto_price tool to fetch live price from CoinLore API. Do not ask questions — just provide data.",
    tools=[get_crypto_price]
)

# Function to run the agent
def run_crypto_agent(user_input):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            Runner.run(crypto_agent, input=user_input, run_config=config)
        ).final_output
    finally:
        loop.close()

# ----------------- Streamlit UI --------------------

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


