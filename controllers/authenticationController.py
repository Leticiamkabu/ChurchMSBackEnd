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



from models.authenticationModel import *
# from models.profileModel import *
# from models.itemsModel import *
from schemas.authenticationSchema import *
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


Role = ["DATA CLERK", "ACCOUNTS", "ADMINISTRATOR" , "DEPARTMENTAL LEADERS" , "ADMIN"]
Privilege = ["Add members", "Create Users", "Get User Details" , "Take Attendance", "Get Attandance Overview", "Get Member Details" ,"Everything"]

# create user
@router.post("/auth/create_user")  # done connecting
async def create_user(db: db_dependency, user: CreateUserSchema):

    logger.info("Endpoint : create_user")

# check if the email already exist, it yes dont resister( todo)

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    if user.role not in Role:
        print(type(user.role))
        return "Role provided does not exist"

    

    for i in user.privileges:
        if i not in Privilege:
            print(i)
            return "Privileges provided does not exist"

    string_privileges = ','.join(user.privileges)
    
        
    print("pr ",string_privileges)
    user_data = User(
                email=user.email,
                firstname=user.firstname,
                lastname =user.lastname,
                phoneNumber=user.phoneNumber,
                password =hashed_password.decode('utf-8'),
                role = user.role,
                privileges = string_privileges,

            )
    

    db.add(user_data)
    await db.commit()

    

    logger.info("User created and saved in the database")


    logger.info("User Registeration Sucessful")
    return {"message": "User registeration successfully", "User": user_data}




# # create Admin
@router.post("/auth/create_admin")
async def create_admin_user( db: db_dependency):

    logger.info("Endpoint : create_admin_user")

       # create admin user 

    admin_password = "boss"
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
    admin_user_data = User(
                email= "kabuleticia36@gmail.com",
                firstname="so",
                lastname ="lo",
                phoneNumber="0556852683",
                password =hashed_password.decode('utf-8'),
                role ="ADMIN",
                privileges = "Everything",

            )
    

    

    db.add(admin_user_data)
    await db.commit()
    logger.info("Admin User created and saved in the database")


    logger.info("Admin User Registeration Sucessful")
    return {"message": "Admin User registeration successfully", "User": admin_user_data}






# login without token

@router.post("/auth/login")
async def login( db: db_dependency, user: LoginSchema):

    # Query for user data using email
    users = await db.execute(select(User).where(User.email == user.email))
    user_data = users.scalar()
    
    # Check if the user was found
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User data queried successfully")

    # Check if the password is valid
    is_valid = bcrypt.checkpw(user.password.encode('utf-8'), user_data.password.encode('utf-8'))

    if is_valid:
        logger.info("User login successful")

        user_data.lastLogedin = str(datetime.utcnow())
        await db.commit()
        return {"message": "User login successful", "data": user_data}

    else:
        raise HTTPException(status_code=400, detail="Incorrect password")
    


# login with token

@router.post("/auth/login_generate_token")
async def login_generate_token(login: LoginSchema, db: db_dependency):
    # Query for user data using email

    user = await db.execute(select(User).where(User.email == login.email))
    user_data = user.scalar()
    
    # Check if the user was found
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User data queried successfully")

    # Check if the password is valid
    is_valid = bcrypt.checkpw(login.password.encode('utf-8'), user_data.password.encode('utf-8'))

    if is_valid:
        # Generate token
        token = generate_characters()
        
        # Save token to the user data
        user_data.token = token
        db.add(user_data)
        await db.commit()
        logger.info("User token saved")

        # Return success message and token
        return {"message": "User token saved", "token": token,"data": user_data.id}

    else:
        raise HTTPException(status_code=400, detail="Incorrect password")


# verify token
@router.get("/auth/verify_login_token")
async def verify_login_token(token: str,user_id: uuid.UUID, db: db_dependency):

    # Query for user data using email
    user_data = await db.get(User, user_id)
    # user_data = user.scalar()
    
    # Check if the user was found
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User data queried successfully")

  
    if user_data.token == token:
        
        logger.info("User login successful")
        return {"message": "User login successful", "data": user_data}

    else:
        raise HTTPException(status_code=400, detail="Invalid token")
    





