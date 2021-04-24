import os
import re
import click
import random
import joblib
import functools
from utlis import utils
from flask_session import Session
from datetime import datetime, date
from flask.cli import with_appcontext
from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash,generate_password_hash
from flask import flash, Flask, session, current_app, Blueprint,flash,g,redirect,render_template,request,session,url_for,json,send_file, jsonify,abort


app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise    RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER "] = os.path.join('static' , 'images')


Session(app)

'''
    Database Related methods for creating te instance and tearing down the connection
'''
def get_db():
    if 'db' not in g:
        engine = create_engine(os.environ.get("DATABASE_URL"))
        db = scoped_session(sessionmaker(bind=engine))
        g.db = db
    return g.db

def close_db(e=None):
    db = g.pop('db',None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        query = text(f.read().decode('utf8'))
        db.execute(query)
        db.commit()

'''
    login and logout required directives
'''
def logout_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user:
			return redirect(url_for("profile"))
		return view(**kwargs)
	return wrapped_view

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for("login"))
		return view(**kwargs)
	return wrapped_view



'''
    A flask command for building the database 
'''

@click.command(name="build-db")
@with_appcontext
def execute_command():
    init_db()
    click.echo("database schema built!")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(execute_command)



'''
    Error handling area for overriding the 
'''
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.before_request
def load_logged_in_user():
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users where u_name = :uname;', {"uname" : username}
        ).fetchone()

@app.route('/auth/login', methods=[ "POST" , "GET"])
@logout_required
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
        # try:
        db = get_db()
        if len(error["errors"]) == 0:
            user = db.execute("SELECT * FROM users where u_name = :uname;" , {"uname" : username}).fetchone()
            if not user:
                error["errors"].append("username or password not correct!")
                error["success"] = False
                return render_template("home.html" , errors = ["username or password not correct"])
            if check_password_hash(user["password"],password):
                session.clear()
                if user["profile_url"] is not None:
                    img_url = user['profile_url'].split('\\')[2]
                    img_ext =img_url[img_url.index(".")+ 1 :]
                    session["profile_url"] = url_for("static" , filename = f"images/{user['u_name'] + '.' + img_ext}")
                else:
                    session["profile_url"] = url_for('static' ,filename = "images/default.png")
                session["username"] = user["u_name"]
                session["b_date"] = user["b_date"]
                session["name"] = user["f_name"] + " " + user["l_name"]
                message = {}
                message["success"] = True
                message["message"] = "Successfully Logedin"
                return redirect(url_for("profile"))
            error["success"] = False
            error["errors"].append("username or password incorrect!")
            return render_template("home.html" ,errors = error["errors"])
        else:
            error["success"] = False
            error["errors"].append("username or password incorrect!")
            return render_template("home.html" , errors=error["errors"])
    return redirect(url_for("index"))

