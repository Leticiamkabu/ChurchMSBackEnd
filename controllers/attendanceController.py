from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
import uuid
import os
from fastapi.responses import FileResponse 
from datetime import date
from sqlalchemy import select, or_, func
import requests
from passlib.context import CryptContext
import bcrypt
import random


from helperFunctions.exportFile import *
from models.attendanceModel import *
# from models.profileModel import *
# from models.itemsModel import *
from schemas.attendanceSchema import *
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

Status = ["PRESENT", "ABSENT" ]

# create member
@router.post("/attendance/create_attendance")  # done connected
async def create_user(db: db_dependency, attendance: AttendanceSchema):

    logger.info("Endpoint : create_attendance")
    result = await db.execute(
        select(Attendance).where(Attendance.memberID == attendance.memberID, Attendance.date == str(date.today()))
    )
    attendance_data = result.scalar() 


    if attendance_data:
            print(attendance.status)
            return "Attendance marked for this member"

    if attendance.status not in Status:
        print(attendance.status)
        return "Status provided does not exist"

     

    attendance_data = Attendance(
                memberID= attendance.memberID,
                fullname = attendance.name ,
                date = str(date.today()),
                status= attendance.status,
                serviceType = attendance.serviceType
                

            )
    

    db.add(attendance_data)
    await db.commit()

    

    logger.info("Attendance created and saved in the database")


    logger.info("Attendnace creation Sucessful")
    return {"message": "Attendance creation successful", "Attendance": attendance_data}






# get all attendance
@router.get("/attendance/get_all_attendance")
async def get_all_members( db: db_dependency):

    attendance = await db.execute(select(Attendance))
    attendance_data = attendance.scalars().all()
    
    if attendance_data  is None:
        raise HTTPException(status_code=404, detail="No attendance data exists", data = attendance_data)
    
    return attendance_data 
    


# get attendance by id
@router.get("/attendnance/get_attendance_by_id/{attendance_id}")
async def get_attendance_by_id( attendance_id: uuid.UUID ,db: db_dependency):

    attendance_data = await db.get(Attendance, attendance_id)
    
    
    if attendance_data  is None:
        raise HTTPException(status_code=404, detail="Attendance with id does not exist", data = attendance_data)
    
    return attendance_data

# get attendance by member id
@router.get("/attendance/get_attendance_by_member_id/{member_id}")
async def get_attendance_by_member_id(member_id: str, db: db_dependency):
    result = await db.execute(
        select(Attendance).where(Attendance.memberID == member_id, Attendance.date == str(date.today()))
    )
    attendance_data = result.scalar()  # Retrieve all matching rows

    if not attendance_data:
        raise HTTPException(status_code=200, detail="Attendance with the given member ID does not exist")

    return attendance_data




# get attendance data by status and date
@router.get("/attendance/get_attendance_data_by_status_and_date")
async def get_attendance_data_by_status_and_date(status: str, date: str, db: db_dependency):

    if status not in Status:
        print(status)
        return "Status provided does not exist"

    # Query to fetch attendance data based on status and date
    result = await db.execute(
        select(Attendance).where(Attendance.date == date, Attendance.status == status)
    )
    
    attendance_data = result.scalars().all()  # Fetch all matching records

    if attendance_data == []:
        return "No data found"

    return attendance_data



# get total number of attendant on a particuler date
@router.get("/attendance/get_attendance_for_the_current_day") # done connected
async def get_attendance_for_the_current_day( db: db_dependency):

    
    result = await db.execute(
        select(func.count()).select_from(Attendance).where(Attendance.date == str(date.today()))
    )
    total_attendance = result.scalar() 
    
    result = await db.execute(
        select(func.count()).select_from(Attendance).where(Attendance.date == str(date.today()), Attendance.status == "PRESENT")
    )
    present_attendance = result.scalar()
    
    result = await db.execute(
        select(func.count()).select_from(Attendance).where(Attendance.date == str(date.today()), Attendance.status == "ABSENT")
    )
    absent_attendance = result.scalar() # Get the count result

    # if total_members == 0
    #     return "No data found"

    return {"total_attendance": total_attendance, "present_attendance": present_attendance,"absent_attendance": absent_attendance}






# get attendance data by current date
@router.get("/attendance/get_attendance_data")
async def get_attendance_data( db: db_dependency):


    # Query to fetch attendance data based on status and date
    result = await db.execute(
        select(Attendance).where(Attendance.date == str(date.today()))
    )
    
    attendance_data = result.scalars().all()  # Fetch all matching records

    if attendance_data == []:
        return "No data found"

    return attendance_data


# get present attendance data by current date
@router.get("/attendance/get_present_attendance_data")
async def get_present_attendance_data( db: db_dependency):


    # Query to fetch attendance data based on status and date
    result = await db.execute(
        select(Attendance).where(Attendance.date == str(date.today()), Attendance.status == "PRESENT")
    )
    
    attendance_data = result.scalars().all()  # Fetch all matching records

    if attendance_data == []:
        return "No data found"

    return attendance_data


