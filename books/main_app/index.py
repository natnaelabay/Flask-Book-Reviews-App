from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for,json,jsonify
)
import math
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

@bp.route("/profile")
@bp.route("/home")
@login_required
def profile():
    return render_template("profile.html")

@bp.route('/book-review/<isbn>')
@login_required
def getbookpage(isbn):
    db = get_db()
    reviews = []
    book = db.execute("SELECT * FROM Books where  isbn  = :book_id", {"book_id" : isbn.strip()}).fetchone()
    if not book:
        return render_template("book.html")
    reviews = db.execute(
        "SELECT USERS.f_name,USERS.l_name,USERS.u_name , USERS.profile_url, REVIEWS.book_id, REVIEWS.rate_count,REVIEWS.rate_desc  FROM USERS INNER JOIN REVIEWS ON USERS.u_name = REVIEWS.usr_id where  REVIEWS.book_id =  :isbn ;", {"isbn" : isbn.strip()}).fetchall()
    '''
        find the amount of total reviews 
        find the mount of 1 - 5 reviews
        calculate average for each of them

    '''
    rows = reviews
    data = []
    user_name = session['username']
    total_rating = 0
    ratings_count = {"one":0 , "two": 0 , "three" :0  , "four" : 0  , "five" :0 , "total_count" :0 , "avg_rating" : 0}
    total_rows = 0
    counter = 0
    has_not_submitted = True
    if reviews:
        for row in rows:
            r = [x for x in row]
            if r[2].strip() == user_name:
                    has_not_submitted = False
            img_url = r[3].split('\\')[3]
            img_ext =img_url[img_url.index(".")+ 1 :]
            img_ext = url_for("static" , filename = f"images/{r[2].strip() + '.' + img_ext}")
            d = { 
                "f_name": r[0].strip(), 
                "l_name" : r[1].strip(), 
                "u_name" : r[2].strip(), 
                "usr_profile" : img_ext, 
                "isbn" : r[4] , 
                "rate_count" : r[5], 
                "rate_desc" : r[6]
            }
            # total_rating += r[5]
            total_rows += 1
            rate_value = r[5]
            if rate_value == 1:
                ratings_count["one"] += 1
                counter +=  1
            elif rate_value == 2:
                counter +=  2
                ratings_count["tow"] += 1
            elif rate_value == 3:
                counter +=  3
                ratings_count["three"] += 1
            elif rate_value == 4:
                counter +=  4
                ratings_count["four"] += 1
            elif rate_value == 5:
                counter +=  5
                ratings_count["five"] += 1
            data.append(d)
        ratings_count["one_avg"] = (ratings_count["one"] / total_rows) * 100
        ratings_count["two_avg"] = ((ratings_count["two"] )/ total_rows) * 100
        ratings_count["three_avg"] = ((ratings_count["three"] )/ total_rows) * 100
        ratings_count["four_avg"] = ((ratings_count["four"] )/ total_rows) * 100
        ratings_count["five_avg"] = ((ratings_count["five"]  )/ total_rows) * 100
        ratings_count["total_count"] = total_rows 
        avg_rating =  (counter/(total_rows ))
        ratings_count["star_rating"] =round(avg_rating)
        ratings_count["avg_rating"] =(avg_rating)
        ratings_count["api_avg"] = 0
        return render_template("book.html" , book_info = book, rating=ratings_count, reviews = data, has_not_submitted = has_not_submitted)
    else:
        return render_template("book.html" , book_info = book, has_not_submitted = True )
    return jsonify(data)


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
