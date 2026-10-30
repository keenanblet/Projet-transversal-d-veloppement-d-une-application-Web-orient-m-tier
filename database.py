from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL="mysql://api_user:1234@172.16.118.67:3306/MaPart"
# Initialize database engine by using MySQL
engine = create_engine(DB_URL,echo=True)

# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

# Create the base class for all ORM models
# The Base object serves as the parent for all database models you define in your application.
Base = declarative_base()