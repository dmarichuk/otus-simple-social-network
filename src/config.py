import logging

from decouple import config

logging.basicConfig(format="[%(asctime)s][%(levelname)s]:: %(message)s")

if config("TEST", cast=bool):
    db_host = config("TEST_MYSQL_HOST")
    db_user = config("TEST_MYSQL_USER")
    db_password = config("TEST_MYSQL_PASSWORD")
    db_database = config("TEST_MYSQL_DATABASE")
    db_port = config("TEST_MYSQL_PORT")
else:
    db_host = config("MYSQL_HOST")
    db_user = config("MYSQL_USER")
    db_password = config("MYSQL_PASSWORD")
    db_database = config("MYSQL_DATABASE")
    db_port = config("MYSQL_PORT")
