#Handles the database connection and configuration, creating the SQLAlchemy engine and metadata instance.from sqlalchemy import create_engine, MetaData
from sqlalchemy import create_engine, MetaData

DATABASE_URL = "postgresql://postgres:Haya@localhost:5432/skills_platform_db"

engine = create_engine(DATABASE_URL)
metadata = MetaData()