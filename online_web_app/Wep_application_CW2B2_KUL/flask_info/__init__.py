from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
import os
from flask_session import Session
import pyotp
from flask_info.constants import *
from uuid import uuid4
# C:\Users\trist\OneDrive - KU Leuven\2021_2022\PO3\files\venv\Lib\site-packages\flask_user
app = Flask(__name__,static_folder='templates_with_css',template_folder='templates_with_css')

class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    # extra layer of protection needed for form HTML
    # random string generated:
    # import os
    # os.urandom(20).hex()
    SECRET_KEY = '2a851f80efde7b9a2e10c9ada37b031193e8fb60'

    # Flask-SQLAlchemy settings
    # you need to CONFIG for pythonanywhere
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'    # File-based SQL database
    SQLALCHEMY_DATABASE_URI = "postgresql://wtdjzngqqcdejo:816569dfc06e2457582ec73f6f43e576e57cb3aa1c1f915466afd4f3e7936a5a@ec2-34-242-89-204.eu-west-1.compute.amazonaws.com:5432/dc3lnlv8ph2q1i"
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = False # stond True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'email@example.com'
    MAIL_PASSWORD = 'password'
    MAIL_DEFAULT_SENDER = '"MyApp" <noreply@example.com>'

    # Flask-User settings
    USER_APP_NAME = "Flask-User Basic App"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False        # Enable email authentication
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"

    SESSION_TYPE = 'sqlalchemy'
    SESSION_SQLALCHEMY_TABLE = 'session_sqlalchemy'
   
    #WEIRDEST ERROR EVER
    #SESSION_KEY_PREFIX = ""
    #SESSION_COOKIE_NAME = uuid4()
    DEBUG = True

app.config.from_object(__name__+'.ConfigClass')
db = SQLAlchemy(app) # sql database
app.config['SESSION_SQLALCHEMY'] = db
#bcrypt = Bcrypt(app) # hashed password
session_ = Session(app)
socketio = SocketIO(app,manage_session=False) # socket
# root path = C:\Users\trist\OneDrive - KU Leuven\2021_2022\PO3\files\flask_info ( zie flask_app.py)
time_based_pin = pyotp.TOTP(secret_key_pyotp)

from flask_info import routes_functions
from flask_info import decorators
