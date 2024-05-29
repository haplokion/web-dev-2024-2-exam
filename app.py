from flask import Flask, render_template, redirect, url_for, request, make_response, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import mysql.connector
import re
from database import Database

app = Flask(__name__)

app.config.from_pyfile('config.py')

db = Database(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'
login_manager.login_message = 'Доступ к данной странице есть только у авторизованных пользователей '
login_manager.login_message_category = 'warning'

query = "show tables;"

def get_roles():
    with db.connect().cursor(named_tuple=True) as cursor:
            query = ('SELECT * FROM roles')
            cursor.execute(query)
            roles = cursor.fetchall()
    return roles


@app.route('/')
def index():
    with db.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        roles = cursor.fetchall()
        print(roles)
        return roles
