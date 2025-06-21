from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, function_tool
from dotenv import load_dotenv
import os
import requests
import asyncio

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

# Function to run the agent (used in Streamlit)
def run_crypto_agent(user_input):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            Runner.run(crypto_agent, input=user_input, run_config=config)
        ).final_output
    finally:
        loop.close()

