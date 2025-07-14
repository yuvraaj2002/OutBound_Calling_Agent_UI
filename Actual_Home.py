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
    page_title="Calling Agent",
    page_icon="🚀",
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

def make_call(tag_type,contact_name,phone_number,agent_name,voice_id,creativity_level):
    status = []
    try:
        agent_prompt = None
        # Getting the Prompt Against the Tag Type
        if tag_type == "CGM":
            agent_prompt = cgm_outreach_prompt.format(agent_name=agent_name, contact_name=contact_name)
        elif tag_type == "CPAP":
            agent_prompt = cpap_prompt.format(agent_name=agent_name, contact_name=contact_name)
        elif tag_type == "Weight Loss":
            agent_prompt = weight_loss_prompt.format(agent_name=agent_name, contact_name=contact_name)
        elif tag_type == "Wheelchair" or tag_type == "Walker" or tag_type == "Crutches" or tag_type == "Canes":
            agent_prompt = wheelchair_walker_crutches_canes_prompt.format(agent_name=agent_name, contact_name=contact_name)
        elif tag_type == "Briefs":
            agent_prompt = briefs_prompt.format(agent_name=agent_name, contact_name=contact_name)
        elif tag_type == "Compression":
            agent_prompt = compression_prompt.format(agent_name=agent_name, contact_name=contact_name)
        elif tag_type == "Orthopedic Shoes":
            agent_prompt = orthopedic_shoes_prompt.format(agent_name=agent_name, contact_name=contact_name)
        elif tag_type == "Diabetic Shoes":
            agent_prompt = diabetic_shoes_prompt.format(agent_name=agent_name, contact_name=contact_name)
        elif tag_type == "General DME":
            agent_prompt = general_dme_prompt.format(agent_name=agent_name, contact_name=contact_name)
        
        status.append(("✅ Successfully retrieved the agent prompt", "success"))
        time.sleep(1)

        status.append(("✅ Completed pre-call configurations", "success"))
        time.sleep(1)

        payload = {
            "phone_number": phone_number,
            "task": agent_prompt,
            "wait_for_greeting": True,
            "block_interruptions": False,
            "interruption_threshold": 70,
            "model": "base",
            "temperature": creativity_level,
            "language": "en",   
            "ignore_button_press": False,
            "record": True,
            "voice": voice_id,
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
            status.append(("✅ Call initialized successfully", "success"))
        
    except Exception as e:
        status.append((f"Error in make_call: {e}", "error"))
    return status

def reset_validation():
    st.session_state['call_validated'] = False

st.title("Outbound Calling Agent📞")
st.markdown("""
This application empowers you to automate and personalize outbound calls for your pharmacy or healthcare organization. Easily configure your call parameters, select the agent persona, and record or upload your call instructions—all in one place.

**How it works:**
- **Step 1:** Select the type of call (e.g., CGM, CPAP, Weight Loss, etc.) and choose your preferred AI agent voice and creativity level.
- **Step 2:** Enter the recipient's name and phone number in the required format.
- **Step 3:** Save time and reduce manual effort for routine outreach.
- **Step 4:** Ensure every call is consistent, compliant, and tailored to your patient's needs.

Get started by configuring your call settings on the left, and record your instructions below. Your next outbound call is just a few clicks away!
""")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### ⚙️ Call Configuration")
    
    # Tag Type Dropdown
    tag_type_options = [
        "CGM", "CPAP", "Weight Loss", "Wheelchair", "Walker", "Crutches", 
        "Canes", "Briefs", "Compression", "Orthopedic Shoes", "Diabetic Shoes", "General DME"
    ]
    selected_tag_type = st.selectbox("Select Tag Type", tag_type_options, on_change=reset_validation)
    
    # Agent Type Dropdown
    agent_type_options = ["Ava (Female)","Olivia (Female)", "Sophia (Female)","Grace (Female)","David (Male)"]
    agent_name = st.selectbox("Select Agent Type", agent_type_options, on_change=reset_validation)
    voice_id = get_voice_id(agent_name)
    
    # Agent Creativity Slider
    creativity_level = st.slider("Agent Creativity Level", min_value=0.0, max_value=1.0, value=0.5, step=0.1, 
                                help="Higher values make the agent more creative and flexible in responses", on_change=reset_validation)
    
    # Contact Name Input
    contact_name = st.text_input("Contact Name", placeholder="Enter the contact's name", on_change=reset_validation)
    
    # Phone Number Input
    phone_number = st.text_input("Phone Number", placeholder="Enter the phone number with E164 format (e.g., +12345678901 for US)", on_change=reset_validation)

    # Creating button for call initiation
    if st.button("🚀 Initiate Call", type="primary", use_container_width=True):
        # Validation checks
        if not phone_number or not selected_tag_type or not agent_name or not creativity_level or not contact_name:
            st.error("❌ Please fill in all fields")
            st.stop()
        if not phone_number.startswith("+"):
            st.error("❌ Phone number must start with a +")
            st.stop()
        if len(phone_number) < 10 or len(phone_number) > 15:
            st.error("❌ Phone number must be between 10-15 digits")
            st.stop()
        # Only call make_call if all validations pass
        call_status = make_call(selected_tag_type, contact_name, phone_number, agent_name, voice_id, creativity_level)
        st.session_state['call_status'] = call_status

with col2:
    st.markdown("### 📊 Call Status")
    st.info("Configure your call settings in the left panel and record your voice instructions below.")
    
    # Show post-validation success messages from make_call
    if 'call_status' in st.session_state:
        for msg, msg_type in st.session_state['call_status']:
            if msg_type == 'success':
                st.success(msg)
            elif msg_type == 'error':
                st.error(msg)
            elif msg_type == 'info':
                st.info(msg)

# Audio section - Independent of columns
st.markdown("---")
st.markdown("# 🎤 Speech to Text Agent")
st.success(
    """
    **How to use:**
    - Click the microphone button below to start recording your voice instructions.
    - Speak clearly and state your call objectives or any message you want transcribed.
    - This feature is for testing only. Once you stop speaking for a few seconds, the recording will automatically stop and your audio will be processed.
    - After recording, you can listen to your audio and view the transcription below.
    """
)

with st.container(border=True):
    # Audio recording using audio-recorder-streamlit
    audio_bytes = audio_recorder(
        text="Click to record your call instructions",
        recording_color="#e74c3c",
        neutral_color="#6c757d",
        icon_name="microphone",
        icon_size="2x"
    )

if audio_bytes:
    st.session_state['audio_bytes'] = audio_bytes
    st.success("✅ Audio recorded successfully!")
    
    # Save recorded audio to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_file_path = tmp_file.name
    
    # Display audio player
    if 'audio_bytes' in st.session_state:
        st.audio(st.session_state['audio_bytes'], format="audio/wav")
    
    # Process button
    if st.button("🚀 Process Audio", type="primary", use_container_width=True):
        with st.spinner("Processing your audio..."):
            try:
                # Extracting the transcription from the .wav audio file
                transcription = openai_service.transcribe_audio(audio_file=open(tmp_file_path, "rb"))
                st.session_state['transcription'] = transcription
                
                st.markdown("### 📋 Transcription")
                st.write(transcription)
                st.markdown("<br><br>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error processing audio: {str(e)}")
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
    # Add padding below the button
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

# if __name__ == "__main__":
#     selected_tag_type = "CGM"
#     phone_number = "+916239305919"
#     agent_name = "Olivia"
#     voice_id = get_voice_id(agent_name)
#     creativity_level = 0.5
#     make_call(selected_tag_type, phone_number, agent_name, voice_id, creativity_level)