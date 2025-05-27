
from fastapi import Form, Depends
from pydantic import BaseModel
import uuid
from typing import Optional


class AttendanceSchema(BaseModel):
    # id : uuid.UUID
    memberID: str
    name: str
    status: str
    serviceType: str
    markedBy: str

class AttendanceResponseSchema(BaseModel):
    id : uuid.UUID
    memberID: str
    fullName: str
    status: str
    department: Optional[str]
    markedBy: str
    timeStamp : str
    

    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models

    
class AttendanceResponse(AttendanceResponseSchema):
    id : Optional[uuid.UUID]
    pass  # You can add any extra fields or modifications if needed
