from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from enum import Enum

class ResponseTypeEnum(str, Enum):
    COMMENT = "comment"
    DIRECT_REPLY = "direct_reply"

class FacebookReplyInput(BaseModel):
    comment_id: str = Field(..., description="User commented id from the webhook")
    message: str = Field(..., description="Reply to the user.")
    response_type: ResponseTypeEnum = Field(..., description="Whether the response should be comment or direct reply.")
    # payload: FacebookPayloadInput = Field(..., description="Facebook Payload")
    
class FacebookReplyTool(BaseTool):
    name: str = "Send Facebook Message or Comment."
    description: str = "Send facebook comment reply or direct message to the user."
    args_schema: Type[BaseModel] = FacebookReplyInput
 
    def _run(self, message, response_type, comment_id):
        access_token = '1234'
        page_id = '1234'
        message_1 = 'Please check your DM'
        print('comment id: ', comment_id)
        if response_type == 'comment':
            url = f"https://graph.facebook.com/v22.0/{comment_id}/comments?message={message}&access_token={access_token}"
        elif response_type == 'direct_reply':
            url_1 = f"https://graph.facebook.com/v22.0/{comment_id}/comments?message={message_1}&access_token={access_token}"
            url_2 = f"https://graph.facebook.com/v22.0/{page_id}/messages?access_token={access_token}"
        return "Comment Sent Successfully"
 
    def _arun(self, message, response_type):
        """Async implementation"""
        # For simple tools, just return the sync implementation
        return self._run(message, response_type)