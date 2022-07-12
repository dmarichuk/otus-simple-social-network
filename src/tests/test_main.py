import pytest
import base64
import json

from ..cli.initdb import init_db
from ..database import db_connection
from ..main import app, get_pwd_hash
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture(autouse=True, scope="session")
def init_table():
    init_db()

@pytest.fixture()
def db_session():
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO polls (fname, lname, age, interests, city, login, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)    
                """,
                    (
                        "test",
                        "test",
                        99,
                        "test",
                        "test",
                        "test",
                        get_pwd_hash("test"),
                    ),
            )
            yield cur
            cur.execute(
                """
                DELETE FROM polls;
                """
            )

@pytest.fixture()
def credentials():
    return base64.b64encode("test:test".encode("ascii")).decode("ascii")


def test_polls(db_session, credentials):
    headers = {"Authorization": f"Basic {credentials}"}
    r = client.get("/polls", headers=headers)
    
    assert r.status_code == 200

def test_single_poll(db_session, credentials):
    db_session.execute("SELECT id FROM polls")
    [poll_id] = db_session.fetchone()
    
    headers = {"Authorization": f"Basic {credentials}"}
    r = client.get(f"/polls/{poll_id}", headers=headers)
    
    assert r.status_code == 200

def test_register_poll(db_session):
    data = json.dumps({
        "first_name": "name",
        "last_name": "surname",
        "age": 89,
        "city": "city",
        "interests": "testing",
        "login": "user",
        "password": "password" 
    })

    r = client.post(
        "/register",
        data=data,
        headers={"Content-Type": "application/json"}
    )

    assert r.status_code == 201

