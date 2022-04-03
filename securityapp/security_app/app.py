from flask import Flask, render_template, flash
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_user import UserMixin
from flask_sqlalchemy import SQLAlchemy
import json
import os
app = Flask(__name__,static_folder="templates_with_css",template_folder="templates_with_css")
username = "CW2B2"
password = "KULeuven"
SECURITY = "security"
LIST_PATH = [SECURITY]
FAILING_PATH = "failing"
failing_message = "UI failed"
BROKER_ADDRESS = "192.168.137.1"



class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    # extra layer of protection needed for form HTML
    # random string generated:
    # import os
    # os.urandom(12).hex()
    SECRET_KEY = os.urandom(20).hex()
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'    # File-based SQL database
    SQLALCHEMY_DATABASE_URI = "postgresql://wtdjzngqqcdejo:816569dfc06e2457582ec73f6f43e576e57cb3aa1c1f915466afd4f3e7936a5a@ec2-34-242-89-204.eu-west-1.compute.amazonaws.com:5432/dc3lnlv8ph2q1i"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning
    # Flask-SQLAlchemy settings
    # you need to CONFIG for pythonanywhere

    MQTT_CLIENT_ID = 'security_app'
    MQTT_BROKER_URL = BROKER_ADDRESS
    MQTT_BROKER_PORT = 1883  # encrypted 8883, 1883 default
    MQTT_USERNAME = username
    MQTT_PASSWORD = password
    MQTT_KEEPALIVE = 5

    # MQTT_TLS_ENABLED =
    # MQTT_TLS_CA_CERTS =
    # MQTT_TLS_CERTFILE =
    # MQTT_TLS_KEYFILE =
    # MQTT_TLS_CERT_REQS =
    # MQTT_TLS_VERSION =
    # MQTT_TLS_CIPHERS =
    # MQTT_TLS_INSECURE =
    MQTT_LAST_WILL_TOPIC = FAILING_PATH
    MQTT_LAST_WILL_MESSAGE = failing_message
    MQTT_LAST_WILL_QOS = 0  # no confirmation
    # MQTT_TRANSPORT ="websockets"
    #MQTT_USER_DATA_SET = connection_params


# root path = C:\Users\trist\OneDrive - KU Leuven\2021_2022\PO3\files\flask_info ( zie flask_app.py)

app.config.from_object(ConfigClass)
db = SQLAlchemy(app)
mqtt = Mqtt(app)
socketio = SocketIO(app)

mqtt.subscribe(SECURITY)

class User(db.Model, UserMixin): # additional class attributes (ctrl +b to inspect)
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(),nullable=False)
    national_number = db.Column(db.String(), nullable=False,unique=True)
    email_address = db.Column(db.String(),nullable=False, unique=True)
    password = db.Column(db.String(),nullable=False)
    faces = db.Column(db.PickleType())
    roles = db.relationship('Role',secondary='user_roles')
    qr_leave = db.Column(db.String(), nullable=False, unique=True)
    qr_leave_code = db.Column(db.String(), nullable=False, unique=True)


    def __repr__(self):  # to change view in database
        return f'Item {self.username}'
class UserRoles(db.Model):
    __tablename__='user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id',onupdate='CASCADE', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id',onupdate='CASCADE', ondelete='CASCADE'))

class Role(db.Model):
    __tablename__ = 'roles'
    #Role.users is users classes with this role
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(),unique=True,nullable=False)

    def __repr__(self): # to change view in database
        return f'Item {self.name}'

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

@mqtt.on_topic(SECURITY)
def function_security(client, userdata, message):

    print("dit is de security")

    msg = json.loads(message.payload)
    print(msg)
    data={}
    if 'code' in msg:
        user = User.query.filter_by(national_number=msg['national_number']).first()
        print(user)
        data['category'] = 'danger'
        data['text'] = f'invalid qr code given by {user.username}'
    elif 'backup' in msg:
        user = User.query.filter_by(national_number=msg['national_number']).first()
        print(user)
        data['category'] = 'info'
        data['text'] = f'{user.username} logged in using the backup'
    elif 'msg' in msg:
        data['category'] = 'danger'
        data['text'] = msg['msg']
    elif 'message' in msg:
        data['category'] = 'danger'
        data['text'] = msg['message']
    print(data)
    socketio.emit("security",data)


@app.route('/')
def hello_world():  # put application's code here
    flash("security is alerted",category="info")
    flash("2",category="danger")
    return render_template('template.html')

if __name__ == '__main__':
    app.run(debug=True)