@app.route('/auth/register',methods=["POST" , "GET"])
@logout_required
def register():
    if request.method == "GET":
        return redirect(url_for("index"))
    f_name = request.form.get('f_name')
    l_name = request.form.get('l_name')
    b_date = request.form.get('date')
    username = request.form.get('u_name')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirm')
    error = {"errors":[]}
    inputs = [f_name , l_name, username, password, password_confirmation]
    values = ["first name" , "last name", "username","password", "password_confirmation"]
    if None in inputs:
        for a in range(len(inputs)):
            if inputs[a] is None:
                error["errors"].append(f"{values[a]} can not be empty")
    else:
        if not (b_date):
            error["errors"].append("birth date is required for the recommendation ML engine!")
        if utils.num_there(f_name.strip()):
                error["errors"].append('Invalid character in first name')
        if len(f_name.strip()) == 0:
            error["errors"].append("name can not be empty")
        elif len(f_name.strip()) >20:
            error["errors"].append("first name can not this long!!")
        
        if len(l_name.strip()) == 0:
            error["errors"].append("name can not be empty")
        elif len(l_name.strip()) > 20:
            error["errors"].append("last name can not this long!!")

        if utils.num_there(l_name.strip()):
            error["errors"].append('Invalid character in last name')
        if len(username.strip()) == 0:
            error["errors"].append("username can not be empty")
        elif not username.strip().isalnum():
            error["errors"].append("username can only contain numbers 0-9, underscore and alphabets Aa-Zz")
        if len(username.strip()) > 15:
            error["errors"].append("username cannot be longer than 15 characters")
        
        if len(password) < 6:
            error["errors"].append("password length too short")
        if  len(password_confirmation.strip()) < 6:
            error["errors"].append("password mismatch and confirmation length too short!!")
        elif password.strip() != password_confirmation.strip():
            error["errors"].append('password mismatch')
        
        if not b_date:
            error["errors"].append('birth date required ')
        if len(error["errors"]) == 0:
            age = calc_age(b_date)
            db = get_db()
            res = db.execute("SELECT COUNT(*) FROM USERS WHERE u_name = :u_name" , {"u_name" : username}).fetchone()
            count =[x for x in res]
            if count[0] == 0:
                img = request.files.get("img")
                if  img:
                    file_path_name = os.path.join(current_app.config["UPLOAD_FOLDER "], username.strip() + "." + img.filename.rsplit(".", 1)[1])
                    img.save(file_path_name)
                    db.execute(
                        "INSERT INTO USERS(f_name,l_name,u_name,password,b_date, profile_url) VALUES( :f_name,:l_name,:u_name,:password,:b_date, :profile_url )" , {
                            "f_name" :f_name.strip(),
                            "l_name": l_name.strip(),
                            "u_name" : username.strip(),
                            "b_date" : b_date.strip(),
                            "password": generate_password_hash(password.strip()),
                            "profile_url" : file_path_name.strip()
                        }
                    )
                    db.commit()
                else:
                    db.execute(
                        "INSERT INTO USERS(f_name,l_name,u_name,password,b_date) VALUES( :f_name,:l_name,:u_name,:password, :b_date )" , {
                            "f_name" :f_name.strip(),
                            "l_name": l_name.strip(),
                            "u_name" : username.strip(),
                            "password": generate_password_hash(password),
                            "b_date" : b_date.strip(),
                        }
                    )
                    db.commit()
                return render_template("home.html" ,errors=["registered Successfully"])
            else:
                error["errors"].append("Username already in use!")
                return render_template("home.html" ,errors=error["errors"])
            # except :
            #     error["errors"].append("Something went wrong in the server! ")
            #     error["success"] = False
            #     return jsonify(error)
        else:
            return render_template("home.html" ,errors=error["errors"])
    
