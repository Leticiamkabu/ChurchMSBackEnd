from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
import uuid
import os

from datetime import datetime
from sqlalchemy import select, or_, func
import requests
from passlib.context import CryptContext
import bcrypt
import random
import base64



from models.membersModel import *
# from models.profileModel import *
# from models.itemsModel import *
from schemas.membersSchema import *
from database.databaseConnection import SessionLocal
# from security.auth import *
# from security.error_handling import *
# from security.auth_bearer import jwtBearer

# # logs
# from logging_lib import LogConfig
# from logging.config import dictConfig
import logging

# email
# from emails import *
# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
# from smtplib import SMTPException
import os
import string


# file upload
from fastapi import UploadFile,status, File, Form
# from utils.minio_util import upload_file

import re
from sqlalchemy.sql import func



# # loging config
# dictConfig(LogConfig().dict())
logger = logging.getLogger("Humanity App")



# create a connection to the database
async def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]




router = APIRouter()


# create member
@router.post("/members/create_member")  # done connecting
async def create_member(db: db_dependency, member: MemberSchema):

    logger.info("Endpoint : create_memeber")

     # Check if at least one field in the member schema has data
    if not any(value for value in member.dict().values() if value not in [None, '']):
        raise HTTPException(
            status_code=200,
            detail="No data provided. Member data rejected."
        )

    member_data = Member(
                title=member.title,
                firstname=member.firstname,
                middlename=member.middlename,
                lastname =member.lastname,
                dateOfBirth = member.dateOfBirth,
                gender = member.gender,
                phoneNumber=member.phoneNumber,
                email = member.email,
                nationality = member.nationality,
                homeTown = member.homeTown,
                homeAddress = member.homeAddress,
                workingStatus = member.workingStatus,
                occupation = member.occupation,
                qualification = member.qualification,
                institutionName = member.institutionName,
                mothersName = member.mothersName,
                fathersName = member.fathersName,
                nextOfKin = member.nextOfKin,
                nextOfKinPhoneNumber = member.nextOfKinPhoneNumber,
                maritalStatus = member.maritalStatus,
                spouseContact = member.spouseContact,
                spouseName = member.spouseName,
                numberOfChildren = member.numberOfChildren,
                memberType = member.memberType,
                cell = member.cell,
                departmentName = member.departmentName,
                dateJoined = member.dateJoined,
                classSelection = member.classSelection,
                position = member.position,
                waterBaptised = member.waterBaptised,
                baptisedBy = member.baptisedBy,
                dateBaptised = member.dateBaptised,
                baptisedByTheHolySpirit = member.baptisedByTheHolySpirit,
                memberStatus = member.memberStatus,
                dateDeceased = member.dateDeceased,
                dateBuried = member.dateBuried,
                confirmed = member.confirmed,
                dateConfirmed = member.dateConfirmed,
                comment = member.comment,

            )


      # Save member to the database
    db.add(member_data)
    await db.commit()

    logger.info("Member registration successful.")
    return {"message": "Member registration successful", "Member": member_data}
    

    

    




# create member
@router.post("/members/create_member_image")  # done connecting
async def create_member_image(db: db_dependency, fullname : str = Form(...),  file: UploadFile = File(...)):

    logger.info("Endpoint : create_member_image")

    # Validate file type (e.g., images only)
    allowed_file_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_file_types:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed types: jpeg, png, gif.")
    
    #  Read the file content as binary data
    member_image_data = await file.read()
    
    # Convert to Base64
    image_base64 = base64.b64encode(member_image_data).decode('utf-8')
    
    # Create an image instance and associate it with the new item
    new_member_image = MemberImage(
        fullname = fullname,  # Use new_item_data.id here
        image = image_base64,
        imageFileName=file.filename
    )
    
    # Add the new image to the database
    db.add(new_member_image)
    await db.commit()
    
    logger.info("Member image created and saved in the database with ID: %s", new_member_image.id)

    return {"message": "Member image creation successful", "member_image_id": new_member_image.id}


# import io
# import pandas as pd
# import magic  # To detect file type
# # from fastapi import APIRouter, UploadFile, HTTPException
# from typing import Any


# @router.post("/members/upload")

# def extract_file_data(file: UploadFile):
#     try:
#         # Read the file content
#         file_content = file.file.read()

