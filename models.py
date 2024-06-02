from flask_login import UserMixin

from werkzeug.security import (
    generate_password_hash, 
    check_password_hash
)

class User(UserMixin):
    def __init__(self, user_id, user_login):
        self.id = user_id
        self.login = user_login