from fastapi import APIRouter, Depends, HTTPException 
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func, and_
import requests
from passlib.context import CryptContext
import bcrypt
import random
import base64
from datetime import datetime, timedelta
from fastapi.responses import FileResponse 


from models.firstTimersModel import *
from models.membersModel import *

# from models.profileModel import *
# from models.itemsModel import *
from schemas.firstTimersSchema import *
from database.databaseConnection import SessionLocal
from notification.sendSMS import *
from pathlib import Path

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
from helperFunctions.exportFile import *

# file upload
from fastapi import UploadFile,status, File, Form
# from utils.minio_util import upload_file

import re
from sqlalchemy.sql import func , extract



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




purpose_of_coming = ["VISIT", "MEMBERSHIP", "REDEDICATION" ]
first_timer_status = ["VISITOR", "MEMBER"]
first_timer_class = ["NEW CONVERT", "NEW MEMBERS", "DISCIPLESHIP", "BAPTISM"],
special_prayer_or_counseling = ["BUSINESS", "HEALTH", "DELIVERANCE", "MARITAL", "EDUCATIONAL", "OTHERS", "" ]


@router.post("/first_timers/create")
async def create_first_timers(db: db_dependency, request: FirstTimersSchema):

    result = await db.execute(
        select(FirstTimers).where(FirstTimers.name == request.name)
    )
    first_timer_data = result.scalar() 

    if first_timer_data:
            # print(attendance.status)
            return "First timer already exists"

    if request.purposeOfComing not in purpose_of_coming:
        print(request.purposeOfComing)
        return "Purpose of coming data provided does not exist"

    if request.specialPrayerOrCounseling not in special_prayer_or_counseling:
        print(request.specialPrayerOrCounseling)
        return "Special prayer or counseling data provided does not exist"

   
    first_timers_data = FirstTimers(
                name = request.name,
                popularName = request.popularName,
                phoneNumber = request.phoneNumber,
                whatsAppNumber = request.whatsAppNumber,
                houseLocation = request.houseLocation,
                purposeOfComing = request.purposeOfComing,
                contactHours = request.contactHours,
                specialPrayerOrCounseling = request.specialPrayerOrCounseling,
                counselor = request.counselor,
                birthMonth = request.birthMonth,
                date = request.date,
                status = "VISITOR",
                ftClass = "NEW MEMBERS",
                createdOn = datetime.today()
                

            )
    

    db.add(first_timers_data)
    await db.commit()

    

    logger.info("First timers created and saved in the database")


    logger.info("First timers creation Sucessful")
    return {"message": "First timers creation successful", "First_Timers": first_timers_data}


# get all first timers
@router.get("/first_timers/get_all_first_timers")
async def get_all_first_timers( db: db_dependency):

    first_timers = await db.execute(select(FirstTimers))
    first_timers_data = first_timers.scalars().all()
    
    if first_timers_data  is None:
        raise HTTPException(status_code=404, detail="No first timers data exists", data = first_timers_data)
    
    return first_timers_data 


# Download first timers List
@router.get("/first_timers/get_all_first_timers_List")
async def get_all_first_timers_List( db: db_dependency):

   
    return "Coming soon"

# get first timer by name
@router.get("/first_timers/get_first_timers_by_name/{name}")
async def get_first_timer_by_name( name: str ,db: db_dependency):

    first_timers = await db.execute(select(FirstTimers).where(FirstTimers.name == request.name))
    first_timer_data = first_timers.scalar() 
    
    if first_timer_data  is None:
        raise HTTPException(status_code=404, detail="First_timer with name does not exist", data = first_timer_data)
    
    return first_timer_data


# get first timers by id
@router.get("/first_timers/get_first_timers_by_id/{id}")
async def get_first_timer_by_id( id: uuid.UUID ,db: db_dependency):

    first_timer_data = await db.get(FirstTimers, id)
    
    
    if first_timer_data  is None:
        raise HTTPException(status_code=404, detail="First Timer with id does not exist", data = first_timer_data)
    
    return first_timer_data