@app.route('/auth/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))



def redirect_if_logged_in(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is not  None:
			return redirect(url_for("profile"))
		return view(**kwargs)
	return wrapped_view


@app.route('/send')
def send():
    return send_file(os.path.join(os.getenv("IMAGE_UPLOADS"), "a.PNG"))

@app.route("/home/")
@app.route("/")
@redirect_if_logged_in
def index():
    return render_template("home.html")

@app.route('/search' , methods=["GET"])
@login_required
def search_book():
    payload = request.args.get("payload")
    if payload:
        return redirect(url_for('profile', search="true" , payload=payload))
    else:
        return redirect(url_for("profile"))

def get_search_words(payload):
    db = get_db()
    if payload is None:
        error = {"success" : False, "message" : "Some of the inputs are empty! "}
        return jsonify(error)
    obj_books = db.execute(
        "select * from books where isbn LIKE ('%"+payload+"%')  or lower(title) LIKE lower('%"+payload+"%') or  lower(author) LIKE lower('%"+payload+"%') order by year desc;"
        ).fetchall() 
    data = []
    for row in obj_books:
        r = [x for x in row]
        d = { "isbn": r[0].strip(), "title" : r[1].strip(), "author" : r[2].strip(), "year" : r[3] }
        data.append(d)
    return data

@app.route("/profile")
@app.route("/books")
@login_required
def profile():
    db = get_db()

    '''
        ML Recommender
    '''
    
    age = calc_age(session["b_date"])
    year = predict_year(age)
    books = db.execute("SELECT * FROM BOOKS WHERE books.year > :start_date and books.year < :end_date  limit 5; " , {"start_date" : year, "end_date": year + 4 }).fetchall()
    recommended = []
    for row in books:
        r = [x for x in row]
        d = { "isbn": r[0].strip(), "title" : r[1].strip(), "author" : r[2].strip(), "year" : r[3] }
        recommended.append(d)

    '''
        ML Recommender
    '''
    chosen = []
    for i in range(3):
        random_index = random.randrange(len(books))
        chosen.append(books[random_index])
    if request.args.get("search"):
        data = get_search_words(request.args.get("payload"))
        if len(data) == 0:
            return render_template("profile.html", searched=True, recommend = chosen)
        else:
            return render_template("profile.html" , search_result=data , recommend=chosen)
    return render_template("profile.html",recommend=chosen)

@app.route('/book-review/<isbn>')
@login_required
def getbookpage(isbn):
    db = get_db()
    reviews = []
    book = db.execute("SELECT * FROM Books where  isbn  = :book_id", {"book_id" : isbn.strip()}).fetchone()
    if not book:
        return render_template("book.html")
    reviews = db.execute(
        "SELECT USERS.f_name,USERS.l_name,USERS.u_name , USERS.profile_url, REVIEWS.book_id, REVIEWS.rate_count,REVIEWS.rate_desc  FROM USERS INNER JOIN REVIEWS ON USERS.u_name = REVIEWS.usr_id where  REVIEWS.book_id =  :isbn;", {"isbn" : isbn.strip()}).fetchall()
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
            img_ext=""
            if r[3]:
                img_url = r[3].split('\\')[2]
                img_ext =img_url[img_url.index(".")+ 1 :]
                img_ext = url_for("static" , filename = f"images/{r[2].strip() + '.' + img_ext}")
            else:
                img_ext = url_for("static" , filename = f"images/{'default' +  '.' + 'png'}")
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
                ratings_count["two"] += 1
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
        ratings_count["star_rating"] =round(avg_rating,2)
        ratings_count["avg_rating"] =round(avg_rating,2)
        rating_api = None
        good_reads_rate_count = None

        try:
            import requests
            res = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key=AIzaSyCq4YjdyQSiKxGoovJVNnwWdCfaXYNJQpo")
            res = res.json()
            if res["totalItems"] != 0:
                        rating_api = res["items"][0]["volumeInfo"]["averageRating"]
                        good_reads_rate_count = res["items"][0]["volumeInfo"]["ratingsCount"]
        except:
            pass
        
        good_reads = {}
        good_reads["api_avg"] = rating_api
        good_reads["api_rate_count"] = good_reads_rate_count
        return render_template("book.html" , book_info = book,errors=[], rating=ratings_count, reviews = data[::-1], has_not_submitted = has_not_submitted, good_reads=good_reads)
    else:
        rating_api = None
        good_reads_rate_count = None
        try:
            import requests
            res = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key=AIzaSyCq4YjdyQSiKxGoovJVNnwWdCfaXYNJQpo")
            res = res.json()

            if res["totalItems"] != 0:
                        rating_api = res["items"][0]["volumeInfo"]["averageRating"]
                        good_reads_rate_count = res["items"][0]["volumeInfo"]["ratingsCount"]
        except:
            pass
        good_reads = {}
        good_reads["api_avg"] = rating_api
        good_reads["api_rate_count"] = good_reads_rate_count
        if request.args.get("errors"):
            return render_template("book.html" , book_info = book, errors=["some of the elements are empty"] , has_not_submitted = True ,good_reads=good_reads , )
        return render_template("book.html" , book_info = book, errors=[] , has_not_submitted = True ,good_reads=good_reads , )
        
    return jsonify(data)

@app.route("/submit-review" , methods=["POST"])
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
        return redirect(url_for("getbookpage" , isbn=book_id))
    else:
        return redirect(url_for("getbookpage" ,isbn=book_id, errors="found"))

def predict_year(year):
    model = joblib.load("my-model.joblib")
    return (model.predict([[year]])[0])

app.cli.add_command(execute_command)

@app.route("/api/<isbn>")
@login_required
def send_json(isbn):
    db = get_db()
    reviews = []
    book = db.execute("SELECT * FROM Books where  isbn  = :book_id", {"book_id" : isbn.strip()}).fetchone()
    if not book:
        # return jsonify({"message" : "Book Not found"}),404
        return abort(404)
    reviews = db.execute(
        "SELECT USERS.f_name,USERS.l_name,USERS.u_name , USERS.profile_url, REVIEWS.book_id, REVIEWS.rate_count,REVIEWS.rate_desc  FROM USERS INNER JOIN REVIEWS ON USERS.u_name = REVIEWS.usr_id where  REVIEWS.book_id =  :isbn ;", {"isbn" : isbn.strip()}).fetchall()
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
        avg_rating =  (counter/(total_rows ))
        data = {}
        data["average_score"] =(avg_rating)
        data["title"] = book["title"]
        data["review_count"] = total_rows
        data["year"] = book["year"]
        data["isbn"] = book["isbn"]
        data["author"] = book["author"]
        return jsonify(data)
    else:
        data = {}
        data["average_score"] =(0.0)
        data["title"] = book["title"]
        data["review_count"] = 0
        data["year"] = book["year"]
        data["isbn"] = book["isbn"]
        data["author"] = book["author"]
        return jsonify(data)

@app.route("/calc-age" , methods=["POST"])
def calc_age(birth_date):
    birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
    today = date.today()
    return (today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day)))

