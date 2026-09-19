import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.watch import WatchDB
from app.main import app
from app.database.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import UserDB

# In-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Configured StaticPool to keep the in-memory database persistent across connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh database for each test and drops it after."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Test client overriding the real database with the test session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture(scope="function")
def test_user(db_session):
    """Provides a verified user without the email field."""
    hashed_password = get_password_hash("testpassword123")
    user = UserDB(username="testuser", hashed_password=hashed_password)

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def authorized_client(client, test_user):
    """Returns an authenticated TestClient with a valid Bearer token."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture(scope="function")
def test_watch(db_session, test_user):
    """Injects a mock watch directly into the test database to avoid AI API calls."""
    watch = WatchDB(
        brand="Seiko",
        model_name="5 Sports",
        is_automatic=True,
        movement_type="Automatic",
        case_size_mm=40.0,
        crystal_type="Hardlex",
        water_resistance_m=100.0,
        strap_type="Steel",
        price=250.0,
        ai_confidence=0.99,
        needs_verification=False,
        user_id=test_user.id
    )
    db_session.add(watch)
    db_session.commit()
    db_session.refresh(watch)
    return watch