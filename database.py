import mysql.connector
from flask import g

# class Database:
#     def __init__(self, app):
#         self.app = app
#         self.app.teardown_appcontext(self.__exit__)

#     def get_config(self):
#         try:
#             return {
#                 "host": self.app.config["DB_HOST"],
#                 "user": self.app.config["DB_USER"],
#                 "password": self.app.config["DB_PASSWORD"],
#                 "database": self.app.config["DB_NAME"]
#             }
#         except Exception as err:
#             print(f"ERROR Database get_config: {err}")
    
#     def connect(self):
#         try:
#             if 'db' not in g:
#                 g.db = mysql.connector.connect(**self.get_config())
#             return g.db
#         except Exception as err:
#             print(f"ERROR Database connection: {err}")

#     def __exit__(self, e=None):
#        db = g.pop('db', None)
#        if db is not None:
#            db.close()


class Database:
    def __init__(self, app):
        self.app = app
        self.app.teardown_appcontext(self.close_db)
        
    def get_config(self):
        try:
            return {
                'user': self.app.config['MYSQL_USER'],
                'password': self.app.config['MYSQL_PASSWORD'],
                'host': self.app.config['MYSQL_HOST'],
                'database': self.app.config['MYSQL_DATABASE']
            }
        except Exception as err:
            print(f"ERROR: {err}")
    
    def connect(self):
        if 'db' not in g:
            g.db = mysql.connector.connect(**self.get_config())
        return g.db
    
    def close_db(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
    