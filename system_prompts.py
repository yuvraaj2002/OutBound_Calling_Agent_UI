# System prompts payload data extraction
payload_extraction_prompt: str = """
        **OBJECTIVE:**  
        Extract key contact and call details from admin instruction transcriptions with high accuracy and consistency. Focus ONLY on the specific fields requested for BlandAI call setup.

        ---

        **KEY INFORMATION TO EXTRACT**  
        Extract ONLY:

        {
          "agent_persona": "",
          "objective": "",
          "contact_name": "",
          "phone_number": "",
        }

        **EXTRACTION GUIDELINES**

        **AGENT PERSONA IDENTIFICATION:**
        - Look for self-introductions ("I'm [Name] from...", "This is [Name] with...", "I'm calling from...")
        - Identify company names, job titles, or department affiliations
        - Extract implied roles based on context and authority level
        - Include professional identity markers (sales rep, customer service, account manager, etc.)
        - Capture the complete professional identity, not just the name

        **OBJECTIVE IDENTIFICATION:**
        - Focus on explicit purpose statements ("I'm calling to...", "The reason for my call is...")
        - Look for action-oriented goals (schedule, confirm, discuss, follow up, etc.)
        - Identify what the caller wants the recipient to do or agree to
        - Extract the primary goal if multiple objectives are mentioned
        - Include specific outcomes or next steps mentioned

        **PHONE NUMBER EXTRACTION:**
        - Extract phone numbers in international E.164 format
        - Always include the + sign and the country code (e.g., +1 for USA, +91 for India)
        - Convert numbers to E.164 format only if clearly possible from the transcription
        - If the number is spoken in a local format, infer and reformat based on context (e.g., caller location or country-specific number pattern)
        - Do not include any dashes, parentheses, or spaces
        - If multiple numbers are mentioned, extract only the primary contact number
        - If the number is unclear or partial, return an empty string
        - IMPORTANT: Do not add country codes unless explicitly mentioned or clearly implied from context
        - If a number is provided without country code, extract it as-is with just the + prefix

        **Examples:**
        - Correct: +14155552671
        - Correct: +919876543210
        - Correct: +916239305919 (if India context is clear)
        - Correct: +916239305919 (if number is provided as 916239305919 with India context)
        - Incorrect: +91916239305919 (adding +91 when number already has 91)
        - Incorrect: 9876543210
        - Incorrect: +1 (415) 555-2671

        **NAME EXTRACTION:**
        - Identify the caller's full name and any titles
        - Extract the recipient's name if mentioned or confirmed
        - Include any third-party names referenced during the conversation
        - Capture names even if pronunciation is unclear (provide best interpretation)
        - If multiple names, separate with commas

        **ACCURACY REQUIREMENTS:**
        - Extract information only if clearly stated or strongly implied
        - Return empty string "" for fields not found in the transcription
        - Do not make assumptions beyond what the transcript supports
        - Account for speech-to-text errors
        - Prioritize repeated or confirmed information

        **CONTEXT CONSIDERATIONS:**
        - Analyze the entire conversation, not just isolated statements
        - Watch for corrections, clarifications, or verification during the call
        - Consider background context that clarifies role or intent
        - Handle unclear audio or interruptions appropriately

        **SPECIAL INSTRUCTIONS:**
        - For agent persona, include all available identity elements (name + company + role)
        - For unclear names or numbers, provide the best likely interpretation
        - Maintain consistent formatting across all fields
        - Focus on the primary speaker's details for agent persona and objective fields
    """
