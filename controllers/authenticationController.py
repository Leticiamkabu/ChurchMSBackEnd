from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
import uuid
import os

from datetime import datetime, date
from sqlalchemy import select, or_, func, create_engine, MetaData, Table
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
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


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


Role = ["DATA CLERK", "ACCOUNTS", "ADMINISTRATOR" , "DEPARTMENTAL LEADERS" , "ADMIN", "GUEST"]
Privilege = ['ADMIN PRIVILEGES', 'DATA CLERK PRIVILEGES', 'ADMINISTRATOR PRIVILEGES', 'GUEST PRIVILEGES']

# create user
@router.post("/auth/create_user")  # done connecting
async def create_user(db: db_dependency, user: CreateUserSchema):

    logger.info("Endpoint : create_user")

# check if the email already exist, it yes dont resister( todo)
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    attendance_data = result.scalar()

    if attendance_data :
        return "Email already exist"

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    if user.role not in Role:
        print(type(user.role))
        return "Role provided does not exist"

    if user.privileges not in Privilege:
        print(type(user.role))
        return "Privileges provided does not exist"

        
    
    user_data = User(
                email=user.email,
                firstName=user.firstName,
                lastName =user.lastName,
                phoneNumber=user.phoneNumber,
                password =hashed_password.decode('utf-8'),
                role = user.role,
                privileges = user.privileges,

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
                firstName="so",
                lastName ="lo",
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
        raise HTTPException(status_code=401, detail="Invalid Credential")
    
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

    if user_data.password != user_input.password:
        hashed_password = bcrypt.hashpw(user_input.password.encode('utf-8'), bcrypt.gensalt())
        user_input.password = hashed_password.decode('utf-8')
    
    
    # Convert user data and input into dictionaries
    converted_user_data = user_data.__dict__
    user_data.updated = datetime.today()
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




import collections

from sqlalchemy import create_engine, MetaData, Table, select, insert , inspect
from sqlalchemy.engine.result import Row
@router.post("/move_table")
async def data_transfere(table_name: str):   
    
        

    # Replace these with your actual database connection URLs
    # SOURCE_DB_URL = 'postgresql://my_say_user:tbcPzQkvP3WCD44NnRG6vrQz9kCMbZqD@dpg-cls55tjip8as73a3duug-a.oregon-postgres.render.com/my_say'
    # DESTINATION_DB_URL = 'postgresql://dbmaster:U49531PObSfZ@10.0.30.15:5432/mysay'

    SOURCE_DB_URL = "postgresql://leticia:leeminho@localhost/churchMSLocal"
    # DESTINATION_DB_URL = "postgresql://leticia:leeminho@localhost/churchMSProd"
    DESTINATION_DB_URL = "postgresql://ctc_dev_12gt_user:D47MC1Bq7TIgU4S6cQg41w5XFrXDoo2O@dpg-d0am3nur433s73da1uhg-a.oregon-postgres.render.com/ctc_dev_12gt"

    #postgresql://ctc_dev_12gt_user:D47MC1Bq7TIgU4S6cQg41w5XFrXDoo2O@dpg-d0am3nur433s73da1uhg-a.oregon-postgres.render.com/ctc_dev_12gt

    # Replace 'your_table_name' with the actual table name you want to transfer
    TABLE_NAME = table_name

    # Set up the engines and metadata
    source_engine = create_engine(SOURCE_DB_URL)
    destination_engine = create_engine(DESTINATION_DB_URL)
    metadata = MetaData()

    # Reflect the table from the source database
    source_table = Table(TABLE_NAME, metadata, autoload_with=source_engine)

    # Connect to both databases
    with source_engine.connect() as source_conn, destination_engine.connect() as dest_conn:
        # Start a transaction in the destination database
        with dest_conn.begin():
             # Check if the destination table exists using the inspector
            inspector = inspect(destination_engine)
            if TABLE_NAME in inspector.get_table_names():
                print(f"Table '{TABLE_NAME}' exists in the destination database.")
                destination_table = Table(TABLE_NAME, metadata, autoload_with=destination_engine)
            else:
                print(f"Table '{TABLE_NAME}' does not exist. Creating table...")
                # Define the schema based on the source table
                destination_table = Table(
                    TABLE_NAME,
                    metadata,
                    *(Column(col.name, col.type, primary_key=col.primary_key) for col in source_table.columns),
                    extend_existing=True

                )
                metadata.create_all(destination_engine)

            # Load data from the source table
            print("Fetching data from source table...")
            select_st = select(source_table)
            results = source_conn.execute(select_st).fetchall()

            # Insert data into the destination table
            print(f"Transferring {len(results)} rows to destination table...")
            for row in results:
                # Convert Row object to dictionary
                row_dict = dict(row._asdict())

                # Insert data into the destination table
                insert_st = insert(destination_table).values(**row_dict)
                dest_conn.execute(insert_st)

    print("Data transfer complete.")
    return "Data transfer complete."






    # Tracking user activities

    # ACTIVE

# create member
@router.post("/auth/user_tracking")  # done connecting
async def create_user_traker(db: db_dependency, loginTrack: UserLoginTrackerSchema):

    user_data = await db.get(User, uuid.UUID(loginTrack.userId))

    if user_data  is None:
        raise HTTPException(status_code=200, detail="User with id does not exist", data = user_tracker_data)
    

    result = await db.execute(
        select(UserLoginTracker).where(UserLoginTracker.userId == loginTrack.userId, UserLoginTracker.logOutTime == "NOT_SET")
    )
    user_tracker_data = result.scalars().all() 

    if user_tracker_data :
        raise HTTPException(status_code=200, detail="User with id is already logged in")
    


    user_track = UserLoginTracker(
        firstName = user_data.firstName,
        lastName= user_data.lastName,
        status= loginTrack.status,
        role= user_data.role,
        logInTime=loginTrack.logInTime,
        logOutTime="NOT_SET",
        userId=loginTrack.userId,
        date=str(date.today()),
        createdOn=datetime.today(),
    )

    db.add(user_track)
    await db.commit()

    logger.info("User activitity tracking successful.")
    return {"message": "User activitity tracking successful", "User tracking data": user_track}
    

@router.get("/auth/get_all_user_tracking")  # done connecting
async def get_user_traker(db: db_dependency):

    result = await db.execute(
        select(UserLoginTracker).where(UserLoginTracker.date == str(date.today()))
    )
    user_tracker_data = result.scalars().all() 

    if user_tracker_data  is None:
        raise HTTPException(status_code=200, detail="User tracker data not found", data = user_tracker_data)
    print(user_tracker_data)
    return user_tracker_data


@router.patch("/auth/update_user_tracking/{user_id}/{logOutTime}")  # done connecting
async def update_user_traker(db: db_dependency, user_id : str, logOutTime : str):

    result = await db.execute(
        select(UserLoginTracker).where(UserLoginTracker.userId == user_id, UserLoginTracker.logOutTime == "NOT_SET")
    )
    user_tracker_data = result.scalars().all() 

    if user_tracker_data  is None:
        raise HTTPException(status_code=200, detail="User tracker with empty updated date does not exist", data = user_tracker_data)

    for tracker in user_tracker_data:
        tracker.logOutTime = logOutTime
        tracker.status = "INACTIVE"
        tracker.updatedOn = str(datetime.today())

    await db.commit()
    
    logger.info("User activitity tracking updated successfully.")
    return {"message": "User activitity tracking updated successfully", "User tracking data": user_tracker_data}