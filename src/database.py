import logging

from mysql.connector import Error, MySQLConnection, connect, errorcode

import src.config as config

log = logging.getLogger(__name__)
log.setLevel("INFO")


def db_connection() -> MySQLConnection | None:
    try:
        return connect(
            host=config.db_host,
            user=config.db_user,
            password=config.db_password,
            database=config.db_database,
            port=config.db_port,
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
