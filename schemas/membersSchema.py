
from fastapi import Form, Depends
from pydantic import BaseModel


class MemberSchema(BaseModel):
    firstname: str
    lastname: str
    othername: str
    phoneNumber: str
    email: str
    age: str
    dateOfBirth: str
    houseAddress: str


    
