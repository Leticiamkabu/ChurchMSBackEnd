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


from models.notificationModel import *
# from models.profileModel import *
# from models.itemsModel import *
from schemas.FirstTimersSchema import *
from database.databaseConnection import SessionLocal
from notification.sendSMS import *
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
special_prayer_or_counseling = ["BUSINESS", "HEALTH", "DELIVERANCE", "MARITAL", "EDUCATIONAL", "OTHERS" ]


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
                date = request.date,
                status = "VISITOR"
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

    first_timers = await db.execute(select(First_Timers))
    first_timers_data = first_timers.scalars().all()
    
    if first_timers_data  is None:
        raise HTTPException(status_code=404, detail="No first timers data exists", data = first_timers_data)
    
    return first_timers_data 


# Download first timers List
@router.get("/first_timers/get_all_first_timers")
async def get_all_first_timers( db: db_dependency):

   
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
async def update_first_timer( id: uuid.UUID ,db: db_dependency, status: str)

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
@router.get("/first_timers/update_first_timers_by_id/{id}")
async def update_first_timer( id: uuid.UUID ,db: db_dependency, request: FirstTimersSchema)
    first_timer_data = await db.get(FirstTimers, id)
    
    if first_timer_data  is None:
        raise HTTPException(status_code=404, detail="First Timer with id does not exist", data = first_timer_data)

    first_timer_data.name = request.name
    first_timer_data.popularName = request.popularName
    first_timer_data.phoneNumber = request.phoneNumber
    first_timer_data.whatsAppNumber = request.whatsAppNumber
    first_timer_data.houseLocation = request.houseLocation
    first_timer_data.purposeOfComing = request.purposeOfComing
    first_timer_data.contactHours = request.contactHours
    first_timer_data.specialPrayerOrCounseling = request.specialPrayerOrCounseling
    first_timer_data.counselor = request.counselor
    first_timer_data.date = request.date
    first_timer_data.updatedOn = datetime.today()

    await db.commit()
    # check if status is member, then add it to member table
    
    return first_timer_data



@router.delete("/first_timers/delete_first_timers_by_id")
async def delete_first_timers_by_id(id: uuid.UUID, db: db_dependency):

    result = await db.execute(select(First_Timers).where(First_Timers.id == id))
    first_timer = result.scalar_one_or_none()
    
    if first_timer is None:
        raise HTTPException(status_code=404, detail="First_timer not found")

    # Delete the user
    await db.delete(attendance)
    await db.commit()


    return "first_timer deleted successfully"
