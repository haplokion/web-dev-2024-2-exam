import os

from flask_paginate import (
    Pagination,
    get_page_parameter
)

import io

from datetime import date

from flask import (
    Flask,
    render_template,
    flash,
    request,
    redirect,
    url_for,
    session,
    send_file
)
from flask_login import login_required, current_user

import markdown

import bleach
from hash import get_md5

UPLOAD_FOLDER = "./static/covers"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config.from_pyfile("config.py")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

from database import Database
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

def get_books():
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT * FROM books")
                cursor.execute(query)
                books = cursor.fetchall()
                return books
    except Exception as err:
        print(f"ERROR GET_BOOKS: {err}")

def get_book(book_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT * FROM books WHERE book_id=%s")
                cursor.execute(query, (book_id,))
                book = cursor.fetchone()
                return book
    except Exception as err:
        print(f"ERROR GET_BOOK: {err}")
        return None

def get_book_name(book_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT book_name FROM books WHERE book_id=%s")
                cursor.execute(query, (book_id,))
                book_name = cursor.fetchone().book_name
                return book_name
    except Exception as err:
        print(f"ERROR GET_BOOK_NAME: {err}")
        return None

def get_cover(cover_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT cover_name FROM covers WHERE cover_id=%s")
                cursor.execute(query, (cover_id,))
                cover = cursor.fetchone()
                return cover.cover_name
    except Exception as err:
        print(f"ERROR GET_COVER: {err}")

#Жанры книги из таблицы books_to_genres
def get_book_genres(book_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT genre_id FROM books_to_genres WHERE book_id=%s")
                cursor.execute(query, (book_id,))
                genres_ids = cursor.fetchall()
                
                list_of_genres = []
                for genre_id in genres_ids:
                    query = ("SELECT genre_name FROM genres WHERE genre_id=%s")
                    cursor.execute(query, (genre_id.genre_id,))
                    genre = cursor.fetchone().genre_name
                    list_of_genres.append(genre)
                genres = ', '.join(list_of_genres)
                return genres
    except Exception as err:
        print(f"ERROR GET_BOOK_GENRES: {err}")

#Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Сохранение файла
def save_file(file, filename):
    try:
        file.stream.seek(0)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return True
    except Exception as err:
        print(f"ERROR SAVE_FILE: {err}")
        return False

#Удаление файла
def delete_file(filename):
    try:
        path_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.remove(path_file)
        return True
    except Exception:
        return False

def get_review(user_id, book_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT * FROM reviews WHERE review_user=%s AND review_book=%s")
            cursor.execute(query, (user_id, book_id))
            review = cursor.fetchone()
            return review
    except Exception as err:
            print(f"GET_REVIEW: {err}")
            return False

def get_reviews(book_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT * FROM reviews WHERE review_book=%s")
                cursor.execute(query, (book_id,))
                reviews = cursor.fetchall()
                return reviews
    except Exception as err:
        print(f"ERROR GET_REVIEWS: {err}")
        return False

def get_login(user_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT user_login FROM users WHERE user_id=%s")
            cursor.execute(query, (user_id,))
            login = cursor.fetchone()
            return login.user_login
    except Exception as err:
            print(f"GET_LOGIN: {err}")
            return False

def get_reviews_amount(book_id):
    if get_reviews(book_id):
        return len(get_reviews(book_id))
    return 0

def get_rating(book_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT review_rating FROM reviews WHERE review_book=%s")
                cursor.execute(query, (book_id,))
                ratings = cursor.fetchall()
                
                if get_reviews_amount(book_id) != 0:
                    score = 0
                    for rate in ratings:
                        score += rate.review_rating
                    return round(score / get_reviews_amount(book_id), 1)
    except Exception as err:
        print(f"ERROR GET_RATING: {err}")
    return '-'

def set_visit(book_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            if current_user.is_authenticated:
                user_id = current_user.id

                query = ("INSERT INTO statistics(statistic_user, statistic_book) VALUES (%s, %s)")
                cursor.execute(query, (user_id, book_id))
            else:
                query = ("INSERT INTO statistics(statistic_book) VALUES (%s)")
                cursor.execute(query, (book_id,))
            db.connect().commit()
    except Exception as err:
        db.connect().rollback()
        print(f"ERROR SET_VISIT: {err}")
    return ''

def get_fio(user_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT * FROM users WHERE user_id=%s")
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            fio = user.user_surname + ' ' + user.user_name + ' ' + user.user_patronym
            return fio
    except Exception as err:
            print(f"GET_FIO: {err}")
            return "Неаутентифицированный пользователь"

@app.route("/export_csv")
def export_csv():
    with db.connect().cursor(named_tuple=True) as cursor:
        query = ('SELECT * FROM statistics')
        cursor.execute(query)
        statistics=cursor.fetchall()

        statistic=[]
        for i in statistics:
            string = {"id": i.statistic_id, "ФИО": get_fio(i.statistic_user), "Название книги": get_book_name(i.statistic_book), "Время посещения": i.statistic_created_at}
            statistic.append(string)

        print(statistic)
        data = load_data(statistic, ["id", "ФИО", "Название книги", "Время посещения"])
        download_name = "Статистика_" + str(date.today()) + ".csv"
        return send_file(data, as_attachment=True, download_name=download_name)

def load_data(records, fields):
    csv_data=", ".join(fields)+"\n"
    for record in records:
        csv_data += ", ".join([str(record[field]) for field in fields]) + "\n"
    print(csv_data)
    f = io.BytesIO()
    f.write(csv_data.encode("utf-8"))
    f.seek(0)
    return f

@app.route("/statistics")
@login_required
@checkRole('create')
def statistics():
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT * FROM statistics")
            cursor.execute(query)
            statistics = cursor.fetchall()
    except Exception:
        print(f"STATISTICS ERROR: {Exception}")
    
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    per_page = 10
    offset = (page - 1) * per_page
    if statistics != None:
        statistics_for_render = statistics[offset:offset + per_page]
        total = len(statistics)
    else:
        statistics_for_render = ''
        total = 0

    pagination = Pagination(page=page, total=total, search=search, record_name='statistics', per_page=per_page, offset=offset)

    return render_template("statistics.html", pagination=pagination, statistics=statistics_for_render, get_fio=get_fio, get_book_name=get_book_name)

@app.route("/")
def index():
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    per_page = 10
    offset = (page - 1) * per_page
    books = get_books()
    if books != None:
        books_for_render = books[offset:offset + per_page]
        total = len(books)
    else:
        books_for_render = ''
        total = 0

    pagination = Pagination(page=page, total=total, search=search, record_name='books', per_page=per_page, offset=offset)
    return render_template("index.html", books=books_for_render, get_cover=get_cover, get_book_genres=get_book_genres, delete_book=delete_book, pagination=pagination, get_reviews_amount=get_reviews_amount, get_rating=get_rating)

@app.route("/history")
def history():
    books = []
    for book_id in session["history"]:
        books.append(get_book(book_id))
    books = books[::-1]
    return render_template("history.html", books=books, get_cover=get_cover, get_book_genres=get_book_genres, get_reviews_amount=get_reviews_amount, get_rating=get_rating)

@app.route("/review/<int:book_id>", methods=["GET", "POST"])
@login_required
def review(book_id):
    if request.method == "POST":
        review_text = bleach.clean(request.form.get("review"))
        review_rating = request.form.get("rating")
        try:
            if not current_user.review(book_id):
                raise Exception("Рецензия существует")
            
            with db.connect().cursor(named_tuple=True) as cursor:
                query = ("INSERT INTO reviews (review_book, review_user, review_rating, review_text) VALUES (%s, %s, %s, %s)")
                cursor.execute(query, (book_id, current_user.id, review_rating, review_text))
                db.connect().commit()
            return redirect(url_for("show_book", book_id=book_id))

        except Exception as err:
            print(f"ERROR REVIEW: {err}")
            db.connect().rollback()
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
    return render_template("review.html", get_review=get_review)

@app.route('/show_book/<int:book_id>')
def show_book(book_id):
    book = get_book(book_id)
    reviews = get_reviews(book_id)
    if "history" not in session:
        session["history"] = [book_id]
    else:
        history_list = session["history"] + [book_id]
        session["history"] = history_list[-5:]

    if current_user.is_authenticated:
        user_review = get_review(current_user.id, book.book_id)
    else:
        user_review = False
    
    render_reviews = []

    for i in reviews:
        if not i == user_review:
            render_reviews.append(i)

    return render_template('show_book.html', book = book, get_cover=get_cover, get_book_genres=get_book_genres, markdown=markdown, get_login=get_login, reviews=render_reviews, user_review=user_review, set_visit=set_visit)

@app.route('/delete_book/<int:book_id>')
@login_required
@checkRole("delete")
def delete_book(book_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("DELETE FROM books WHERE book_id=%s")
                cursor.execute(query, (book_id,))
                db.connect().commit()
                flash("Удаление успешно", "success")
    except Exception as err:
        flash("Ошибка при удалении книги", "danger")
        db.connect().rollback()
        print(f"ERROR DELETE_BOOK: {err}")
    return redirect(url_for("index"))

@app.route("/create_book", methods=["GET", "POST"])
@login_required
@checkRole("create")
def create_book():
    genres = get_genres()

    if request.method == "POST":
        book_name = request.form.get("name")
        book_description = bleach.clean(request.form.get("description"))
        book_year = request.form.get("year")
        book_publisher = request.form.get("publisher")
        book_author = request.form.get("author")
        book_size = request.form.get("size")
        cover = request.files.get("cover")
        book_genres = request.form.getlist("genres")

        cover_data = cover.read()
        cover_MD5_hash = get_md5(cover_data)
        cover_name = cover_MD5_hash + '.' + cover.filename.rsplit('.', 1)[1].lower()
        cover_mime_type = cover.mimetype

        try:
            if not allowed_file(cover.filename):
                raise Exception("Файл недопустимого расширения")

            with db.connect().cursor(named_tuple=True) as cursor:
                #Проверка на наличие обложки в БД
                query = ("SELECT cover_id FROM covers WHERE cover_MD5_hash=%s")
                cursor.execute(query, (cover_MD5_hash,))
                cover_id = cursor.fetchone()

                if cover_id == None:
                    query = ("INSERT INTO covers (cover_name, cover_mime_type, cover_MD5_hash) VALUES (%s, %s, %s)")
                    cursor.execute(query, (cover_name, cover_mime_type, cover_MD5_hash))
                    cover_id = cursor.lastrowid

                    book_cover = cover_id
                    query = ("INSERT INTO books (book_name, book_description, book_year, book_publisher, book_author, book_size, book_cover) VALUES (%s, %s, %s, %s, %s, %s, %s)")
                    cursor.execute(query, (book_name, book_description, book_year, book_publisher, book_author, book_size, book_cover))

                    book_id = cursor.lastrowid
                    genre_ids = book_genres
                    for genre_id in genre_ids:
                        query = ("INSERT INTO books_to_genres (book_id, genre_id) VALUES (%s, %s)")
                        cursor.execute(query, (book_id, genre_id))

                    if not save_file(cover, cover_name):
                        raise Exception
                else:
                    book_cover = cover_id.cover_id
                    query = ("INSERT INTO books (book_name, book_description, book_year, book_publisher, book_author, book_size, book_cover) VALUES (%s, %s, %s, %s, %s, %s, %s)")
                    cursor.execute(query, (book_name, book_description, book_year, book_publisher, book_author, book_size, book_cover))

                    book_id = cursor.lastrowid
                    genre_ids = book_genres
                    for genre_id in genre_ids:
                        query = ("INSERT INTO books_to_genres (book_id, genre_id) VALUES (%s, %s)")
                        cursor.execute(query, (book_id, genre_id))
                db.connect().commit()
            return redirect(url_for("show_book", book_id=book_id))

        except Exception as err:
            print(f"ERROR CREATE_BOOK: {err}")
            db.connect().rollback()
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
        return render_template("create_book.html", genres = genres, extensions = ALLOWED_EXTENSIONS, request=request)
    
    return render_template("create_book.html", genres = genres, extensions = ALLOWED_EXTENSIONS)

@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
@login_required
@checkRole("edit")
def edit_book(book_id):
    genres = get_genres()
    book_genres = get_book_genres(book_id).split(", ")

    if request.method == "POST":
        book_name = request.form.get("name")
        book_description = bleach.clean(request.form.get("description"))
        book_year = request.form.get("year")
        book_publisher = request.form.get("publisher")
        book_author = request.form.get("author")
        book_size = request.form.get("size")
        book_genres = request.form.getlist("genres")

        try:
            with db.connect().cursor(named_tuple=True) as cursor:
                query = ("UPDATE books SET book_name=%s, book_description=%s, book_year=%s, book_publisher=%s, book_author=%s, book_size=%s WHERE book_id=%s")
                cursor.execute(query, (book_name, book_description, book_year, book_publisher, book_author, book_size, book_id))

                genre_ids = book_genres
                for genre_id in genre_ids:
                    query = ("DELETE FROM books_to_genres WHERE book_id=%s")
                    cursor.execute(query, (book_id, ))
                    query = ("INSERT INTO books_to_genres (book_id, genre_id) VALUES (%s, %s)")
                    cursor.execute(query, (book_id, genre_id))
                db.connect().commit()
            return redirect(url_for("show_book", book_id=book_id))

        except Exception as err:
            print(f"ERROR EDIT_BOOK: {err}")
            db.connect().rollback()
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
        return render_template("edit_book.html", genres = genres, name = book_name, description = book_description, year = book_year, publisher = book_publisher, author = book_author, size = book_size, book_genres = book_genres)
    book = get_book(book_id)
    book_name = book.book_name
    book_description = book.book_description
    book_year = book.book_year
    book_publisher = book.book_publisher
    book_author = book.book_author
    book_size = book.book_size
    
    return render_template("edit_book.html", genres = genres, name = book_name, description = book_description, year = book_year, publisher = book_publisher, author = book_author, size = book_size, book_genres = book_genres)