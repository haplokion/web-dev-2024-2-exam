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

from models import User

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = Database(app)

from auth import bp as bp_auth, init_login_manager
app.register_blueprint(bp_auth)
init_login_manager(app)

# def send_query(query, *arg):
#     try:
#         with db.connect().cursor(named_tuple=True) as cursor:
#                 cursor.execute(query, arg)
#                 response = cursor.fetchall()
#                 db.connect().commit()
#         return response
#     except mysql.connector.errors.DatabaseError as err:
#         db.connect().rollback()
#         print(f"ERROR: {err}")
#         return f"ERROR: {err}"


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/history')
def history():
    return render_template("history.html")

@app.route('/top_books')
@login_required
def top_books():
    return render_template("base.html")
