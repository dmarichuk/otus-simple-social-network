import click
from faker import Faker
from ..database import db_connection
from ..main import get_pwd_hash

@click.command()
@click.option('--count', default=1, help="Number of rows to poulate 'polls'")
@click.option('--locale', default="en_US", help="Locale for fake data")
def populate(count, locale):
    """Populate table 'polls' with random data witn --count-- rows"""
    fake = Faker(locale=locale)
    if count > 1000000:
        click.echo("Can't generate more then 1000000")
        return
    with db_connection() as conn:
        with conn.cursor() as cur:
            for n in range(count):
                Faker.seed(n)
                data = {
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "age": fake.random_int(min=12, max=100),
                    "city": fake.city(),
                    "interests": fake.sentence(nb_words=10),
                    "login": f"user_{str(n).zfill(7)}",
                    "password": get_pwd_hash("password")
                }
                cur.execute("""
                    INSERT INTO polls (fname, lname, age, interests, city, login, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)    
                """, data.values())
                click.echo(f"User ID#{cur.lastrowid} {data['first_name']} {data['last_name']} added!")

if __name__ == "__main__":
    populate()