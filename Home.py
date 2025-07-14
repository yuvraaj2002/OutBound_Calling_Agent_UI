import streamlit as st
import requests
import json
import tempfile
import os
from datetime import datetime
from audio_recorder_streamlit import audio_recorder
from src.openai_service import OpenAIService
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.agent_config import *
from langchain_core.messages import SystemMessage, HumanMessage
import time
from rich import print

# Force wide mode
st.set_page_config(
    page_title="Inbound Calling Agent",
    page_icon="📞",
    layout="wide",  
    initial_sidebar_state="collapsed"
)
openai_service = OpenAIService()

# Additional CSS to ensure wide mode
st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    max-width: 90%;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
                .top-margin{
                    margin-top: 4rem;
                    margin-bottom:2rem;
                }
                .block-button{
                    padding: 10px; 
                    width: 100%;
                    background-color: #c4fcce;
                }
                /* Force wide layout */
                .main .block-container {
                    max-width: 100%;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)

def make_call(phone_number):
    status = []
    try:

        status.append(("✅ Completed pre-call configurations", "success"))
        time.sleep(1)

        payload = {
            "phone_number": phone_number,
            "wait_for_greeting": False,
            "block_interruptions": False,
            "interruption_threshold": 70,
            "pathway_id": "56818c1b-a21b-44dd-ba6b-a54844569d12",
            "model": "base",
            "temperature": 0.7,
            "language": "en",   
            "ignore_button_press": False,
            "record": True,
            "voice": "june",  # Default voice for OHC Pharmacy
        }
        
        # Make the API call to BlandAI
        headers = {
            "authorization": st.secrets.get("BLANDAI_API_KEY"),
            "Content-Type": "application/json"
        }
        response = requests.request("POST", "https://api.bland.ai/v1/calls", json=payload, headers=headers)
        response.raise_for_status()
        
        # Parse the response from BlandAI
        response_data = response.json()
        call_id = response_data.get("call_id")
        if call_id:
            status.append(("✅ Inbound call initialized successfully", "success"))
        
    except Exception as e:
        status.append((f"Error in make_call: {e}", "error"))
    return status

def reset_validation():
    st.session_state['call_validated'] = False

st.title("Inbound Calling Agent 📞")
st.markdown("""
This application simulates an inbound calling system for OHC Pharmacy. When you initiate a call, our AI agent will behave as if you have called OHC Pharmacy and will assist you with your pharmacy-related inquiries.

**How it works:**
- **Step 1:** Enter your phone number in the proper E.164 format (e.g., +12345678901 for US numbers).
- **Step 2:** Click "Initiate Call" to start the inbound call simulation.
- **Step 3:** The AI agent will answer as an OHC Pharmacy representative and assist you with your questions.

**E.164 Format Requirements:**
- Must start with a "+" sign
- Include country code (e.g., +1 for US, +44 for UK)
- Include area code and phone number
- No spaces, dashes, or parentheses
- Example: +12345678901 (US), +447911123456 (UK)

Get started by entering your phone number below!
""")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### ⚙️ Call Configuration")
    
    # Phone Number Input with E.164 format validation
    phone_number = st.text_input(
        "Your Phone Number (E.164 Format)", 
        placeholder="+12345678901", 
        help="Enter your phone number in E.164 format (e.g., +12345678901 for US numbers)",
        on_change=reset_validation
    )

    # Creating button for call initiation
    if st.button("🚀 Initiate Inbound Call", type="primary", use_container_width=True):
        # Validation checks
        if not phone_number:
            st.error("❌ Please enter your phone number")
            st.stop()
        if not phone_number.startswith("+"):
            st.error("❌ Phone number must start with a + (E.164 format)")
            st.stop()
        if len(phone_number) < 10 or len(phone_number) > 15:
            st.error("❌ Phone number must be between 10-15 digits")
            st.stop()
        
        # Only call make_call if all validations pass
        call_status = make_call(phone_number)
        st.session_state['call_status'] = call_status

with col2:
    st.markdown("### 📊 Call Status")
    st.info("Enter your phone number in the left panel to initiate an inbound call to OHC Pharmacy.")
    
    # Show post-validation success messages from make_call
    if 'call_status' in st.session_state:
        for msg, msg_type in st.session_state['call_status']:
            if msg_type == 'success':
                st.success(msg)
            elif msg_type == 'error':
                st.error(msg)
            elif msg_type == 'info':
                st.info(msg)

st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)