@router.get("/attendance/get_absent_attendance_data")
async def get_absent_attendance_data( db: db_dependency):


    # Query to fetch attendance data based on status and date
    result = await db.execute(
        select(Attendance).where(Attendance.date == str(date.today()), Attendance.status == "ABSENT")
    )
    
    attendance_data = result.scalars().all()  # Fetch all matching records

    if attendance_data == []:
        return "No data found"

    return attendance_data


# update attendance by id



@router.patch("/attendance/update_individual_attendance_fields/{attendance_id}")
async def update_attendance(db: db_dependency, attendance_id: str, attendance_input: dict):
    
    logger.info("Endpoint: update_attendce called for attendance_id: %s", attendance_id)
    
    # Query for the user data
    attendance_data = await db.get(Attendance, uuid.UUID(attendance_id))
    # user_data = users.scalar()
    # old_username = user_data.username
    # print("old username : ", old_username)
    
    if not attendance_data:
        logger.error("User with ID %s not found", attendance_id)
        raise HTTPException(status_code=404, detail="Member not found")
    
    logger.info("Attendance data queried successfully for attendance_id: %s", attendance_id)
    
    # Convert user data and input into dictionaries
    converted_attendance_data = attendance_data.__dict__
    inputs = attendance_input


    # Only update fields that are present in both user data and input
    for key, value in inputs.items():
        if key in converted_attendance_data and value is not None: 
            # print("key : ", key)
            # print("value :", value) # Avoid updating with `None` values
            setattr(attendance_data, key, value)
    
    logger.info("Member data ready for storage for attendance_id: %s", attendance_id)
    
   
    await db.commit()
    
    

    
    logger.info("Member data updated successfully for attendance_id: %s", attendance_id)
    
    return attendance_data
    
    



# delete user

@router.delete("/attendance/delete_attendance_by_id")
async def delete_attendance_by_id(attendnance_id: uuid.UUID, db: db_dependency):

    result = await db.execute(select(Attendance).where(Attendance.id == attendance_id))
    attendance = result.scalar_one_or_none()
    
    if attendance is None:
        raise HTTPException(status_code=404, detail="attendance not found")

    # Delete the user
    await db.delete(attendance)
    await db.commit()


    return "Attendance deleted successfully"



# download attendance
@router.get("/attendance/download_attendance_data")
async def download_attendance_data(db: db_dependency):

    attendance = await db.execute(select(Attendance).order_by(Attendance.id))
    attendance_data = attendance.scalars().all()
    ordered_attendance_data = [AttendanceResponse.from_orm(attendance) for attendance in attendance_data]  

    attendance_dicts = []
    for attendance in ordered_attendance_data:
        attendance_dict = {}
        for key, value in attendance.__dict__.items():
            if not key.startswith('_'):
                # If the value is a UUID, set the key as 'id' and convert the value to a string
                if isinstance(value, uuid.UUID):
                    attendance_dict['id'] = str(value)  # Change the key to 'id' and convert the UUID to a string
                else:
                    attendance_dict[key] = value
        attendance_dicts.append(attendance_dict)
        print ("the data before the sheet ",attendance_dicts)
    # Check if member_data is empty
    if not attendance_data:
        raise HTTPException(status_code=200, detail="No user data exists")

    # Generate Excel file
    file_path = generate_excel(attendance_dicts, "attendance_data")

    # Return the file using FastAPI's FileResponse
    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="attendance_data.xlsx")




# download attendance for a particular day
@router.get("/attendance/download_current_attendance_data")
async def download_current_attendance_data(db: db_dependency):

    attendance = await db.execute(select(Attendance).where(Attendance.date == str(date.today())))
    attendance_data = attendance.scalars().all()
    ordered_attendance_data = [AttendanceResponse.from_orm(attendance) for attendance in attendance_data]  

    attendance_dicts = []
    for attendance in ordered_attendance_data:
        attendance_dict = {}
        for key, value in attendance.__dict__.items():
            if not key.startswith('_'):
                # If the value is a UUID, set the key as 'id' and convert the value to a string
                if isinstance(value, uuid.UUID):
                    attendance_dict['id'] = str(value)  # Change the key to 'id' and convert the UUID to a string
                else:
                    attendance_dict[key] = value
        attendance_dicts.append(attendance_dict)
        print ("the data before the sheet ",attendance_dicts)
    # Check if member_data is empty
    if not attendance_data:
        raise HTTPException(status_code=200, detail="No user data exists")

    # Generate Excel file
    file_path = generate_excel(attendance_dicts, "attendance_data")

    # Return the file using FastAPI's FileResponse
    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="attendance_data.xlsx")