# update first timers status
@router.get("/first_timers/update_first_timers__status/{id}")
async def update_first_timer( id: uuid.UUID ,db: db_dependency, status: str):

    if status not in first_timer_status:
        print(status)
        return "Status provided does not exist"

    first_timer_data = await db.get(FirstTimers, id)
    
    if first_timer_data  is None:
        raise HTTPException(status_code=404, detail="First Timer with id does not exist", data = first_timer_data)

    first_timer_data.status = status

    await db.commit()
    # check if status is member, then add it to member table
    
    return first_timer_data


# update first timers 
@router.patch("/first_timers/update_first_timers_by_id/{id}")
async def update_first_timer( id: str ,db: db_dependency, request: FirstTimersSchema):
    first_timer_data = await db.get(FirstTimers, uuid.UUID(id))
    
    if first_timer_data  is None:
        raise HTTPException(status_code=404, detail="First Timer with id does not exist", data = first_timer_data)

    # Handle promotion to MEMBER
    if request.status == "MEMBER":
        full_name = request.name.strip()
        name_parts = full_name.split()

        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        middle_name = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ''

        result = await db.execute(select(func.count(Member.id)))
        count = result.scalar()
        member_data = Member(
            memberID=generatedId(count),
            firstName=first_name,
            middleName=middle_name,
            lastName=last_name,
            phoneNumber=request.phoneNumber,
            homeAddress=request.houseLocation,
            memberType="MEMBER",
            dateJoined=str(datetime.today()),
            memberStatus="ALIVE",
        )

        db.add(member_data)
        await db.commit()

        result = await db.execute(
        select(Member).where(Member.memberID == member_data.memberID)
        )
        new_member_data = result.scalar() 

        if new_member_data:
            await db.delete(first_timer_data)
            await db.commit()
        return {
        "message": "First Timer is now a member",
        "First Timer": first_timer_data
    }
    

    # Update regular first timer fields
    inputs = request.dict(exclude_unset=True)

    # Always update updatedOn field
    first_timer_data.updatedOn = datetime.today()

    # Optional: Update ftClass if present
    if "ftClass" in inputs:
        first_timer_data.ftClass = inputs["ftClass"]

    # Update all other fields safely
    for key, value in inputs.items():
        if hasattr(first_timer_data, key) and value is not None:
            setattr(first_timer_data, key, value)

    await db.commit()
    await db.refresh(first_timer_data)

    logger.info("First timer data updated successfully for first_timer_id: %s", id)

    return {
        "message": "First timer details update successful",
        "First Timer": first_timer_data
    }
    


@router.delete("/first_timers/delete_first_timers_by_id/{id}")
async def delete_first_timers_by_id(id: uuid.UUID, db: db_dependency):

    result = await db.execute(select(First_Timers).where(First_Timers.id == id))
    first_timer = result.scalar_one_or_none()
    
    if first_timer is None:
        raise HTTPException(status_code=404, detail="First_timer not found")

    # Delete the user
    await db.delete(first_timer)
    await db.commit()


    return "first_timer deleted successfully"





# upload member sample document docx
@router.get("/first_timers/download_sample_upload_data_document")
async def upload_docx():

    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = BASE_DIR/"sampleDataFormat/firstTimers/Sample_Data_for_Adding_First_Timers.docx"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename="first_timers_data_sample_document.docx")


# get first timer by name
@router.get("/first_timers/get_first_timer_by_name/{name}")
async def get_first_timers_by_words( name: str ,db: db_dependency):

    search_conditions = [
        FirstTimers.name.ilike(f"%{name}%")
    ]

    query = select(FirstTimers).filter(*search_conditions)


    result = await db.execute(query)
    first_timers_data = result.scalars().all()
    print(first_timers_data)
    
    
    
    if first_timers_data  == []:
        raise HTTPException(status_code=200, detail="First timers with the given names do not exist" )
    
    return first_timers_data


