import functools
import os
from flask import (
   current_app, Blueprint,flash,g,redirect,render_template,request,session,url_for,flash,json,send_file
)
from werkzeug.security import check_password_hash,generate_password_hash

from books.db.db import get_db
from books.utlis import utils

bp = Blueprint('auth' , __name__, url_prefix="/auth")


@bp.route('/login', methods=["GET" , "POST"])
def login():
    if request.method == "POST":
        username=request.form.get('u_name')
        password=request.form.get("password")
        db = get_db()
        error = []
        if username is None:
            error.append("username is required")
        elif password is None:
            error.append("password is required")
        
        if len(error) == 0:
            user = db.execute("SELECT * FROM users where u_name = :uname;" , {"uname" : username}).fetchone()
            if not user:
                return "empty"
            if check_password_hash(user["password"],password):
                session.clear()
                session["username"] = user["u_name"]
            return redirect(url_for('main.index'))
        flash(error)
        # return render_template("login.html")

        

    return redirect(url_for("main.index"))
    # return render_template("login.html")

@bp.route('/register',methods=["POST" , "GET"])
def register():
    if request.method == "GET":
        return redirect(url_for("main.index"))
    f_name = request.form.get('f_name')
    l_name = request.form.get('l_name')
    username = request.form.get('u_name')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirm')
    img = request.files.get("img")
    # print(img)
    error = []

    if utils.num_there(f_name):
        error.append('Invalid character in name')
        if len(f_name) == 0:
            error.append("name can not be empty")
    if utils.num_there(l_name):
        error.append('Invalid character in name')
        if len(l_name) == 0:
            error.append("name can not be empty")
    if len(username) == 0:
        error.append("username can not be empty")

    if len(password) < 6:
        error.append('Password is too short')
    # return { "pass" : password , "p" : password_confirmation}
    if password != password_confirmation:
        error.append('password mismatch')

    if len(error) == 0:
        db = get_db()
        db.execute(
            "INSERT INTO USERS(f_name,l_name,u_name,password) VALUES( :f_name,:l_name,:u_name,:password )" , {
                "f_name" :f_name,
                "l_name": l_name,
                "u_name" : username,
                "password": generate_password_hash(password)
            }
        )
        db.commit()

        # img = request.files["img"]
        if  img:
            img.save(os.path.join(current_app.config["UPLOAD_FOLDER "], username + "." + img.filename.rsplit(".", 1)[1]))

        # return redirect(url_for('auth.login'))
        return "redirect(url_for('auth.login'))"


    flash(error)
    return render_template("register.html")
    
@bp.route('/logout')
def logout():
    session.clear()
    return render_template("login.html")
    # return redirect(url_for('index'))


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for("auth.login"))
		return view(**kwargs)
	return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    username = session.get('username')

    if username is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users where u_name = :uname;', {"uname" : username}
        ).fetchone()
        print("-----------g.user---------------")
        print(g.user)
        print("---------------g.user---------------")

@bp.route('/')
@login_required
def check():
    return "just checking"

#  file upload
@bp.route('/up', methods=["POST","GET"])
def upload():
    if request.method == "POST":
        img = request.files["img"]
        print(img)
        img.save(os.path.join(current_app.config["UPLOAD_FOLDER "],  img.filename))
        return "yehe"
    return render_template("upload.html")

@bp.route('/send')
def send():
    return send_file(os.path.join(os.getenv("IMAGE_UPLOADS"), "a.PNG"))