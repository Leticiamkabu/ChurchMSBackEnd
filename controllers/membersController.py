from fastapi import APIRouter, Depends, HTTPException 
from typing import Annotated
from sqlalchemy.orm import Session
import uuid
from fastapi.responses import FileResponse 
from datetime import datetime, date
from sqlalchemy import select, or_, func, and_,update
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
from helperFunctions.exportFile import *

# file upload
from fastapi import UploadFile,status, File, Form
# from utils.minio_util import upload_file

import re
from sqlalchemy.sql import func , extract
from pathlib import Path


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

    result = await db.execute(select(func.count(Member.id)))
    count = result.scalar() 
    
    if member.dateOfBirth != "":
        age = int(date.today().strftime("%Y")) - int(member.dateOfBirth[0:4])
    else:
        age = member.age

    member_data = Member(
                memberID = generatedId(count),
                title=member.title,
                firstName=member.firstName,
                middleName=member.middleName,
                lastName =member.lastName,
                dateOfBirth = member.dateOfBirth,
                age = age,
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
                spiritualGift = member.spiritualGift,
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
async def create_member_image(db: db_dependency, fullName : str = Form(...),  file: UploadFile = File(...)):

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
        fullName = fullname,  # Use new_item_data.id here
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

    member = await db.execute(select(Member).order_by(Member.id))
    member_data = member.scalars().all()

    
    if member_data  is None:
        raise HTTPException(status_code=200, detail="No user data exists", data = member_data)
    
    return [MemberResponse.from_orm(member) for member in member_data]  
    

@router.get("/members/get_all_members_file")
async def get_all_members(db: db_dependency):

    member = await db.execute(select(Member).order_by(Member.id))
    member_data = member.scalars().all()
    ordered_member_data = [MemberResponse.from_orm(member) for member in member_data]  

    member_dicts = []
    for member in ordered_member_data:
        member_dict = {}
        for key, value in member.__dict__.items():
            if not key.startswith('_'):
                # If the value is a UUID, set the key as 'id' and convert the value to a string
                if isinstance(value, uuid.UUID):
                    member_dict['id'] = str(value)  # Change the key to 'id' and convert the UUID to a string
                else:
                    member_dict[key] = value
        member_dicts.append(member_dict)
        print ("the data before the sheet ",member_dicts)
    # Check if member_data is empty
    if not member_data:
        raise HTTPException(status_code=200, detail="No user data exists")

    # Generate Excel file
    file_path = generate_excel(member_dicts, "member_data")

    # Return the file using FastAPI's FileResponse
    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="member_data.xlsx")


# get member by id
@router.get("/members/get_member_by_id/{member_id}")
async def get_member_by_id( member_id: uuid.UUID ,db: db_dependency):

    member_data = await db.get(Member, member_id)
    
    
    if member_data  is None:
        raise HTTPException(status_code=200, detail="user with id does not exist", data = member_data)
    
    return member_data


# get member by id
@router.get("/members/sort_member_data/{age}/{department}/{bithMonth}")
async def get_member_by_id( member_id: uuid.UUID ,db: db_dependency):

    member_data = await db.get(Member, member_id)
    
    
    if member_data  is None:
        raise HTTPException(status_code=200, detail="user with id does not exist", data = member_data)
    
    return member_data



# get member by words
@router.get("/members/get_member_by_words/{words}")
async def get_member_by_words( words: str ,db: db_dependency):

    name = words.split()

    search_conditions = [
    or_(
        Member.firstName.ilike(f"%{word}%"),
        Member.middleName.ilike(f"%{word}%"),
        Member.lastName.ilike(f"%{word}%")
    )
    for word in name
]

    query = select(Member).filter(*search_conditions)
# results = query.all()

    # Modify the query to check if the search string is present in firstname, lastname, or email
    # query = select(Member).where(
    #     or_(
    #         Member.firstname.ilike(f"%{words}%"),  # Case-insensitive match
    #         Member.lastname.ilike(f"%{words}%"),
    #         Member.middlename.ilike(f"%{words}%")
    #     )
    # )

    # Execute the query
    result = await db.execute(query)
    members_data = result.scalars().all()
    # user = await db.execute(select(User).where(User.role == role))
    # user_data = user.scalars().all()
    
    
    if members_data  == []:
        raise HTTPException(status_code=200, detail="Members with the given names do not exist" )
    
    return members_data




