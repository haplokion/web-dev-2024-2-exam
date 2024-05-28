import mysql.connector
from flask import g

class Database:
    def __init__(self, app):
        self.app = app

    def get_config(self):
        return {
            "host": self.app.config["DB_HOST"],
            "user": self.app.config["DB_USER"],
            "password": self.app.config["DB_PASSWORD"],
            "database": self.app.config["DB_NAME"]
        }
    
    def connect(self):
        if 'db' not in g:
            g.db = mysql.connector.connect(**self.get_config())
        return g.db
    
    def close(self):
        