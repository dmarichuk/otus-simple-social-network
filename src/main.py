import logging
import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .database import Error, db_connection, errorcode
from .models import PollRead, PollRegister
from .utils import get_pwd_hash


log = logging.getLogger(__name__)
log.setLevel("INFO")

app = FastAPI()

security = HTTPBasic()


def check_credentials(c: HTTPBasicCredentials, conn=None):
    if not conn:
        conn = db_connection()
    with conn.cursor(buffered=True) as cur:
        try:
            cur.execute(
                "SELECT login, password FROM polls WHERE login=%s", (c.username,)
            )
            if cur.rowcount < 1:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect login or password",
                    headers={"WWW-Authenticate": "Basic"},
                )
            username, pwd_hash = cur.fetchone()
        except Error as err:
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err.msg
            )
        correct_username = secrets.compare_digest(c.username, username)
        correct_password = secrets.compare_digest(get_pwd_hash(c.password), pwd_hash)
        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
                headers={"WWW-Authenticate": "Basic"},
            )


@app.get("/polls/", response_model=list[PollRead], status_code=200)
async def get_polls(
    offset: int = 0, limit: int = 10, c: HTTPBasicCredentials = Depends(security)
):
    with db_connection() as conn:
        check_credentials(c, conn)
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
    with db_connection() as conn:
        check_credentials(c, conn)
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
                        get_pwd_hash(poll.password),
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
