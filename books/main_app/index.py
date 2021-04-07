from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for,json
)
from werkzeug.security import check_password_hash , generate_password_hash

bp = Blueprint("", __name__)


@bp.route("/home")
def home_page():
    return render_template("home.html")