import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create TEST DATABASE
TEST_DB_URL = "sqlite:///./test_db.sqlite"

engine = create_engine(
    TEST_DB_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override DB dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    # Reset database before ALL tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

# Helper: create user + return token
@pytest.fixture
def user_token(client):
    signup = client.post("/signup", json={
        "email": "user@example.com",
        "password": "password123"
    })

    login = client.post("/token",
        data={"username": "user@example.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    return login.json()["access_token"]
