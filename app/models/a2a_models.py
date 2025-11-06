from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field
import json

class JSONRPCRequest(BaseModel):
    jsonrpc: str = Field('2.0', description='JSON-RPC version')
    method: str = Field(..., description='Method to be invoked')
    params: Optional[Union[Dict[str, Any], list]] = Field(None, 
                                                          description='Method parameters',
                                                          examples=[{
                                                            'message': 'What time is it in Tokyo?',
                                                            'user_id': 'user123'
                                                          }])
    id: Optional[Union[int, str]] = Field(None, description='Request identifier')

class JSONRPCResponse(BaseModel):
    jsonrpc: str = Field('2.0', description='JSON-RPC version')
    result: Optional[Any] = Field(None, description='Method result on success')
    error: Optional[Dict[str, Any]] = Field(None, description='Error object on failure')
    id: Optional[Union[int, str]]  = Field(None, description='Request identifier')

class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class JSONRPCException(Exception):
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)


class JSONRPCErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000

def create_error_response(error_code: int, error_message: str, request_id: Optional[Union[int, str]] = None, data: Optional[Any] = None) -> JSONRPCResponse:
    return JSONRPCResponse(
        jsonrpc='2.0',
        error={
            'code': error_code,
            'message': error_message,
            'data': data
        },
        id=request_id
    )

def create_success_response(result: Any, request_id: Optional[Union[int, str]] = None) -> JSONRPCResponse:
    return JSONRPCResponse(
        jsonrpc='2.0',
        result=result,
        id=request_id
    )