#         # Detect the file type based on extension
#         file_extension = file.filename.split('.')[-1].lower()

#         if file_extension in ['xls', 'xlsx']:
#             # Handle Excel files
#             data = pd.read_excel(io.BytesIO(file_content))
#             extracted_data = data.to_dict(orient="records")  # Convert to list of dicts

#         elif file_extension == 'csv':
#             # Handle CSV files
#             data = pd.read_csv(io.BytesIO(file_content))
#             extracted_data = data.to_dict(orient="records")

#         elif file_extension == 'json':
#             # Handle JSON files
#             extracted_data = json.loads(file_content.decode("utf-8"))

#         elif file_extension == 'txt':
#             # Handle plain text files (assume space or tab delimited)
#             try:
#                 data = pd.read_csv(io.BytesIO(file_content), delimiter=r'\s+')
#                 extracted_data = data.to_dict(orient="records")
#             except Exception:
#                 # If parsing as a table fails, return raw text lines
#                 extracted_data = file_content.decode("utf-8").splitlines()

#         else:
#             raise HTTPException(status_code=400, detail="Unsupported file type. Please upload CSV, JSON, TXT, or Excel files.")

#         return extracted_data

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")





# get all members
@router.get("/members/get_all_members")
async def get_all_members( db: db_dependency):

    member = await db.execute(select(Member))
    member_data = member.scalars().all()
    
    if member_data  is None:
        raise HTTPException(status_code=200, detail="No user data exists", data = member_data)
    
    return member_data 
    


# get member by id
@router.get("/members/get_member_by_id/{member_id}")
async def get_member_by_id( member_id: uuid.UUID ,db: db_dependency):

    member_data = await db.get(Member, member_id)
    
    
    if member_data  is None:
        raise HTTPException(status_code=200, detail="user with id does not exist", data = member_data)
    
    return member_data






# get member by words
@router.get("/members/get_member_by_words/{words}")
async def get_member_by_words( words: str ,db: db_dependency):


    # Modify the query to check if the search string is present in firstname, lastname, or email
    query = select(Member).where(
        or_(
            Member.firstname.ilike(f"%{words}%"),  # Case-insensitive match
            Member.lastname.ilike(f"%{words}%"),
            Member.middlename.ilike(f"%{words}%")
        )
    )

    # Execute the query
    result = await db.execute(query)
    members_data = result.scalars().all()
    # user = await db.execute(select(User).where(User.role == role))
    # user_data = user.scalars().all()
    
    
    if members_data  == []:
        raise HTTPException(status_code=200, detail="Members with the given names do not exist")
    
    return members_data




# get total number of members
@router.get("/members/get_total_number_of_members")
async def get_total_number_of_members(db: db_dependency):

    result = await db.execute(select(func.count(Member.id)))
    total_members = result.scalar()  

    return {"total_members": total_members}







# update member by id



@router.patch("/members/update_individual_member_fields/{member_id}")
async def update_member(db: db_dependency,member_id: str, member_input: dict):
    
    logger.info("Endpoint: update_member called for member_id: %s", member_id)
    
    # Query for the user data
    member_data = await db.get(Member, uuid.UUID(member_id))
    # user_data = users.scalar()
    # old_username = user_data.username
    # print("old username : ", old_username)
    
    if not member_data:
        logger.error("User with ID %s not found", member_id)
        raise HTTPException(status_code=404, detail="Member not found")
    
    logger.info("Member data queried successfully for member_id: %s", member_id)
    
    # Convert user data and input into dictionaries
    converted_member_data = member_data.__dict__
    inputs = member_input


    # Only update fields that are present in both user data and input
    for key, value in inputs.items():
        if key in converted_member_data and value is not None: 
            # print("key : ", key)
            # print("value :", value) # Avoid updating with `None` values
            setattr(member_data, key, value)
    
    logger.info("Member data ready for storage for member_id: %s", member_id)
    
   
    await db.commit()
    
    

    
    logger.info("Member data updated successfully for member_id: %s", member_id)
    
    return member_data
    
    



# delete user

@router.delete("/members/delete_member_by_id")
async def delete_member_by_id(member_id: uuid.UUID, db: db_dependency):

    result = await db.execute(select(Member).where(Member.id == member_id))
    member = result.scalar_one_or_none()
    
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    # Delete the user
    await db.delete(member)
    await db.commit()


    return "Member deleted successfully"
