import click
from ..database import db_connection


@click.command()
def init_db():
    click.echo("Initialize database...")
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8"""
            )
    click.echo("Database initialized!")


if __name__ == "__main__":
    init_db()