# download members
@router.get("/first_timers/download_first_timers_data/{format}")
async def download_first_timers_data(db: db_dependency, format : str):

    if format != "Excel" and format != "Docx":
        raise HTTPException(status_code=400, detail="File format does not exist")

    first_timer = await db.execute(select(FirstTimers).order_by(FirstTimers.id))
    first_timer_data = first_timer.scalars().all()
    ordered_first_timer_data = [FirstTimersResponse.from_orm(first_timer) for first_timer in first_timer_data]  

    first_timer_dicts = []
    for first_timer in ordered_first_timer_data:
        first_timer_dict = {}
        for key, value in first_timer.__dict__.items():
            if not key.startswith('_'):
                # If the value is a UUID, set the key as 'id' and convert the value to a string
                if isinstance(value, uuid.UUID):
                    first_timer_dict['id'] = str(value)  # Change the key to 'id' and convert the UUID to a string
                else:
                    first_timer_dict[key] = value
        first_timer_dicts.append(first_timer_dict)
        # print ("the data before the sheet ",member_dicts)
    # Check if member_data is empty
    if not ordered_first_timer_data:
        raise HTTPException(status_code=200, detail="No first timers data exists")

    if format == "Excel":
        # Generate Excel file
        file_path = generate_excel(first_timer_dicts, "first_timers_data")
        media_Type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file_Name = "first_timers_data.xlsx"

    elif format == "Docx":
        file_path = generate_excel(first_timer_dicts, "first_timers_data")
        media_Type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file_Name = "first_timers_data.docs"


    # Return the file using FastAPI's FileResponse
    return FileResponse(file_path, media_type = media_Type, filename = file_Name)

def to_camel_case(snake_str):
    """Convert snake_case or other formats to camelCase"""
    components = re.split(r'[_\s]+', snake_str)  # Split by underscores or spaces
    return components[0].lower() + ''.join(x.capitalize() for x in components[1:])


from docx import Document
import io
@router.post("/first_timers/upload-docx")
async def upload_docx(db: db_dependency , file: UploadFile = File(...)):
    try:
        # Ensure the file is a .docx file
        if not file.filename.endswith(".docx"):
            raise HTTPException(status_code=400, detail="Only .docx files are supported.")

        # Read the file content
        contents = await file.read()

        # Convert bytes to a file-like object
        doc_file = io.BytesIO(contents)

        # Load the .docx document
        doc = Document(doc_file)

                # Each table represents part of each individual's data
        tables = [table for table in doc.tables]

        # Extract headers and rows from each table
        table_rows = []
        for table in tables:
            
            rows = [
                [cell.text.strip() for cell in row.cells]
                for row in table.rows
                if any(cell.text.strip() for cell in row.cells) and not row.cells[0].text.strip().lower().startswith("sp")
            ]

            print("rows : ",rows)
            
            header = rows[0][1:]
            print(header)
            data_rows = [row[1:] for row in rows[1:]]
            # print(data_rows)
            print("First data row:", data_rows[0])
            print("Header:", header)
            # Convert each row to a dict using the table's header
            row_dicts = [dict(zip(header, row)) for row in data_rows]
            # print("yes",row_dicts)
            table_rows.append(row_dicts)
            print("First data row:", table_rows[0])


        

        print("yes", table_rows)
        # Now combine the matching rows across all tables
        individuals_data = []
        for i in range(len(table_rows[0])):  # assuming all tables have same number of rows
            print("ys")
            person_data = {}
            for table in table_rows:
                person_data.update(table[i])  # merge dictionaries for same person from each table
            individuals_data.append(person_data)
            print("person: ", person_data) 

        

        counts = 0
        new_first_timer_list = []
        skiped_first_timers_list = []
        for first_timer_data in individuals_data:
            counts = counts + 1
            result = await db.execute(select(func.count(FirstTimers.id)))
            first_timers_count = result.scalar()

            # print("yiiy",member_data)
            data = {to_camel_case(k): v for k, v in first_timer_data.items() if k.strip()}
            print("hfjhfghj", data)

            stmt = select(FirstTimers).where(FirstTimers.name == data['name'])

            result = await db.execute(stmt)
            existing_first_timers = result.scalar_one_or_none()


            if existing_first_timers:
                print("yessssssss")
                skiped_first_timers_list.append(data['name'])
                pass
                
            else:

                new_first_timer = FirstTimers(**data)
                new_first_timer_list.append(new_first_timer)
                db.add(new_first_timer)
                await db.commit()
        
        return {"message": "First Timers added successfully", "total_first_timers": len(new_first_timer_list),"skipped_first_timers": skiped_first_timers_list} 

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

def generatedId(lastNumber):
    id_constant = 'CTC_M_00'
    id_number = lastNumber + 1
    return id_constant + str(id_number)
