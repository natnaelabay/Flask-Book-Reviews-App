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

    @app.route("/")
    def index():            
        return '<a class="button" href="/login">Google Login</a>'

    return app