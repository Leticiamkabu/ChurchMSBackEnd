
from fastapi import Form, Depends
from pydantic import BaseModel
import uuid

class MemberSchema(BaseModel):
    memberID : str
    title : str
    firstName : str
    middleName : str
    lastName : str
    dateOfBirth : str
    age : str
    gender : str
    phoneNumber : str
    email : str
    nationality :str
    homeTown :str
    homeAddress : str
    workingStatus : str
    occupation : str
    qualification : str
    institutionName : str
    mothersName :str
    fathersName :str
    nextOfKin :str
    nextOfKinPhoneNumber :str
    maritalStatus :str
    spouseContact :str
    spouseName :str
    numberOfChildren :str
    memberType :str
    cell :str
    departmentName :str
    dateJoined :str
    classSelection :str
    spiritualGift :str
    position :str
    waterBaptised :str
    baptisedBy :str
    dateBaptised :str
    baptisedByTheHolySpirit :str
    memberStatus :str
    dateDeceased :str
    dateBuried :str
    confirmed :str
    dateConfirmed :str
    comment :str
    
   
    

    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models


class MemberResponse(MemberSchema):
    pass  # You can add any extra fields or modifications if needed
