from flask import (
    Blueprint,
    render_template,
    flash,
    request,
    redirect,
    url_for,
    session
)

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    current_user
)

from functools import wraps

from check_rights import CheckRights

from app import db

bp = Blueprint("auth", __name__)

ADMIN_ROLE_ID = 1
MODERATOR_ROLE_ID = 2
USER_ROLE_ID = 3

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Для выполнения данного действия необходимо пройти процедуру аутентификации"
    login_manager.login_message_category = "warning"
    login_manager.user_loader(load_user)

class User(UserMixin):
    def __init__(self, id, login, surname, name, patronym, role):
        self.id = id
        self.login = login
        self.surname = surname
        self.name = name
        self.patronym = patronym
        self.role = role

    def is_admin(self):
        return ADMIN_ROLE_ID == self.role
    
    def is_moderator(self):
        return MODERATOR_ROLE_ID == self.role
    
    def is_user(self):
        return USER_ROLE_ID == self.role
    
    def can(self, action, record=None):
        check_rights = CheckRights(record)
        method = getattr(check_rights, action, None)
        if method:
            return method()
        return False
    
    def review(self, book_id):
        try:
            with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT review_id FROM reviews WHERE review_user=%s AND review_book=%s")
                cursor.execute(query, (self.id, book_id))
                review_id = cursor.fetchone()
                if review_id == None:
                    return True
        except Exception as err:
            print(f"USER: {err}")
            return False

def load_user(user_id):
    try:
        with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT * FROM users WHERE user_id=%s")
                cursor.execute(query, (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(user_data.user_id, user_data.user_login, user_data.user_surname, user_data.user_name, user_data.user_patronym, user_data.user_role)
    except Exception as err:
        print(f"ERROR LOAD_USER: {err}")
    return None

def checkRole(action):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            user = None
            if user_id:
                user = load_user(user_id)
            if current_user.can(action,record=user) :
                return f(*args, **kwargs)
            flash("У вас недостаточно прав для выполнения данного действия", "danger")
            return redirect(url_for("index"))
        return wrapper
    return decorator

from hash import get_hash
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user_login = request.form.get("login")
        user_password = request.form.get("password")
        remember = request.form.get("remember")

        user_password_hash = get_hash(user_login, user_password)

        try:
            with db.connect().cursor(named_tuple=True) as cursor:
                query = ("SELECT * FROM users WHERE user_login=%s and user_password_hash=%s")
                cursor.execute(query, (user_login, user_password_hash))
                user_data = cursor.fetchone()

                if user_data:
                    login_user(User(user_data.user_id, user_data.user_login, user_data.user_surname, user_data.user_name, user_data.user_patronym, user_data.user_role), remember=remember)
                    flash("Вы успешно прошли аутентификацию", "success")
                    return redirect(url_for("index"))
            flash("Невозможно аутентифицироваться с указанными логином и паролем", "danger")
        except Exception as err:
            print(f"ERROR LOGIN: {err}")
    return render_template("login.html")

@bp.route('/logout')
def logout():
    session.pop("history", None)
    logout_user()
    return redirect(url_for('index'))