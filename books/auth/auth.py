from flask import (
    Blueprint,flash,g,redirect,render_template,request,session,url_for
)
from werkzeug.security import check_password_hash,generate_password_hash

from books.db.db import get_db



bp = Blueprint('auth' , __name__, url_prefix="/auth")
@bp.route('/login', methods=["GET" , "POST"])
def login():
    if request.method == "POST":
        username=request.form.get('username')
        password=request.form.get("password")
        db = get_db()
        error = []
        if username is None:
            error.append("username is required")
        elif password is None:
            error.append("password is required")
        
        if len(error) == 0:
            user = db.execute("SELECT * USER WHERE username= :uname" , {"uname" : username}).fetchone()
            if check_password_hash(user["password"],password):
                pass
    return { "page" : "login-page" }



