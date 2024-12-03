
from fastapi import Form, Depends
from pydantic import BaseModel


class AttendanceSchema(BaseModel):
    memberID: str
    firstname: str
    lastname: str
    othername: str
    status: str
    serviceType: str
    


    
