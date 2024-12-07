
from fastapi import Form, Depends
from pydantic import BaseModel


class AttendanceSchema(BaseModel):
    memberID: str
    name: str
    status: str
    serviceType: str
    


    
