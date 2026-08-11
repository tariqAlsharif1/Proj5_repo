# Import database engine and metadata instance
from database import engine
from models import metadata

if __name__ == "__main__":
    # Create all tables defined in models.py inside the PostgreSQL database
    metadata.create_all(engine)
    print("Database tables created successfully!")