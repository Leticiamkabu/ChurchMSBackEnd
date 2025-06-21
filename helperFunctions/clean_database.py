# generate an excel sheet from data
from fastapi import  Response
from io import BytesIO
import os
import re


    
from sqlalchemy import create_engine, MetaData, Table, update, null
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import VARCHAR, TEXT
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Fetch database credentials from environment variables
db_user = os.getenv('DB_USER') 
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')



def replace_nulls_with_empty_string():
    # Build the database URL
    database_url = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"

    # Connect and reflect database schema
    engine = create_engine(database_url)
    metadata = MetaData(bind=engine)
    metadata.reflect()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for table_name, table in metadata.tables.items():
            print(f"Scanning table: {table_name}")
            for column in table.columns:
                if isinstance(column.type, (VARCHAR, TEXT)):
                    stmt = (
                        update(table)
                        .where(column.is_(None))  # PostgreSQL NULL check
                        .values({column: ""})
                    )
                    result = session.execute(stmt)
                    if result.rowcount > 0:
                        print(f"Updated {result.rowcount} rows in '{table_name}' for column '{column.name}'")
        session.commit()
        print("All NULLs replaced with empty strings in string columns.")
    except Exception as e:
        session.rollback()
        print("Error:", e)
    finally:
        session.close()

   