# get total number of members
@router.get("/members/get_total_number_of_members")
async def get_total_number_of_members(db: db_dependency):

    result = await db.execute(select(func.count(Member.id)))
    total_members = result.scalar()  

    return {"total_members": total_members}







# update member by id



@router.patch("/members/update_individual_member_fields/{member_id}")
async def update_member(db: db_dependency,member_id: str, member_input: MemberSchema):
    
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
    converted_member_data.updatedOn = datetime.today()
    inputs = member_input.__dict__


    # Only update fields that are present in both user data and input
    for key, value in inputs.items():
        if key in converted_member_data and value is not None: 
            # print("key : ", key)
            # print("value :", value) # Avoid updating with `None` values
            setattr(member_data, key, value)
    
    logger.info("Member data ready for storage for member_id: %s", member_id)
    
   
    await db.commit()
    
    

    
    logger.info("Member data updated successfully for member_id: %s", member_id)
    
    return {"message": "Member details update successful", "Member": member_data}
    
    



# delete user

@router.delete("/members/delete_member_by_id/{member_id}")
async def delete_member_by_id(member_id: uuid.UUID, db: db_dependency):

    result = await db.execute(select(Member).where(Member.id == member_id))
    member = result.scalar_one_or_none()
    
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    # Delete the user
    await db.delete(member)
    await db.commit()


    return "Member deleted successfully"


# download members
@router.get("/members/download_member_data/{format}")
async def download_member_data(db: db_dependency, format : str):

    if format != "Excel" and format != "Docx":
        raise HTTPException(status_code=400, detail="File format does not exist")

    member = await db.execute(select(Member).order_by(Member.id))
    member_data = member.scalars().all()
    ordered_member_data = [MemberResponse.from_orm(member) for member in member_data]  

    member_dicts = []
    for member in ordered_member_data:
        member_dict = {}
        for key, value in member.__dict__.items():
            if not key.startswith('_'):
                # If the value is a UUID, set the key as 'id' and convert the value to a string
                if isinstance(value, uuid.UUID):
                    member_dict['id'] = str(value)  # Change the key to 'id' and convert the UUID to a string
                else:
                    member_dict[key] = value
        member_dicts.append(member_dict)
        # print ("the data before the sheet ",member_dicts)
    # Check if member_data is empty
    if not member_data:
        raise HTTPException(status_code=200, detail="No user data exists")

    if format == "Excel":
        # Generate Excel file
        file_path = generate_excel(member_dicts, "member_data")
        media_Type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file_Name = "member_data.xlsx"

    elif format == "Docx":
        file_path = generate_excel(member_dicts, "member_data")
        media_Type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file_Name = "member_data.docs"


    # Return the file using FastAPI's FileResponse
    return FileResponse(file_path, media_type = media_Type, filename = file_Name)
# {'title': '', 'firstName': 'Millicent', 'middleName': '', 'lastName': 'Ocloo', 'dateOfBirth': '', 'age': '', 'gender': 'Female', 'phoneNumber': '0592634014', 'email': '', 'nationality': '', 'homeTown': '', 'homeAddress': 'Kordiabe', 'workingStatus': '', 'occupation': '', 'qualification': '', 'institutionName': '', 'mothersName': '', 'fathersName': '', 'nextOfKin': '', 'nextOfKinPhoneNumber': '', 'maritalStatus': '', 'spouseContact': '', 'spouseName': '', 'numberOfChildren': '', 'memberType': '', 'cell': '', 'departmentName': '', 'dateJoined': '', 'classSelection': '', 'spiritualGift': '', 'position': '', 'waterBaptised': '', 'baptisedBy': '', 'dateBaptised': '', 'baptisedByTheHolySpirit': '', 'memberStatus': '', 'dateDeceased': '', 'dateBuried': '', 'confirmed': '', 'dateConfirmed': '', 'comment': ''}



