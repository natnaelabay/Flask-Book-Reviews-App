from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for,json,jsonify
)
from werkzeug.security import check_password_hash , generate_password_hash
from books.db.db import get_db
from books.utlis.utils import build_sql
from books.auth.auth import login_required, redirect_if_logged_in
from sqlalchemy import text
bp = Blueprint("main", __name__)
 
@bp.route("/home/")
@bp.route("/")
@redirect_if_logged_in
def index():
    return render_template("home.html")


@bp.route('/search' , methods=["GET"])
def search_book():
    db = get_db()
    payload = request.args.get("payload")
    search_category = request.args.get("search_category")
    if payload is None or search_category is None:
        error = {"success" : False, "message" : "Some of the inputs are empty! "}
        return jsonify(error)
    obj_books = []
    if search_category == "year":
        obj_books = db.execute(
            f"select * from books where {search_category} = '%{int(payload)}%' limit 200 ;" , {
                "payload" : payload,
                "search_category" : search_category
            }
            ).fetchall()
    else:
        obj_books = db.execute(
            f"select * from books where {search_category} LIKE '%{payload}%' limit 200 ;" , {
                "payload" : payload,
                "search_category" : search_category
            }
            ).fetchall() 
    data = []
    for row in obj_books:
        r = [x for x in row]
        d = { "pub_date" : r[0], "title" : r[2], "isbn" : r[1].strip(), "author" :r[3] }
        data.append(d)
    return jsonify({"data" : data , "success" : True})



@bp.route('/book/<isbn>')
def book(isbn):
    db = get_db()
    book = db.execute("SELECT * FROM BOOKS WHERE isbn = :isbn;" , {"isbn" : isbn}).fetchone()
    return render_template("book.html" , data=[x for x in book])


@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@bp.route('/book-review/<book_id>')
def getbookpage(book_id):
    db = get_db()
    reviews = db.execute("SELECT * FROM USERS INNER JOIN REVIEWS ON  REVIEWS.book_id = :book_id", {"book_id" : book_id}).fetchall()
    return jsonify([x for x in reviews] )

@bp.route("/rate" , methods=["POST"])
@login_required
def submit_rate():
    rating_count = request.form.get("rating_count")
    rating_text = request.form.get("rating_text")
    book_id = 1
    usr_id = 1
    if (rating_count and rating_text and book_id and usr_id):
        db = get_db()
        db.execute(
            "INSERT INTO REVIEWS( book_id, usr_id, rate_count, rate_desc) VALUES(:book_id, :usr_id, :rate_count, :rate_desc);"
            ,{
                "book_id" : book_id,
                "usr_id" : usr_id,
                "rate_count" : rating_count,
                "rate_desc" : rating_text
            })
        db.commit()
        return jsonify("success")
    else:
        return "something happened"

@bp.route("/a")
def a():
    return render_template("book.html")