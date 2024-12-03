
from fastapi import Form, Depends
from pydantic import BaseModel


class CreateUserSchema(BaseModel):
    firstname: str
    lastname: str
    email: str
    phoneNumber: str
    password: str
    role: str
    privileges: list[str]

class LoginSchema(BaseModel):
    email: str
    password: str
    