# sort member data
@router.get("/members/sort_member_data/{age}/{ageRange}/{department}/{birthMonth}")
async def sort_member_data(db: db_dependency, age: str, ageRange: str, department:str, birthMonth:str):

    # Collect optional filters
    filters = []

    # Add filters based on optional inputs
    if age != "a":  # If a date is provided
        filters.append(Member.age == age)
    if department != "d":  # If a date is provided
        filters.append(Member.departmentName == department)
    if ageRange != "ar":
        # "1,2"  # If a specific status is provided
        ranges = list(map(int, ageRange.split(",")))
        filters.append(and_(Member.age >= str(ranges[0]), Member.age <= str(ranges[1])))
    if birthMonth != "bm":
        # "07"  # If a specific status is provided
        filters.append(func.substr(Member.dateOfBirth, 6, 2) == birthMonth)

    member = await db.execute(select(Member).where(and_(*filters))) 
    member_data = member.scalars().all()
    ordered_member_data = [MemberResponse.from_orm(member) for member in member_data]  

    return ordered_member_data

    

# create member
@router.post("/members/update_member_image/{name}")  # done connecting
async def update_member_image(db: db_dependency, fullname : str = Form(...),  file: UploadFile = File(...)):

    logger.info("Endpoint : update_member_image")

    memberImageData = await db.execute(select(MemberImage).where(MemberImage.fullname == fullname))
    memberImageData_data = memberImageData.scalar()

    print("sdfghj", memberImageData_data)
    
    if memberImageData_data  == None:
        raise HTTPException(status_code=200, detail="Member Image with name does not exist")

    # Validate file type (e.g., images only)
    allowed_file_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_file_types:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed types: jpeg, png, gif.")
    
    #  Read the file content as binary data
    member_image_data = await file.read()
    
    # Convert to Base64
    image_base64 = base64.b64encode(member_image_data).decode('utf-8')


    memberImageData.image = image_base64
    memberImageData.image = file.filename
   
    
    
    await db.commit()
    
    logger.info("Member image updated and saved in the database with id %s ", memberImageData_data.id)

    return {"message": "Member image update successful", "member_image_id": memberImageData_data.id}





# create member
@router.get("/members/get_member_image/{fullname}")  # done connecting
async def get_member_image(db: db_dependency, fullname : str):

    logger.info("Endpoint : update_member_image")

    memberImageData = await db.execute(select(MemberImage).where(MemberImage.fullname == fullname))
    memberImageData_data = memberImageData.scalar()

    print("sdfghj", memberImageData_data)
    
    if memberImageData_data  == None:
        raise HTTPException(status_code=200, detail="Member Image with name does not exist")


    
    logger.info("Member image data queried successful . Data :  %s ", memberImageData_data)

    return {"message": "Member image data queried successful", "member_image_data": memberImageData_data}


def generatedId(lastNumber):
    id_constant = 'CTC_M_00'
    id_number = lastNumber + 1
    return id_constant + str(id_number)




# Function to Process Excel File
async def preprocess_excel(contents, filename):

#
    # Extract file extension safely
    file_extension = os.path.splitext(filename)[1].lower()

    # Ensure contents is not empty
    if not contents:
        raise ValueError("Uploaded file is empty.")

    # Read the Excel file based on extension
    if file_extension == ".xlsx":
        df = pd.read_excel(io.BytesIO(contents), engine="openpyxl")
    elif file_extension == ".xls":
        print("yes")
        print(pd.read_excel(io.BytesIO(contents), engine="xlrd"))
        df = pd.read_excel(io.BytesIO(contents), engine="xlrd")
        print(pd.read_excel(io.BytesIO(contents), engine="xlrd"))
    else:
        raise ValueError("Unsupported file format. Please upload an Excel file.") 

    # Normalize column names
    df.columns = [col.lower().strip() for col in df.columns]

    # Convert all text columns to string
    df = df.astype(str).applymap(lambda x: x.strip() if isinstance(x, str) else None)

    return df



    # import data to pupulate database
# import pandas as pd
# @router.post("/upload-excel/")
# async def upload_excel(db: db_dependency , file: UploadFile = File(...)):

