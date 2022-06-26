import hashlib
import logging
import secrets

from decouple import config
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from mysql.connector import Error, MySQLConnection, connect, errorcode
from pydantic import BaseModel, Field, validator

logging.basicConfig(format="[%(asctime)s][%(levelname)s]:: %(message)s")
log = logging.getLogger(__name__)
log.setLevel("INFO")

app = FastAPI()

security = HTTPBasic()


def db_connection() -> MySQLConnection | None:
    try:
        return connect(
            host=config("MYSQL_HOST"),
            user=config("MYSQL_USER"),
            password=config("MYSQL_PASSWORD"),
            database=config("MYSQL_DATABASE"),
            autocommit=True,
        )
    except Error as err:
        match err.errno:
            case errorcode.ER_ACCESS_DENIED_ERROR:
                log.error("Wrong username or password")
            case errorcode.ER_BAD_DB_ERROR:
                log.error("Database does not exist")
            case _:
                log.error(f"Failed to connect to db: {err}")
        return None


def init_db():
    log.info("Initialize database...")
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS polls (
                id int NOT NULL AUTO_INCREMENT,
                fname varchar(100) NOT NULL,
                lname varchar(100) NOT NULL,
                age int NOT NULL,
                city varchar(100) NOT NULL,
                interests varchar(256) DEFAULT NULL,
                login varchar(20) NOT NULL,
                password binary(32) NOT NULL,
                CONSTRAINT pk_polls PRIMARY KEY (id),
                CONSTRAINT unique_login UNIQUE (login) 
                )"""
            )
    log.info("Database initialized!")


def get_pwd_hash(pwd: str) -> bytes:
    return hashlib.sha256(pwd.encode()).digest()


class PollBase(BaseModel):
    first_name: str = Field(title="Person's first name", max_length=100)
    last_name: str = Field(title="Person's last name", max_length=100)
    age: int = Field(gt=0, title="Person's age")
    city: str = Field(title="Person's city", max_length=100)
    interests: str | None = Field(
        default=None, title="Person's interests", max_length=256
    )


class PollRegister(PollBase):
    login: str = Field(title="Person's login", max_length=20)
    password: str = Field(title="Person's password", max_length=48)

    @validator("login")
    def alnum_ascii(cls, v: str):
        assert (
            v.isalnum() and v.isascii()
        ), "Must be a string of ASCII characters and numbers"
        return v

    @validator("password")
    def ascii(cls, v: str):
        assert v.isascii(), "Must be a string of ASCII"
        return v

    class Config:
        validate_assignment = True


class PollRead(PollBase):
    id: int


def check_credentials(c: HTTPBasicCredentials):
    with db_connection() as conn:
        with conn.cursor(buffered=True) as cur:
            try:
                cur.execute(
                    "SELECT login, password FROM polls WHERE login=%s", (c.username,)
                )
                if cur.rowcount < 1:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password",
                        headers={"WWW-Authenticate": "Basic"},
                    )
                username, pwd_hash = cur.fetchone()
            except Error as err:
                log.error(err)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err.msg
                )
            correct_username = secrets.compare_digest(c.username, username)
            correct_password = secrets.compare_digest(
                get_pwd_hash(c.password), pwd_hash
            )
            if not (correct_username and correct_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Basic"},
                )


@app.get("/polls/", response_model=list[PollRead], status_code=200)
async def get_polls(
    offset: int = 0, limit: int = 10, c: HTTPBasicCredentials = Depends(security)
):
    check_credentials(c)
    with db_connection() as conn:
        with conn.cursor(buffered=True) as cur:
            try:
                results = []
                cur.execute(
                    "SELECT id, fname, lname, age, interests, city FROM polls LIMIT %s OFFSET %s;",
                    (limit, offset),
                )
                for id, first_name, last_name, age, interests, city in cur:
                    results.append(
                        PollRead(
                            id=id,
                            first_name=first_name,
                            last_name=last_name,
                            age=age,
                            interests=interests,
                            city=city,
                        )
                    )
            except Error as err:
                log.error(err)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err.msg
                )

            return results


@app.get("/polls/{poll_id}", response_model=PollRead, status_code=200)
async def get_one_poll(poll_id: int, c: HTTPBasicCredentials = Depends(security)):
    check_credentials(c)
    with db_connection() as conn:
        with conn.cursor(buffered=True) as cur:
            try:
                cur.execute(
                    "SELECT id, fname, lname, age, interests, city FROM polls WHERE id=%s;",
                    (poll_id,),
                )
                if cur.rowcount < 1:
                    return HTTPException(
                        status_code=status.HTTP_204_NO_CONTENT,
                        detail=f"Poll with id {poll_id} doesn't exist",
                    )
                id, first_name, last_name, age, interests, city = cur.fetchone()
            except Error as err:
                log.error(err)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err.msg
                )
            return PollRead(
                id=id,
                first_name=first_name,
                last_name=last_name,
                age=age,
                interests=interests,
                city=city,
            )


@app.post("/register", response_model=PollRead, status_code=201)
async def register_poll(poll: PollRegister):
    pwd_hash = get_pwd_hash(poll.password)
    with db_connection() as conn:
        with conn.cursor(buffered=True) as cur:
            try:
                cur.execute(
                    """
                INSERT INTO polls (fname, lname, age, interests, city, login, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)    
                """,
                    (
                        poll.first_name,
                        poll.last_name,
                        poll.age,
                        poll.interests,
                        poll.city,
                        poll.login,
                        pwd_hash,
                    ),
                )
            except Error as err:
                match err.errno:
                    case errorcode.ER_DUP_ENTRY:
                        msg = f"Poll for {poll.login!r} already exist"
                        log.warn(msg)
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Poll for {poll.login!r} already exist",
                        )
                    case _:
                        log.error(err)
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
            poll_read = PollRead(**poll.dict(), id=cur.lastrowid)
            return poll_read
