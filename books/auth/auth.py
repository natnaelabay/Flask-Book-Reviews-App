import functools
import os
from flask import (
   current_app, Blueprint,flash,g,redirect,render_template,request,session,url_for,flash,json,send_file, jsonify
)
from werkzeug.security import check_password_hash,generate_password_hash

from books.db.db import get_db
from books.utlis import utils

bp = Blueprint('auth' , __name__, url_prefix="/auth")


@bp.route('/login', methods=[ "POST" , "GET"])
def login():
    if request.method == "POST":
        username=request.form.get('u_name')
        password=request.form.get("password")
        error = {"errors" : []} 
        if username is None or len(username) == 0:
            error["errors"].append("username is required")
        elif password is None:
            error["errors"].append("password is required")
        elif len(password) < 6:
            error["errors"].append("password is to short")
        try:
            db = get_db()
            if len(error["errors"]) == 0:
                user = db.execute("SELECT * FROM users where u_name = :uname;" , {"uname" : username}).fetchone()
                if not user:
                    error["errors"].append("username or password not correct!")
                    error["success"] = False
                    return jsonify(error)
                if check_password_hash(user["password"],password):
                    session.clear()
                    if user["profile_url"] is not None:
                        img_url = user['profile_url'].split('\\')[3]
                        img_ext =img_url[img_url.index(".")+ 1 :]
                        session["profile_url"] = url_for("static" , filename = f"images/{user['u_name'] + '.' + img_ext}")
                    else:
                        session["profile_url"] = url_for('static' ,filename = "images/default.png")
                    session["username"] = user["u_name"]
                    session["name"] = user["f_name"] + " " + user["l_name"]
                    message = {}
                    message["success"] = True
                    message["message"] = "Successfully Logedin"
                    # return session["profile_url"]
                    # return redirect((url_for("profile")))
                    #  redirect to the profile page
                    return jsonify(message)
                error["success"] = False
                error["errors"].append("username or password incorrect!")
                return jsonify(error)
            else:
                error["success"] = False
                error["errors"].append("username or password incorrect!")
                return jsonify(error)
        except :
            error["errors"].append("internal Error")
            error["success"] = False
            return jsonify(error)
    return redirect(url_for("main.index"))

@bp.route('/register',methods=["POST" , "GET"])
def register():
    if request.method == "GET":
        return redirect(url_for("main.index"))
    f_name = request.form.get('f_name')
    l_name = request.form.get('l_name')
    username = request.form.get('u_name')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirm')
    # img = request.files.get("img")
    error = {"errors":[]}
    inputs = [f_name , l_name, username, password, password_confirmation]
    values = ["first name" , "last name", "username","password", "password_confirmation"]
    if None in inputs:
        for a in range(len(inputs)):
            if inputs[a] is None:
                error["errors"].append(f"{values[a]} can not be empty")
    else:
        if utils.num_there(f_name):
                error["errors"].append('Invalid character in first name')
        if len(f_name) == 0:
            error["errors"].append("name can not be empty")
        if len(l_name) == 0:
            error["errors"].append("name can not be empty")
        if utils.num_there(l_name):
            error["errors"].append('Invalid character in last name')
        if len(username) == 0:
            error["errors"].append("username can not be empty")
        if len(password) < 6:
            error["errors"].append("password length too short")
        if  len(password_confirmation) < 6:
            error["errors"].append("password confirmation too short and mismatch")
        if password != password_confirmation:
            error["errors"].append('password mismatch')
        if len(error["errors"]) == 0:
            try:
                db = get_db()
                res = db.execute("SELECT COUNT(*) FROM USERS WHERE u_name = :u_name" , {"u_name" : username}).fetchone()
                count =[x for x in res]
                if count[0] == 0:
                    img = request.files.get("img")
                    if  img:
                        file_path_name = os.path.join(current_app.config["UPLOAD_FOLDER "], username + "." + img.filename.rsplit(".", 1)[1])
                        img.save(file_path_name)
                        db.execute(
                            "INSERT INTO USERS(f_name,l_name,u_name,password, profile_url) VALUES( :f_name,:l_name,:u_name,:password, :profile_url )" , {
                                "f_name" :f_name,
                                "l_name": l_name,
                                "u_name" : username,
                                "password": generate_password_hash(password),
                                "profile_url" : file_path_name
                            }
                        )
                        db.commit()
                    else:
                        db.execute(
                            "INSERT INTO USERS(f_name,l_name,u_name,password) VALUES( :f_name,:l_name,:u_name,:password )" , {
                                "f_name" :f_name,
                                "l_name": l_name,
                                "u_name" : username,
                                "password": generate_password_hash(password),

                            }
                        )
                        db.commit()
                    message = {}
                    message["success"] = True
                    message["message"] =   "user created successfully!"
                    return jsonify( message)
                else:
                    error["errors"].append("The username is already taken")
                    error["success"] = False
                    return jsonify(error)
            except :
                error["errors"].append("Something went wrong in the server! ")
                error["success"] = False
                return jsonify(error)
        else:
            error["success"] = False
            return jsonify(error)

    return jsonify(error)
    
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("main.index"))
    # return redirect(url_for('index'))


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for("auth.login"))
		return view(**kwargs)
	return wrapped_view

def redirect_if_logged_in(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is not  None:
			return redirect(url_for("main.profile"))
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