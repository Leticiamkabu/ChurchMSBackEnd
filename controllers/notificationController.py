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
from schemas.notificationSchema import *
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




notification_type = ["SMS", "BULK_SMS", "SCHEDULE_MESSAGE" ]
@router.post("/notification/send/individual_sms")
async def send_sms_notification(db: db_dependency, request: SMSRequestSchema):

    if request.notificationType not in notification_type:
        print(request.notificationType)
        return "Notification type provided does not exist"

    try:
        print("number" ,request.to )
        print("message" ,request.message)
        
        # 233552285103
        sms_response = await send_sms(request.to, request.message)


        notification_data = Notification(
                notificationType = request.notificationType,
                recipient = request.to,
                message = request.message,
                
            )
    
        print(notification_data)
        db.add(notification_data)
        await db.commit()

        if sms_response.get("status") != 'success':
            logger.info("SMS Message not sent")
            return {"message": "SMS Message not sent", "error" : sms_response.get("message")}
        

        logger.info("SMS Message sent Sucessfully")
        return {"message": "SMS Message sent Sucessfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# check if there is a way to send bulk messages in a go than multiple request
@router.post("/notification/send/bulk_sms")
async def send_bulk_sms_notification(db: db_dependency, request: BulkSMSRequestSchema):

    if request.notificationType not in notification_type:
        print(request.notificationType)
        return "Notification type provided does not exist"

    try:
        
        recipients_str = ",".join(request.recipient)
        print(recipients_str)
        print("message" ,request.message)

        bulk_sms_response = await send_bulk_sms(recipients_str , request.message)

        notification_data = Notification(
            notificationType= request.notificationType,
            recipient = recipients_str,
            message = request.message
                
        )
    

        db.add(notification_data)
        await db.commit()

      

        logger.info(" Bulk SMS Message processed Sucessfully")
        return {"message": "Bulk SMS Message processed Sucessfully",
                "recipients": recipients_str,
                "total_recipients": len(request.recipient),
                 }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# FILE_PATH = "notification/scheduledMessages.json"
# @router.post("/notification/store-message")
# async def store_message(msg: ScheduledSMSMessageRequestSchema):
#     message_data = msg.dict()
#     message_data["storedAt"] = datetime.now().isoformat()

#     # Load existing messages
#     if os.path.exists(FILE_PATH):
#         with open(FILE_PATH, "r") as f:
#             messages = json.load(f)
#     else:
#         messages = []

#     # Add new message
#     messages.append(message_data)

#     # Sort by scheduledTime
#     messages.sort(key=lambda x: x["scheduledTime"])

#     # Save back to file
#     with open(FILE_PATH, "w") as f:
#         json.dump(messages, f, indent=4)

#     return {"message": "Message stored and sorted by scheduled time"}


@router.post("/notification/store_scheduled_messages")
async def store_scheduled_messages(db: db_dependency, scheduledMessage: ScheduledSMSMessageRequestSchema):
    
    logger.info(" About to store scheduled messages ")

    if scheduledMessage.notificationType not in notification_type:
        print(request.notificationType)
        return "Notification type provided does not exist"

    newScheduledMessage = ScheduledMessages(
        notificationType = scheduledMessage.notificationType,
        recipient = scheduledMessage. recipient,
        message = scheduledMessage.message,
        sendTime = scheduledMessage.scheduledTime,
        messageStatus = "PENDING",
        senderId = scheduledMessage.sender,
        createdOn = datetime.today()

    )

    db.add()
    await db.commit()

    logger.info(" Scheduled Message stored in db ")
    return {"message": "Message stored in db"}


@router.post("/notification/send/scheduled_sms_message")
async def send_scheduled_sms_message_notification(request: SendScheduledSMSRequestSchema, sendTime: str):

    logger.info(" About to send available scheduled messages ")

    logger.info(" Gettingsender phone number for alert ")
    result = await db.execute(
                select(User).where(str(User.id) == request.senderId)
            )
    scheduled_message_user = result.scalar()

    try:

    # Send
        response = "Sent"
        recipients_str = ",".join(request.recipient)
        print(recipients_str)
        print("number" ,recipients_str)
        print("message" ,request.message)
        
        # 233552285103
        sms_response = await send_sms(recipients_str, request.message)


        if sms_response.get("status") != 'success':

            response = "Not Sent"

            logger.info(f"SMS scheduled Message not sent, error: {sms_response.get('message')}")
        

        # save message status
        result = await db.execute(
                select(ScheduledMessages).where(str(ScheduledMessages.id) == request.id)
            )
        scheduled_message_data = result.scalar() 
        scheduled_message_data.messageStatus = response

        db.add(scheduled_message_data) 
        await db.commit()

        # send notification to message sender of the sending response
        sms_response = await send_sms(scheduled_message_user.phoneNumber, f"Your scheduled message has a status of {response}")

        logger.info("SMS Message sent Sucessfully")
        return {"message": "SMS Message processed Sucessfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get the message 

# save it in the dm

# check the database evry day to see if there re available smessages to be sent

# if there are , we get the list of messages and start to shedule message sent at that time

# the after a meaase is sent the list is cheked and the next near time and its message are taken

# when  message is sent the status changes to messae sent depending on the response

# if the message is not sent or sent an sms is sent to the message creator of the status
    if request.notificationType not in notification_type:
        print(request.notificationType)
        return "Notification type provided does not exist"

    try:

        scheduled_time = datetime.fromisoformat(request.scheduledTime)
        now = datetime.now()

        if scheduled_time <= now <= scheduled_time + timedelta(minutes=5):
            print("yes")
        
            recipients_str = ",".join(request.recipient)
            print(recipients_str)
            print("message" ,request.message)

            bulk_sms_response = await send_bulk_sms(recipients_str , request.message)

            notification_data = Notification(
                notificationType= request.notificationType,
                recipient = recipients_str,
                message = request.message
                    
            )
        

            db.add(notification_data)
            await db.commit()

        

            logger.info(" Scheduled SMS Message processed Sucessfully")
            return {"message": "Scheduled SMS Message processed Sucessfully",
                    "recipients": recipients_str,
                    "total_recipients": len(request.recipient),
                    }

        elif now > scheduled_time + timedelta(minutes=5):
            return {"message": "Time passed. SMS not sent."}

        else:
            return {"message": "Too early to send SMS."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/notification/check_scheduled_sms_message")
# every 6 am
async def check_scheduled_sms_message():

    logger.info("Endpoint : checking for scheduled messages")
    # 2025-07-18 10:00:00
    # '2025-07-29'
    result = await db.execute(
        select(ScheduledMessages).where(
            func.date(ScheduledMessages.sendTime) == str(date.today()),
            ScheduledMessages.status == "Not sent")
            .order_by(desc(ScheduledMessages.sendTime))
    )
    scheduled_message_data = result.scalar() 

    if scheduled_message_data == None:
        return "No messages found for today"

# create a new cron jobs with the messages
    # for i in scheduled_message_data:

    request = SendScheduledSMSRequestSchema(
        recipient = list(scheduled_message_data[0].recipient),
        message = scheduled_message_data[0].message,
        senderId =scheduled_message_data[0].senderId
    )

    sendTime =scheduled_message_data[0].senderTime[11,18]
    # schedule message
    scheuled_message_response = send_scheduled_sms_message_notification(request, sendTime)
 
    # scheuled_message_response.status_code == 200:


    return scheduled_message_data
