
from fastapi import Form, Depends
from pydantic import BaseModel


class CreateUserSchema(BaseModel):
    firstName: str
    lastName: str
    email: str
    phoneNumber: str
    password: str
    role: str
    privileges: str

class LoginSchema(BaseModel):
    email: str
    password: str


class UserLoginTrackerSchema(BaseModel):
    status: str
    logInTime: str
    userId: str
    
