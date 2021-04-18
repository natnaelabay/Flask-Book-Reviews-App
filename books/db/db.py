import os
import click
from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import current_app,g
from flask.cli import with_appcontext
from dotenv import load_dotenv
load_dotenv()

def get_db():
    if 'db' not in g:
        engine = create_engine(os.getenv("DATABASE_URL"))
        db = scoped_session(sessionmaker(bind=engine))
        g.db = db
    return g.db

def close_db(e=None):
    db = g.pop('db',None)
    if db is not None:
        db.close()



def init_db():
    db = get_db()
    with current_app.open_resource(os.path.join("db", "schema.sql")) as f:
        query = text(f.read().decode('utf8'))
        db.execute(query)
        db.commit()

@click.command("build-db")
@with_appcontext
def execute_command():
    init_db()
    click.echo("database schema built!")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(execute_command)
    