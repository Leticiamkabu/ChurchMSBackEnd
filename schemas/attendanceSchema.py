
from fastapi import Form, Depends
from pydantic import BaseModel
import uuid


class AttendanceSchema(BaseModel):
    id : uuid.UUID
    memberID: str
    firstname: str
    lastname: str
    othername: str
    status: str
    serviceType: str

class AttendanceResponseSchema(BaseModel):
    id : uuid.UUID
    memberID: str
    fullname: str
    status: str
    serviceType: str
    

    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models

    
class AttendanceResponse(AttendanceResponseSchema):
    pass  # You can add any extra fields or modifications if needed