def generate_characters(length: int = 8) -> str:
    # Define the possible characters (alphanumeric)
    characters = string.ascii_letters + string.digits

    # Generate a random string of the specified length
    random_characters = ''.join(random.choice(characters) for _ in range(length))
    
    return random_characters




# get all users
@router.get("/auth/get_all_users")
async def get_all_users( db: db_dependency):

    users = await db.execute(select(User))
    users_data = users.scalars().all()
    
    if users_data  is None:
        raise HTTPException(status_code=200, detail="No user data exists", data = users_data)
    
    return users_data 
    


# get user by id
@router.get("/auth/get_user_by_id/{user_id}")
async def get_all_users( user_id: uuid.UUID ,db: db_dependency):

    user_data = await db.get(User, user_id)
    
    
    if user_data  is None:
        raise HTTPException(status_code=200, detail="user with id does not exist", data = user_data)
    
    return user_data



@router.get("/auth/get_user_count") # d
async def get_user_count( db: db_dependency):

    
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()  
    
    result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "DATA CLERK")
    )
    data_clerk = result.scalar()
    
    result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "ACCOUNTS")
    )
    accounts = result.scalar()

    result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "ADMINISTRATOR")
    )
    administrator = result.scalar()

    result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "DEPARTMENTAL LEADERS")
    )
    departmentLeaders = result.scalar()

    result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "ADMIN")
    )
    admin = result.scalar()


    return {"total_users": total_users, "data_clerk": data_clerk, "accounts": accounts, "administrator": administrator, "departmentLeaders": departmentLeaders , "admin": admin }


# # get user details by usename
# @router.get("/auth/get_user_by_username/{username}")
# async def get_users_by_username( username: str ,db: db_dependency):

#     user = await db.execute(select(User).where(User.username == username))
#     user_data = user.scalar()
    
#     if user_data  is None:
#         raise HTTPException(status_code=200, detail="user with provided username does not exist", data = user_data)
    
#     return user_data




# get users by role
@router.get("/auth/get_users_by_role")
async def get_users_by_role( role: str ,db: db_dependency):

    if role not in Role:
        print(role)
        return "Role provided does not exist"

    user = await db.execute(select(User).where(User.role == role))
    user_data = user.scalars().all()
    
    
    if user_data  is None:
        raise HTTPException(status_code=200, detail="users with role does not exist", data = user_data)
    
    return user_data




# get total number of users
@router.get("/auth/get_total_number_of_users")
async def get_total_number_of_users(db: db_dependency):

    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()  

    return {"total_users": total_users}




# get number of users by role
@router.get("/auth/get_total_number_of_users_by_role")
async def get_total_number_of_users_by_role(role: str, db: db_dependency):

    if role not in Role:
        print(role)
        return "Role provided does not exist"

    result = await db.execute(select(func.count(User.id)).where(User.role == role))
    total_users_by_role = result.scalar()

    if total_users_by_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    return {f"total_number_of_{role}_users": total_users_by_role}




# update user by id



@router.patch("/auth/update_individual_user_fields/{user_id}")
async def update_user(db: db_dependency,user_id: str, user_input: CreateUserSchema):
    
    logger.info("Endpoint: update_user called for user_id: %s", user_id)
    
    # Query for the user data
    user_data = await db.get(User, uuid.UUID(user_id))
   
    
    if not user_data:
        logger.error("User with ID %s not found", user_id)
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User data queried successfully for user_id: %s", user_id)
    
    hashed_password = bcrypt.hashpw(user_input.password.encode('utf-8'), bcrypt.gensalt())
    # Convert user data and input into dictionaries
    converted_user_data = user_data.__dict__
    user_input.privileges = ','.join(user_input.privileges)
    user_input.password = hashed_password.decode('utf-8')
    inputs = user_input.__dict__


    
    # Only update fields that are present in both user data and input
    for key, value in inputs.items():
        if key in converted_user_data and value is not None: 
            setattr(user_data, key, value)
    
    logger.info("User data ready for storage for user_id: %s", user_id)
    

    await db.commit()
    

    
    logger.info("User data updated successfully for user_id: %s", user_id)
    
    return user_data
    
    



# delete user

@router.delete("/auth/delete_user_by_id/{user_id}")
async def delete_user_by_id(user_id: uuid.UUID, db: db_dependency):

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user
    await db.delete(user)
    await db.commit()


    return "User deleted successfully"
