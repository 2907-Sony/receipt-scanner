from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os



load_dotenv()  # reads .env file and loads its values into the environment

DATABASE_URL = os.getenv("DATABASE_URL") # link that connecets the database



engine = create_engine(DATABASE_URL) # prepares the connection 

SessionLocal = sessionmaker(bind=engine) # telling the session to use respective engine to talk to database i.e using bind 


class Base(DeclarativeBase):   # inherited class model(Base), from the inbuilt base class (DeclarativeBase)
    pass



if __name__ == "__main__":
    connection = engine.connect() # Actual momant of connection
    print("Successfully connected to the database!")
    connection.close()
