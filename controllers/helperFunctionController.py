from fastapi import APIRouter, Depends, HTTPException, FastAPI, HTTPException 
from typing import Annotated
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import select, or_, func, and_, create_engine, MetaData, Table, update, null, insert , inspect
from sqlalchemy.sql import func , extract
from sqlalchemy.engine.result import Row
from dotenv import load_dotenv

import logging
import os
import subprocess
import tempfile
from fastapi import UploadFile,status, File, Form, Request



# create a connection to the database
async def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]




router = APIRouter()

# Load environment variables from .env file
load_dotenv()

# Fetch database credentials from environment variables
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')




@router.post("/helperFunction/clean_data_base/{table_name}")
async def replace_null_values_in_the_database(table_name: str):

    DATABASE_URL = "postgresql://ctc_dev_17ay_user:uIuAVJQQF1TirGjb6uxb1UyaAWIryzPA@dpg-d3ioso6mcj7s739e79j0-a.oregon-postgres.render.com/ctc_dev_17ay"

    # DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()
    metadata = MetaData()

    try:
        # Reflect the table
        table = Table(table_name, metadata, autoload_with=engine)

        # Select all rows
        stmt = select(table)
        results = session.execute(stmt).fetchall()

        updated_rows = 0

        for row in results:
            update_data = {}
            colum_numbers = 0
            for column in table.columns:

                
                if row[colum_numbers] is None:
                    update_data[column.name] = ""
                colum_numbers += 1

        
            if update_data:
                upd = (
                    update(table)
                    .where(table.columns.id == row[0])
                    .values(**update_data)
                )
                session.execute(upd)
                updated_rows += 1

        session.commit()
        return {"message": f"{updated_rows} row(s) updated."}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# work on this soon

