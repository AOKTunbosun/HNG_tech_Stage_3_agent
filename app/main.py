from fastapi import FastAPI, HTTPException
from typing import List, Optional, Union, Dict, Any
import google.genai as genai
from .config import settings


from .chatbot import chatbot
from .models.a2a_models import (
    JSONRPCRequest,
    JSONRPCResponse,
    create_error_response, 
    create_success_response,
    JSONRPCErrorCodes
)

app = FastAPI(
    title='Timezone Conversion Chatbot - JSON-RPC 2.0',
    description='A JSON-RPC 2.0 compliant chatbot that converts time between different timezones',
    version='1.0.0'
)


class JSONRPCProcessor:
    def __init__(self, chatbot_instance):
        self.chatbot = chatbot_instance
        self.methods = {
            'chat': self.chat
        }
    

    async def chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not params or 'message' not in params:
            raise ValueError('Missing required parameter: message')
        
        user_id = params.get('user_id')
        return await self.chatbot.process_chat_message(params['message'], user_id)
    
    
    async def process_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        try:
            if request.method not in self.methods:
                return create_error_response(
                    JSONRPCErrorCodes.METHOD_NOT_FOUND,
                    f'Method not found: {request.method}',
                    request.id,
                    {'available_methods': list(self.methods.keys())}
                )
            
            method_handler = self.methods[request.method]
            result = await method_handler(request.params or {})

            return create_success_response(result, request.id)
        
        except ValueError as e:
            return create_error_response(
                JSONRPCErrorCodes.INVALID_PARAMS,
                str(e),
                request.id
            )
        except Exception as e:
            return create_error_response(
                JSONRPCErrorCodes.INTERNAL_ERROR,
                f'Internal error: {str(e)}',
                request.id
            )
    
rpc_processor = JSONRPCProcessor(chatbot)

@app.get('/')
async def root():
    return {
        'message': 'Timezone Conversion Chatbot API',
        'status': 'running',
        'specification': 'JSON-RPC 2.0',
        'available_methods': ['chat']
    }

@app.post('/rpc')
async def json_rpc_endpoint(request_data: JSONRPCRequest):
    try:
        response = await rpc_processor.process_request(request_data)
        return response.dict()
    
    except Exception as e:
        return create_error_response(
            JSONRPCErrorCodes.INTERNAL_ERROR,
            f'Error processing request: {str(e)}'
        ).dict()



@app.get("/debug/api-test")
async def debug_api_test():
    """Test API connection and available models"""
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Test 1: List models
        models = client.models.list()
        model_names = [model.name for model in models]
        
        # Test 2: Try a simple generation with known working model
        try:
            test_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Say 'Hello World'"
            )
            generation_works = True
            test_text = test_response.text
        except Exception as e:
            generation_works = False
            test_text = str(e)
        
        return {
            "api_key_valid": True,
            "available_models": model_names,
            "generation_test": generation_works,
            "test_response": test_text,
            "total_models": len(model_names)
        }
        
    except Exception as e:
        return {
            "api_key_valid": False,
            "error": str(e)
        }