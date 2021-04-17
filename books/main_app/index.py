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
            f"select  * from books where {search_category} LIKE '%{payload}%' limit 200 ;" , {
                "payload" : payload,
                "search_category" : search_category
            }
            ).fetchall() 
    data = []
    for row in obj_books:
        r = [x for x in row]
        d = { "isbn": r[0].strip(), "title" : r[1].strip(), "author" : r[2].strip(), "year" : r[3] }
        data.append(d)
    return jsonify({"data" : data , "success" : True})

# @bp.route('/book/<isbn>')
# def book(isbn):
#     db = get_db()
#     book = db.execute("SELECT * FROM BOOKS WHERE isbn = :isbn;" , {"isbn" : isbn}).fetchone()
#     return render_template("book.html" , data=[x for x in book])


@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@bp.route('/book-review/<isbn>')
@login_required
def getbookpage(isbn):
    db = get_db()
    reviews = []
    reviews = db.execute("SELECT * FROM USERS INNER JOIN REVIEWS ON  REVIEWS.book_id = :book_id", {"book_id" : isbn}).fetchall()
    book_info = db.execute("SELECT * FROM BOOKS WHERE RTRIM(LTRIM(isbn)) = :isbn;", {"isbn" : isbn.strip()}).fetchone()
    reviews = [x for x in reviews]
    # books = [x for x in book_info]
    # data = []
    data = []
    # for book in book_info:
    data = dict(book_info)
    data["rating_star"] = 3
    data["rating"] = 3
    # return jsonify(data)
    # return jsonify(dict(book_info))
    return render_template("book.html", book_info=data, reviews=reviews)

@bp.route("/submit-review" , methods=["POST"])
@login_required
def submit_rate():
    rating_count = request.form.get("rating_count")
    rating_text = request.form.get("rating_text")
    book_id = request.form.get("review_isbn")
    usr_id = session.get("username")
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
        return redirect(url_for("main.getbookpage" , isbn=book_id))
    else:
        return jsonify([rating_count, rating_text, book_id, usr_id])

@bp.route("/a")
def a():
    return render_template("book.html")