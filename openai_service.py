from openai import OpenAI
import logging
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from agent_config import payload_extraction_prompt
from langchain_core.messages import HumanMessage, SystemMessage
from rich import print

class OpenAIService:
    def __init__(self):
        # Use st.secrets instead of os.getenv
        openai_api_key = st.secrets.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in Streamlit secrets")
        
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.chat_openai = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini", temperature=0.2, max_tokens=1000, timeout=None, max_retries=2)
        self.logger = logging.getLogger(__name__)
        
    def transcribe_audio(self, audio_file):
        """
        Uses OpenAI's Whisper model to transcribe speech from an audio file.
        """
        try:
            # Read the file content into bytes
            audio_content = audio_file.read()
            
            response = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=("audio.wav", audio_content),  
                response_format="text"
            )
            return response

        except Exception as e:
            self.logger.error(f"Error in transcription: {str(e)}")
            return None
    
    def get_response_with_retry(self, messages, keys_to_check):
        retries = 3
        for attempt in range(retries):
            try:
                response = self.chat_openai.invoke(messages)
                response = response.content

                # Check if required keys exist in the response and their values are not None
                missing_keys = [key for key in keys_to_check if key not in response]
                if not missing_keys:
                    return response
                else:
                    raise ValueError(f"Missing keys or None values in response: {missing_keys}")
            except Exception as e:
                self.logger.error(f"Error retrieving response: {e}. Attempt {attempt + 1} of {retries}.")
        return {}
    

# if __name__ == "__main__":
#     openai_service = OpenAIService()
#     messages = [
#         SystemMessage(payload_extraction_prompt.format(transcript="Hey, good morning. I wanted to call Ibrahim Singh to get an update on his back pain and his phone number is 916239305919 and the main objective is that I wanted to make sure to get an update on how his back pain is going on and act as a very friendly assistant I would say.")),
#         HumanMessage("Extract the key information from the transcript")
#     ]
#     result = openai_service.get_response_with_retry(messages, ["agent_persona", "objective", "name", "phone_number"])
#     print(result)