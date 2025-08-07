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

    # DATABASE_URL = f"postgresql://ctc_dev_06r2_user:c7jxzBBZTHTNeequSLRVLflYYhZo1Nq6@dpg-d1l00m15pdvs73bbq1og-a.oregon-postgres.render.com/ctc_dev_06r2"

    DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"
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
    # server_user: str, server_pass: str, server_host: str, server_db: str,server__port: str,table_name: str
    try:
        # Dump source DB to temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            dump_file = tmpfile.name

        # Set env for pg_dump
        env = os.environ.copy()
        env["PGPASSWORD"] = "leeminho"
        env["PGSSLMODE"] = "require" 

        # dump_cmd = [
        #     "pg_dump",
        #     "-h", "localhost",
        #     "-p", str(5432),
        #     "-U", "leticia",
        #     "-d", "churchMSDev",
        #     "-Fc",  # custom format for pg_restore
        #     "-f", dump_file
        # ]

        dump_cmd = [
            "pg_dump",
            "-h", "localhost",
            "-p", str(5432),
            "-U", "leticia",
            "-d", "churchMSDev",
            "-Fc",  # custom format for pg_restore
            "-f", dump_file
        ]

        subprocess.run(dump_cmd, check=True, env=env)

        # Create target database
        env["PGPASSWORD"] = "TQarR3DpwZPAZieKlm2b9ccDDLfCDM6s"
        env["PGSSLMODE"] = "require"
        # createdb_cmd = [
        #     "createdb",
        #     "-h", "dpg-d29sksndiees738d04qg-a.oregon-postgres.render.com",
        #     "-p", str(5432),
        #     "-U", "ctc_dev_4mjf_user",
        #     "ctc_dev_4mjf"
        # ]
        # subprocess.run(createdb_cmd, check=True, env=env)

        # Restore into target DB
        # restore_cmd = [
        #     "pg_restore",
        #     "-h", "dpg-d29sksndiees738d04qg-a.oregon-postgres.render.com",
        #     "-p", str(5432),
        #     "-U", "ctc_dev_4mjf_user",
        #     "-d", "ctc_dev_4mjf",
        #     dump_file
        # ]

        restore_cmd = [
            "pg_restore",
            "-h", "dpg-d29sksndiees738d04qg-a.oregon-postgres.render.com",
            "-p", str(5432),
            "-U", "ctc_dev_4mjf_user",
            "-d", "ctc_dev_4mjf",
            dump_file
        ]
        subprocess.run(restore_cmd, check=True, env=env)

        # Clean up
        os.remove(dump_file)

        return {"status": "success", "message": f"Database cloned to {req.target_db}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/helperFunction/move_table_data")
async def data_transfere(table_name: str):   
    
        
    SOURCE_DB_URL = "postgresql://leticia:leeminho@localhost/churchMSDev"
    DESTINATION_DB_URL = "postgresql://ctc_dev_4mjf_user:TQarR3DpwZPAZieKlm2b9ccDDLfCDM6s@dpg-d29sksndiees738d04qg-a.oregon-postgres.render.com/ctc_dev_4mjf"

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


