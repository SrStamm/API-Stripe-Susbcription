import os
import errno
import pytest
from main import app
from db.session import get_session
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from models import user, auth, plan, subscription
from models.user import Users

engine = create_engine("sqlite:///./test/test.db")


@pytest.fixture(scope="module")
def test_db():
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()

    try:
        os.remove("./test/test.db")
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


@pytest.fixture()
def test_session(test_db):
    session = Session(test_db)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(test_session):
    app.dependency_overrides[get_session] = lambda: test_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_session):
    new_user = Users(email="test@gmail.com", stripe_customer_id=None)
    test_session.add(new_user)
    test_session.commit()


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/login", json={"email": "test@gmail.com"})
    assert response.status_code == 200, f"Error en login: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
