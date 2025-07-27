from fastapi import APIRouter, Depends, HTTPException, FastAPI, HTTPException 
from typing import Annotated
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import select, or_, func, and_, create_engine, MetaData, Table, update, null
from sqlalchemy.sql import func , extract
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




@router.post("/helperFunction/clean_data_base")
async def replace_null_values_in_the_database(db_user: str, db_pass: str, db_host: str, db_name: str, table_name: str):

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



@router.post("/helperFunction/clone_db")
async def clone_db(server_user: str, server_pass: str, server_host: str, server_db: str,server__port: str,table_name: str):

    try:
        # Dump source DB to temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            dump_file = tmpfile.name

        # Set env for pg_dump
        env = os.environ.copy()
        env["PGPASSWORD"] = req.source_password

        dump_cmd = [
            "pg_dump",
            "-h", req.source_host,
            "-p", str(req.source_port),
            "-U", req.source_user,
            "-d", req.source_db,
            "-Fc",  # custom format for pg_restore
            "-f", dump_file
        ]

        subprocess.run(dump_cmd, check=True, env=env)

        # Create target database
        env["PGPASSWORD"] = req.target_password
        createdb_cmd = [
            "createdb",
            "-h", req.target_host,
            "-p", str(req.target_port),
            "-U", req.target_user,
            req.target_db
        ]
        subprocess.run(createdb_cmd, check=True, env=env)

        # Restore into target DB
        restore_cmd = [
            "pg_restore",
            "-h", req.target_host,
            "-p", str(req.target_port),
            "-U", req.target_user,
            "-d", req.target_db,
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

# class CloneDBRequest(BaseModel):
#     source_host: str
#     source_port: int
#     source_user: str
#     source_password: str
#     source_db: str

#     target_host: str
#     target_port: int
#     target_user: str
#     target_password: str
#     target_db: str


    