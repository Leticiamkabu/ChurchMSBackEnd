from fastapi import Form, Depends
from pydantic import BaseModel
import uuid
from typing import List

class FirstTimersSchema(BaseModel):
    name : str
    popularName : str
    phoneNumber: str
    whatsAppNumber: str
    houseLocation: str
    purposeOfComing: str
    contactHours: str
    specialPrayerOrCounseling: str
    counselor: str
    ftClass: str
    date: str
    status: str
    
    


    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models


class FirstTimersResponse(FirstTimersSchema):
    pass  # You can add any extra fields or modifications if needed


