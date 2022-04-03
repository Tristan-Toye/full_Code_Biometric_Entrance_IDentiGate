from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# C:\Users\trist\OneDrive - KU Leuven\2021_2022\PO3\files\venv\Lib\site-packages\flask_user


class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    # extra layer of protection needed for form HTML
    # random string generated:
    # import os
    # os.urandom(12).hex()
    SECRET_KEY = os.urandom(20).hex()

    # Flask-SQLAlchemy settings
    # you need to CONFIG for pythonanywhere
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test2.db'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning


# root path = C:\Users\trist\OneDrive - KU Leuven\2021_2022\PO3\files\flask_info ( zie flask_app.py)
app = Flask(__name__)

app.config.from_object(__name__+'.ConfigClass')
db = SQLAlchemy(app) # sql database


from flask_info_ui import routes_functions_ui
