import streamlit as st
import requests
import json
from pathlib import Path

# Get the absolute path of the project root
ROOT = Path(__file__).parent.parent.parent

# Load channel data
try:
    with open(ROOT / "data" / "Unergy.json", "r") as f:
        unergy_channels = json.load(f)
    with open(ROOT / "data" / "TheSunFactory.json", "r") as f:
        the_sun_factory_channels = json.load(f)
except FileNotFoundError:
    st.error(
        "Error: Channel data JSON files not found. Make sure 'Unergy.json' and 'TheSunFactory.json' are in the 'data/' directory."
    )
    unergy_channels = {}
    the_sun_factory_channels = {}

st.set_page_config(page_title="Dulcinea Agent Tester", layout="centered")
st.title("Dulcinea Agent Tester")

# Server selection
guild_names = ["Unergy", "The_Sun_Factory"]
selected_guild = st.selectbox("Select Discord Server:", guild_names)

# Dynamically load channels based on selected server
if selected_guild == "Unergy":
    channels = list(unergy_channels.keys())
else:
    channels = list(the_sun_factory_channels.keys())

if not channels:
    st.warning(f"No channels found for {selected_guild}.")
    selected_channel = None
else:
    selected_channel = st.selectbox("Select Channel:", channels)

# Query input
query = st.text_area("Enter your query:", height=150)

if st.button("Get Agent Response"):
    if selected_guild and selected_channel and query:
        st.info("Fetching response from agent...")
        api_url = "http://localhost:8000/dulcinea"  # Assuming FastAPI is running on localhost:8000
        headers = {"Content-Type": "application/json"}
        payload = {
            "query": query,
            "guild_name": selected_guild,
            "channel_name": selected_channel,
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors

            agent_response = response.json()
            if "result" in agent_response:
                st.subheader("Agent Response:")
                st.markdown(agent_response["result"])
            else:
                st.error("Unexpected response format from agent.")
                st.json(agent_response)

        except requests.exceptions.ConnectionError:
            st.error(
                "Error: Could not connect to the FastAPI agent. Please ensure the agent is running at http://localhost:8000."
            )
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e}")
            st.write(f"Response content: {response.text}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please select a server, channel, and enter a query.")
