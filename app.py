from flask import (
    Flask,
    Blueprint,
    render_template,
    flash
)

from flask_login import LoginManager

import mysql.connector
from database import Database

app = Flask(__name__)

app.config.from_pyfile('config.py')

db = Database(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Для выполнения данного действия необходимо пройти процедуру аутентификации"
login_manager.login_message_category = "warning"

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

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

query = "show tables;"

@app.route('/')
def index():
    a = send_query(query)
    flash("SUCCEEES", "error")
    return render_template("index.html")