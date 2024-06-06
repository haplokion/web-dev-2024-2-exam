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
    return render_template("create_book.html")