@router.post("/helperFunction/clone_db")
async def clone_db():
    try:
        # Dump source DB to temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            dump_file = tmpfile.name

        # Source DB credentials
        env = os.environ.copy()
        env["PGPASSWORD"] =  "leeminho"
        env["PGSSLMODE"] = "disable"

        dump_cmd = [
            "pg_dump",
            "-h",  "localhost",
            "-p", str(5432),
            "-U",  "postgres",
            "-d",  "churchMSDev",
            "-Fc",
            "--no-owner",
            "-f", dump_file
        ]
        subprocess.run(dump_cmd, check=True, env=env)

        # Target DB credentials
        env["PGPASSWORD"] =  "sOg4Ja1CNTTdlVr8j15HplPQJQyM94kz"
        env["PGSSLMODE"] = "require"

        restore_cmd = [
            "pg_restore",
            "-h", "dpg-d4s17dh5pdvs73btcoi0-a.oregon-postgres.render.com",
            "-p", str(5432),
            "-U", "ctc_dev_n0qw_user",
            "-d", "ctc_dev_n0qw",
            "--no-owner",
            "--no-acl", 
            "--clean",
            "--verbose",
            dump_file
        ]
        subprocess.run(restore_cmd, check=True, env=env)

        os.remove(dump_file)

        return {"status": "success", "message": "Database cloned succesfully"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/helperFunction/move_table_data")
async def data_transfere(table_name: str):   
    
        
    DESTINATION_DB_URL = "postgresql://leticia:leeminho@localhost/churchMSDev"
    SOURCE_DB_URL = "postgresql://ctc_dev_4mjf_user:TQarR3DpwZPAZieKlm2b9ccDDLfCDM6s@dpg-d29sksndiees738d04qg-a.oregon-postgres.render.com/ctc_dev_4mjf"

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

import aiofiles
from docx import Document
import io


def read_docx(doc):
    """Extracts name and department from a Word Document table."""
    data_list = []  # list of dicts for multiple rows

    # Check if the document has tables
    if not doc.tables:
        return {"error": "No tables found in document"}

    table = doc.tables[0]  # assuming first table contains your data

    # Get headers from first row
    headers = [cell.text.strip().upper() for cell in table.rows[0].cells]

    # Check required columns
    if "NAME" not in headers or "DEPARTMENT" not in headers:
        return {"error": "Table must contain 'NAME' and 'DEPARTMENT' columns"}

    name_idx = headers.index("NAME")
    dept_idx = headers.index("DEPARTMENT")

    # Read remaining rows
    for row in table.rows[1:]:
        name = row.cells[name_idx].text.strip()
        department = row.cells[dept_idx].text.strip()
        data_list.append({"NAME": name, "DEPARTMENT": department})

    return data_list


import psycopg2
from psycopg2 import OperationalError
# postgresql://ctc_dev_n0qw_user:sOg4Ja1CNTTdlVr8j15HplPQJQyM94kz@dpg-d4s17dh5pdvs73btcoi0-a.oregon-postgres.render.com/ctc_dev_n0qw
def get_connection():
    """Safely connect to the Render PostgreSQL database with SSL enabled."""
    SOURCE_DB_URL = (
        "postgresql://ctc_dev_n0qw_user:"
        "sOg4Ja1CNTTdlVr8j15HplPQJQyM94kz@"
        "dpg-d4s17dh5pdvs73btcoi0-a.oregon-postgres.render.com/"
        "ctc_dev_n0qw?sslmode=require"
    )
    try:
        conn = psycopg2.connect(SOURCE_DB_URL)
        return conn
    except OperationalError as e:
        print("⚠️ Database connection failed:", e)
        return None


def update_department_in_db(name, department):
    """Updates department for a given employee name in the database."""
    conn = get_connection()
    if not conn:
        return {"status": "error", "message": "Failed to connect to database"}

    cursor = conn.cursor()

    try:
        # Normalize name (lowercase + remove spaces)
        clean_name = name.replace(" ", "").lower().strip()

        # Find matching members
        cursor.execute("""
            SELECT id, "firstName", "middleName", "lastName"
            FROM members
            WHERE LOWER(TRIM("lastName" || COALESCE("middleName", '') || "firstName")) = %s
        """, (clean_name,))

        records = cursor.fetchall()

        if len(records) == 0:
            msg = f"No record found for {name}"
            return {"status": "none", "message": msg}

        elif len(records) > 1:
            msg = f"Multiple records found for {name}, skipping update."
            return {"status": "multiple", "message": msg}

        # Exactly one match → update department
        member_id = records[0][0]
        cursor.execute(
            'UPDATE members SET "departmentName" = %s WHERE id = %s',
            (department, member_id),
        )
        conn.commit()

        msg = f"Department updated for {name}"
        return {"status": "updated", "message": msg}

    except OperationalError as e:
        msg = f"Database operation failed for {name}: {e}"
        print("⚠️", msg)
        return {"status": "error", "message": msg}

    finally:
        cursor.close()
        conn.close()

import time

@router.post("/helperFunction/updateDepartment")
async def department_data_update(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        return {"error": "Invalid file type. Please upload a .docx file"}

    contents = await file.read()
    doc = Document(io.BytesIO(contents))
    data = read_docx(doc)
    print("Extracted data:", data)

    if "NAME" not in data[0] or "DEPARTMENT" not in data[0]:
        return {"error": "Document must contain 'Name:' and 'Department:' fields"}

    # result = update_department_in_db(data["NAME"], data["DEPARTMENT"])

    for row in data:
        print("rowss : ", row )
        name = row.get("NAME")
        department = row.get("DEPARTMENT")

        if not name or not department:
            results.append({"name": name, "status": "error", "message": "Missing name or department"})
            continue

        update_result = update_department_in_db(name, department)
        time.sleep(20) 

    # Return the appropriate message based on status
        if update_result["status"] == "updated":
            print("message:", update_result["message"], "department:", row.get("DEPARTMENT"))
        else:
            print("error:", update_result["message"], "department:", row.get("DEPARTMENT"))




# postgresql://ctc_dev_as4o_user:yIIfvLFHsyAMI8vIIWgs2xLbrxiTzAk0@dpg-d46qubc9c44c738m52v0-a.oregon-postgres.render.com/ctc_dev_as4o