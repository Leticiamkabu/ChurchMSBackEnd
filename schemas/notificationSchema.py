from fastapi import Form, Depends
from pydantic import BaseModel
import uuid
from typing import List

class SMSRequestSchema(BaseModel):
    to : str
    message : str
    notificationType: str
    
    


    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models


class SMSRequestResponse(SMSRequestSchema):
    pass  # You can add any extra fields or modifications if needed


class BulkSMSRequestSchema(BaseModel):
    recipient: List[str] # phone number
    message: str
    notificationType: str


class ScheduledSMSMessageRequestSchema(BaseModel):
    senderId : str
    recipient: List[str] # phone number
    message: str
    notificationType: str
    scheduledTime: str

class SendScheduledSMSRequestSchema(BaseModel):
    recipient: List[str] # phone number
    message: str
    senderId: str