#     try:
#         # Read the file into a pandas DataFrame
#         # Read the file content
#         contents = await file.read()
        
#         # Process the Excel file
#         df = await preprocess_excel(contents, file.filename )
#         # df = pd.read_excel(io.BytesIO(contents))

#         df_columns = [col.lower().strip() for col in df.columns]

#         memberColums = [colum.name for colum in Member.__table__.columns]
#         print(memberColums) 

#     # List to store processed records
#         processed_records = []

#         # Iterate through each row in the DataFrame
#         # for _, row in df.iterrows():
#         #     row_dict = {col: row[col] for col in df_columns if col in memberColums}
#         #     processed_records.append(row_dict)

#         # print(processed_records)

#         processed_records = []
#         for _, row in df.iterrows():
#             row_dict = {col: str(row[col]).strip() if pd.notna(row[col]) else None for col in df_columns if col in memberColums}
#             processed_records.append(row_dict)

#         print(processed_records )


#         for record in processed_records:
#         # Create a new Member instance with the processed data
#             new_member = Member(**record)  # Unpacking dictionary into Member fields
#             db.add(new_member)  # Add the new instance to the session
#         await db.commit()
   

#         # memberColums = [colum for colum in MemberSchema]
#         # print(memberColums)
#         # Validate required columns
#         # required_columns = {"name", "category", "price"}
#         # if not required_columns.issubset(df.columns):
#         #     raise HTTPException(status_code=400, detail=f"Missing required columns: {required_columns - set(df.columns)}")

#         # Insert data into the database
#         # for _, row in df.iterrows():
#         #     item = Item(name=row["name"], category=row["category"], price=row["price"])
#         #     db.add(item)
        
#         # db.commit()
#         return {"message": "Data inserted successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


def to_camel_case(snake_str):
    """Convert snake_case or other formats to camelCase"""
    components = re.split(r'[_\s]+', snake_str)  # Split by underscores or spaces
    return components[0].lower() + ''.join(x.capitalize() for x in components[1:])




from docx import Document
import io
@router.post("/members/upload-docx")
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
        new_members_list = []
        skiped_members_list = []
        for member_data in individuals_data:
            counts = counts + 1
            result = await db.execute(select(func.count(Member.id)))
            member_count = result.scalar()

            # print("yiiy",member_data)
            data = {to_camel_case(k): v for k, v in member_data.items() if k.strip()}
            print("hfjhfghj", data)

            conditions = []

            if data.get('firstName'):
                conditions.append(Member.firstName == data['firstName'])

            if data.get('middleName'):
                conditions.append(Member.middleName == data['middleName'])

            if data.get('lastName'):
                conditions.append(Member.lastName == data['lastName'])

            stmt = select(Member).where(and_(*conditions))

            result = await db.execute(stmt)
            existing_member = result.scalar_one_or_none()


            if existing_member:
                print("member exists")
                current_dept = existing_member.departmentName or ""
                new_dept = data['departmentName']
    
                if new_dept not in current_dept:
                    updated_dept = f"{current_dept}, {new_dept}" if current_dept else new_dept
                    await db.execute(
                        update(Member)
                        .where(Member.id == existing_member.id)
                        .values(departmentName=updated_dept)
                    )
                else:
                    skiped_members_list.append(data['firstName'] + data['middleName'] + data['lastName'])
                    pass
                    # raise HTTPException(status_code=500, detail="User and department name already exist")

            else:

                data["memberID"] = generatedId(member_count)
                print(data)
                new_members = Member(**data)
                new_members_list.append(new_members)
                db.add(new_members)
                await db.commit()
        
        return {"message": "Members added successfully", "total_members": len(new_members_list),"skiped_members": skiped_members_list} 

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")



#clean data function


# upload member sample document docx
@router.get("/members/download_sample_upload_data_document")
async def upload_docx():

    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = BASE_DIR/"sampleDataFormat/members/Sample_Data_for_Adding_Members.docx"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename="member_data_sample_document.docx")
    

@router.post("/members/test")
async def download_docx():
    file_path = generate_docx()

    return FileResponse(file_path, media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename = "test_data.docs")
