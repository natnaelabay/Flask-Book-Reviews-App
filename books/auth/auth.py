import functools
from flask import (
    Blueprint,flash,g,redirect,render_template,request,session,url_for,flash,json
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
                session["user_id"] = user["id"]
            return render_template("home.html")
        flash(error)
        return render_template("login.html")

        

    return render_template("login.html")

@bp.route('/register',methods=["POST" , "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    f_name = request.form.get('f_name')
    l_name = request.form.get('l_name')
    username = request.form.get('u_name')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirm')
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

        return redirect(url_for('auth.login'))


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
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/')
@login_required
def check():
    return "just checking"