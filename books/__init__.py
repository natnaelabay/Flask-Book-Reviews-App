import os
from dotenv import load_dotenv
from flask import Flask,session
from flask_session import Session


load_dotenv()
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
    )
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    print(app.url_map)

    # @app.route("/")
    # def index():            
    #     return '<a class="button" href="/login">Google Login</a>'

    from books.db import db
    from books.main_app import index
    db.init_app(app)
    app.register_blueprint(index.bp)
    
    return app