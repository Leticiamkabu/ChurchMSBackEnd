import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch database credentials from environment variables
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

# Ensure that all the necessary environment variables are loaded
if not all([db_user, db_pass, db_host, db_name]):
    raise EnvironmentError("Missing one or more required environment variables for database connection")

# Construct the async database URL
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}/{db_name}"

# Create async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Async sessionmaker
SessionLocal = sessionmaker(expire_on_commit=False, class_=AsyncSession, bind=engine)

# Declarative base for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Function to create database tables asynchronously
async def create_database_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Use asyncio to run the asynchronous setup code
async def setup():
    try:
        await create_database_tables()
        print("Database tables created successfully.")
    except Exception as e:
        print(f"An error occurred during database setup: {e}")
