import click
from ..database import db_connection

@click.command()
def clear():
    """Clear table 'polls'"""
    with db_connection() as conn:
        with conn.cursor() as cur:
            
            cur.execute("""DELETE FROM polls""")
            click.echo("Table 'polls' cleared")

if __name__ == "__main__":
    clear()