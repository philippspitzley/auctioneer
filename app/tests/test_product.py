import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from .. import db, utils
from ..config import DB_USER
from ..main import app
from ..models.user_model import User

TEST_DATABASE_URL = f"postgresql://{DB_USER}@localhost:5432/auctioneer_test_db"
REGISTERED_USER = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password123",
}


def create_registered_user(engine: Engine):
    with Session(engine) as session:
        hashed_password = utils.get_password_hash(REGISTERED_USER["password"])
        user = User(
            username=REGISTERED_USER["username"],
            email=REGISTERED_USER["email"],
            password_hash=hashed_password,
        )
        session.add(user)
        session.commit()


@pytest.fixture(scope="function", name="session")
def session():
    # Setup the engine and create tables for the test
    engine = create_engine(TEST_DATABASE_URL)
    SQLModel.metadata.create_all(engine)

    # Create a new session for each test
    with Session(engine) as session:
        # Start a transaction before the test
        session.begin()
        create_registered_user(engine)
        yield session

        # Rollback any changes made during the test to keep database state clean
        session.rollback()

    # Drop tables after all tests are finished
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client(session: Session):
    # Override session dependency in FastAPI app
    def get_session_override():
        return session

    app.dependency_overrides[db.get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="authenticated_client")
def authenticated_client(client: TestClient):
    login_data = {
        "username": REGISTERED_USER["email"],
        "password": REGISTERED_USER["password"],
    }
    response = client.post("auth/login", data=login_data)
    token = response.json()["access_token"]
    token_type = response.json()["token_type"]

    # Attach token to client headers for future requests
    client.headers.update({"Authorization": f"{token_type} {token}"})

    return client


class TestProductCRUD:
    @pytest.fixture(autouse=True)
    def setup(self, session, authenticated_client):
        self.session = session
        self.client = authenticated_client

    def test_create_product(self):
        response = self.create_product_in_db()
        data = response.json()

        assert response.status_code == 200
        assert "id" in data
        assert data["name"] == "Laptop"
        assert data["description"] == "A laptop"

    def create_product_in_db(self):
        product_data = {
            "owner_id": 1,
            "name": "Laptop",
            "description": "A laptop",
        }
        response = self.client.post("/products", json=product_data)
        return response

    def test_read_product(self):
        product_id = self.create_product_in_db().json()["id"]
        response = self.client.get(f"/products/{product_id}")
        data = response.json()
        print(data)

        assert response.status_code == 200
        assert data["id"] == product_id
        assert data["name"] == "Laptop"
        assert data["description"] == "A laptop"

    def test_update_product(self):
        product_id = self.create_product_in_db().json()["id"]
        updated_data = {
            "name": "Updated Laptop",
            "description": "Updated description",
        }
        response = self.client.patch(
            f"/products/{product_id}", json=updated_data
        )
        data = response.json()

        assert response.status_code == 200
        assert data["name"] == "Updated Laptop"
        assert data["description"] == "Updated description"

    def test_delete_product(self):
        product_id = self.create_product_in_db().json()["id"]
        response = self.client.delete(f"/products/{product_id}")
        assert response.status_code == 200

        response = self.client.get(f"/products/{product_id}")
        assert response.status_code == 404  # Product should no longer exist
