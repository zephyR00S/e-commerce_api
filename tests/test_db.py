from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables for test DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
