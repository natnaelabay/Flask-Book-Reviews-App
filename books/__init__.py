import os
from dotenv import load_dotenv
from flask import Flask,session,render_template,send_from_directory
from flask_session import Session


load_dotenv()
def create_app():
    app = Flask(__name__,static_folder='static', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
    )
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
    app.config["UPLOAD_FOLDER "] = os.path.join(os.getcwd() ,os.path.join('books' , os.path.join('static' , 'images')))

    Session(app)
    print(app.url_map)

    @app.route("/check")
    def index():    
        # goal_dir = os.path.join(os.getcwd(), "../../my_dir")
        # print()
        return '<a class="button" href="/login">Google Login</a>'
    
    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return render_template("404.html")
    


    # this is for serving files
    @app.route("/static/<path:path>")
    def static_dir(path):
        return send_from_directory("static", path)

    from books.db import db
    from books.main_app import index
    from books.auth import auth
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(index.bp)
    
    return app