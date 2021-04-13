from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for,json
)
from werkzeug.security import check_password_hash , generate_password_hash
from books.db.db import get_db
from books.utlis.utils import build_sql
from books.auth.auth import login_required
bp = Blueprint("main", __name__)

@bp.route("/home/")
@bp.route("/")
def index():
    return render_template("home.html")


@bp.route('/return_res' , methods=["GET"])
def return_res():
    db = get_db()
    isbn = request.args.get('isbn')
    title  = request.args.get('title')
    author = request.args.get('author')
    books = [title , isbn , author]
    commands = []
    for i in range(len(books)):
        if books[i] is not None and i == 0:
            commands.append(build_sql(books[i],'title'))
        if books[i] is not None and i == 1:
            commands.append(build_sql(books[i],'isbn'))
        if books[i] is not None and i == 2:
            commands.append(build_sql(books[i],'author'))
    sql_query = ""
    for i in  range(len(commands)):
        if i == 0:
             sql_query = commands[0]+ "  "
        else:
            sql_query += "and " +  commands[i] + "  " 
    obj_books = db.execute(
        "select * from books where " + sql_query  + "  order by year desc limit 10;"
        ).fetchall() 
    data = []
    for row in obj_books:
        r = [x for x in row]
        d = { "pub_date" : r[0], "title" : r[2], "isbn" : r[1].strip(), "author" :r[3] }
        data.append(d)
    return json.dumps(data)



@bp.route('/book/<isbn>')
def book(isbn):
    db = get_db()
    book = db.execute("SELECT * FROM BOOKS WHERE isbn = :isbn;" , {"isbn" : isbn}).fetchone()
    return render_template("book.html" , data=[x for x in book])


@bp.route("/profile")
@login_required
def reviews():
    return "there was an error"