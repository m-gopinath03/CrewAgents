from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any
import requests

class TrackingDetailsInput(BaseModel):
    tracking_number: str = Field(..., description="The tracking number to look up")

class TrackingDetails(BaseTool):
    name: str = "Tracking Details"
    description: str = "Get the tracking details by tracking number"
    args_schema: Type[BaseModel] = TrackingDetailsInput
    
    def _run(self, tracking_number: str) -> Dict[str, Any]:
        url = "https://app.pinascargo.com/ai_api/tracking"
        headers = {
            "apikey": "26820b9f-a7e7-46cd-a772-7520e1d82041"
        }
        data = {
            "booking_number": tracking_number
        }
        response = requests.post(url, headers=headers, json=data)
        # Hardcoded tracking data for demo
        return response.json().get("data", "No data found")

    def _arun(self, tracking_number: str):
        """Async implementation"""
        # For simple tools, just return the sync implementation
        return self._run(tracking_number)