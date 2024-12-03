
from fastapi import Form, Depends
from pydantic import BaseModel


class MemberSchema(BaseModel):
    title : str
    firstname : str
    middlename : str
    lastname : str
    dateOfBirth : str
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
    


    
