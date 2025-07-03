from openai import OpenAI
import logging
import streamlit as st
from system_prompts import payload_extraction_prompt

class OpenAIService:
    def __init__(self):
        # Use st.secrets instead of os.getenv
        openai_api_key = st.secrets.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in Streamlit secrets")
        
        self.openai_client = OpenAI(api_key=openai_api_key)
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
        
    def generate_response(self, input_text, max_tokens):

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": payload_extraction_prompt},
                {"role": "user", "content": input_text}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def get_response_with_retry(self, input_text, keys_to_check, max_tokens):
        retries = 3
        for attempt in range(retries):
            try:
                response = self.generate_response(input_text, max_tokens)

                # Check if required keys exist in the response and their values are not None
                missing_keys = [key for key in keys_to_check if key not in response]
                if not missing_keys:
                    return response
                else:
                    raise ValueError(f"Missing keys or None values in response: {missing_keys}")
            except Exception as e:
                self.logger.error(f"Error retrieving response: {e}. Attempt {attempt + 1} of {retries}.")
        return {}