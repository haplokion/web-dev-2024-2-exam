from flask import (
    Flask,
    render_template,
    flash,
    request,
    redirect,
    url_for
)

from flask_login import login_required, current_user

import mysql.connector
from database import Database

app = Flask(__name__)
app.config.from_pyfile("config.py")

db = Database(app)

from auth import bp as bp_auth, init_login_manager, checkRole
app.register_blueprint(bp_auth)
init_login_manager(app)

#Жанры из таблицы genres
def get_genres():
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT * FROM genres")
                cursor.execute(query)
                genres = cursor.fetchall()
                return genres
    except Exception as err:
        print(f"ERROR GET_GENRES: {err}")

#Жанры книги из таблицы books_to_genres
def get_book_genres(book_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT genre_id FROM books_to_genres WHERE book_id=%s")
                cursor.execute(query, (book_id,))
                genres_ids = cursor.fetchall()
                return genres_ids
    except Exception as err:
        print(f"ERROR GET_BOOK_GENRES: {err}")

#Запись в таблицу books_to_genres
def set_book_genres(book_id, genre_ids):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                for genre_id in genre_ids:
                    query = ("INSERT INTO books_to_genres (book_id, genre_id) VALUES (%s, %s)")
                    cursor.execute(query, (book_id, genre_id))
                db.connect().commit()
                return 
    except Exception as err:
        db.connect().rollback()
        print(f"ERROR SET_BOOK_GENRES: {err}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/top_books")
@login_required
def top_books():
    return render_template("top_books.html")

@app.route("/create_book")
@login_required
@checkRole("create")
def create():
    genres = get_genres()
    print(genres)
    return render_template("create_book.html", genres = genres)