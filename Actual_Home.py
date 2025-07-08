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
from system_prompts import payload_extraction_prompt
from langchain_core.messages import SystemMessage, HumanMessage

# Force wide mode
st.set_page_config(
    page_title="Calling Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

openai_service = OpenAIService()

st.title("Outbound Calling Agent📞")
st.markdown("""
**Welcome to the Outbound BlandAI Voice Calling Workflow.** Choose your input method:
- **Voice Command**: Record your call objectives and talking points using the microphone
- **File Upload**: Upload a document with call details for automatic processing
The system will extract structured instructions and initiate personalized AI-powered calls.
""")

col1, col2 = st.columns(2, gap="large")

with col1:
    # Streamlit dropdown to select the Audio record or file upload
    audio_option = st.selectbox("Select the suitable option", ["Voice command", "File upload"])
    if audio_option == "Voice command":
        
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
            if st.button("🚀 Initialize Processing", type="primary", use_container_width=True):
                with st.spinner("Processing your audio..."):
                    try:
                        # Extracting the transcription from the .wav audio file
                        transcription = openai_service.transcribe_audio(audio_file=open(tmp_file_path, "rb"))
                        st.session_state['transcription'] = transcription
                        
                        with col2:
                            st.markdown("### 📋 Transcription")
                            st.write(transcription)
                            st.markdown("### 🔍 Voice Agent Instructions")
                            
                            with st.spinner():

                                # Building the ChatPromptTemplate
                                formatted_prompt = payload_extraction_prompt.format(transcript=transcription)
                                messages = [
                                    SystemMessage(content=formatted_prompt),
                                    HumanMessage(content="Extract the key information from the transcript")
                                ]
                                
                                # Initialize ChatOpenAI with the API key from secrets
                                llm = ChatOpenAI(
                                    api_key=st.secrets.get("OPENAI_API_KEY"),
                                    model="gpt-4o-mini",
                                    temperature=0
                                )
                                
                                # Get the response using LangChain ChatOpenAI Model
                                response = llm.invoke(messages)
                                payload = response.content
                                st.session_state['payload'] = payload
                                
                                # If payload is a string, parse it
                                if isinstance(payload, str):
                                    try:
                                        payload = json.loads(payload)
                                    except Exception as e:
                                        st.error(f"Failed to parse payload as JSON: {e}")
                                        payload = {}

                                if isinstance(payload, dict):
                                    table_data = {
                                        "Parameters": list(payload.keys()),
                                        "Values": list(payload.values())
                                    }
                                    st.table(table_data)
                                else:
                                    st.warning("Payload is not a dictionary.")

                                # Validate required fields
                                required_fields = ["agent_persona", "objective", "contact_name", "phone_number"]
                                missing_fields = []
                                present_fields = []
                                
                                for field in required_fields:
                                    field_value = payload.get(field, "").strip()
                                    if not field_value:
                                        missing_fields.append(field)
                                    else:
                                        present_fields.append(field)
                                
                                # Show validation results
                                if missing_fields:
                                    st.error(f"❌ Missing required fields: {', '.join(missing_fields)}")
                                    if present_fields:
                                        st.info(f"✅ Present fields: {', '.join(present_fields)}")
                                else:
                                    # FastAPI backend endpoint to initiate the call (Post request with the payload)
                                    url = f"https://{st.secrets.get('BASE_URL')}/api/initiate_call"
                                    
                                    # Use st.secrets for BlandAI API key
                                    blandai_api_key = st.secrets.get("BLANDAI_API_KEY")
                                    if not blandai_api_key:
                                        st.error("❌ BLANDAI_API_KEY not found in Streamlit secrets")
                                    else:
                                        headers = {
                                            "Authorization": st.secrets.get("BLANDAI_API_KEY"),
                                            "Content-Type": "application/json"
                                        }
                                        
                                        call_payload = {
                                            "agent_persona": payload.get("agent_persona", ""),
                                            "objective": payload.get("objective", ""),
                                            "contact_name": payload.get("contact_name", ""),
                                            "agent_name": "linda",
                                            "phone_number": payload.get("phone_number", "")
                                        }
                                        
                                        response = requests.post(url, json=call_payload, headers=headers)
                                        
                                        # Check if the request was successful
                                        if response.status_code == 200:
                                            response_json = response.json()
                                            st.success("✅ Call initiated successfully!")
                                        else:
                                            st.error(f"❌ Failed to initiate call. Status code: {response.status_code}")
                                            st.write(f"Error: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Error processing audio: {str(e)}")
                    finally:
                        # Clean up temporary file
                        if os.path.exists(tmp_file_path):
                            os.unlink(tmp_file_path)
    else:
        # Only allow csv,xls, xlsx file
        uploaded_file = st.file_uploader("Upload an audio file", type=["csv", "xls", "xlsx"])
        if uploaded_file:
            pass

            # Getting the credential of the file such as total rows, columns, etc.
            with st.container(border=True):
                
                # Read the uploaded file based on its type
                if uploaded_file.name.endswith('.csv'):
                    import pandas as pd
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xls') or uploaded_file.name.endswith('.xlsx'):
                    import pandas as pd
                    df = pd.read_excel(uploaded_file)
                
                # Calculate file credentials
                total_rows = len(df)
                total_columns = len(df.columns)
                missing_values = df.isnull().sum().sum()
                duplicate_rows = df.duplicated().sum()

                with col2:
                
                    # Display file credentials in a structured format
                    st.markdown("## 📋 File Credentials")
                    file_credentials_col1, file_credentials_col2 = st.columns(2)
                    
                    with file_credentials_col1:
                        st.metric("📊 Total Rows", total_rows)
                        st.metric("📈 Total Columns", total_columns)
                    
                    with file_credentials_col2:
                        st.metric("❌ Missing Values", missing_values)
                        st.metric("🔄 Duplicate Rows", duplicate_rows)
                    
                    # Display list of columns
                    st.markdown("**📋 List of Columns:**")
                    columns_list = list(df.columns)
                    st.write(", ".join(columns_list))
                    if duplicate_rows > 0 or missing_values > 0:
                        st.error("There are duplicate values or missing values in the file. Please check the file and try again.")

            initiate_call_button = st.button("Initiate Call", type="primary", use_container_width=True)
            if initiate_call_button:
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
                url = f"https://{st.secrets.get('BASE_URL')}/file-upload"
                response = requests.post(url, files=files)
                if response.status_code == 200:
                    st.success("File uploaded and call process initiated!")
                else:
                    st.error(f"Failed to upload file. Status code: {response.status_code}")
                    st.write(response.text)