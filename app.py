from flask import (
    Flask,
    Blueprint,
    render_template,
    flash
)

from models import User

from flask_login import LoginManager

import mysql.connector
from database import Database

app = Flask(__name__)

app.config.from_pyfile('config.py')

db = Database(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Для выполнения данного действия необходимо пройти процедуру аутентификации"
login_manager.login_message_category = "warning"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    query = ("SELECT * FROM users WHERE user_id=%s")
    user = send_query(query, user_id)
    if user:
       return User(user.id,user.login)
    return None

query = "show tables;"

def send_query(query, *arg):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                cursor.execute(query, arg)
                response = cursor.fetchall()
                db.connect().commit()
        return response
    except mysql.connector.errors.DatabaseError as err:
        db.connect().rollback()
        print(f"ERROR: {err}")
        return f"ERROR: {err}"

@app.route('/')
def index():
    a = send_query(query)
    flash("Успешно проверили", "success")
    return render_template("base.html")
