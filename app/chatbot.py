import google.genai as genai
import pytz
from datetime import datetime
from typing import Dict, Any, Optional
from .config import settings
from .models.a2a_models import JSONRPCException, JSONRPCErrorCodes

class TimezoneChatbot:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = 'gemini-2.5-flash'

        self.system_prompt = """
        You are a helpful timezone conversion assitant. Your role is to:
        1. Help users convert time between different timezones
        2. Provide current time in different locations
        3. Handle timezone-related queries

        When users ask about time conversion:
        - Always ask for clarification if the timezone or time is ambiguous
        - Use standard timezone names (e.g., 'Africa/Lagos', 'Asia/Shanghai')
        - Provide accurate time conversions

        Be conversational and helpful. If you need more information to provide an accurate conversation, ask the user for clarification.

        Example interaction:
        User: 'What time is it in China when it's 2 PM in Nigeria?'
        Assistant: 'When it's 2:00 PM in Nigeria (Africa/Lagos), it would be 9:00 PM in China (Asia/Shanghai). Nigeria is UTC+1 and China is UTC+8, so China is 7 hours ahead of Nigeria.'

        User: 'Current time in New York'
        Assistant: 'The current time in New York (America/New_York) is [calculate current time].'
        """

    async def process_chat_message(self, message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not message or not message.strip():
                raise JSONRPCException(
                    code=JSONRPCErrorCodes.INVALID_PARAMS,
                    message='Message cannot be empty'
                )
            
            enhanced_prompt = f'''
            {self.system_prompt}

            User query: {message}
            
            Please provide a helpful response about timezone conversion.
            '''

            response = self.client.models.generate_content(model=self.model, contents=enhanced_prompt)

            return {
                'response': response.text,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
        
        except JSONRPCException:
            raise
        except Exception as e:
            raise JSONRPCException(
                code=JSONRPCErrorCodes.INTERNAL_ERROR,
                message=f'Error processing chat message: {str(e)}'
            )

chatbot = TimezoneChatbot()