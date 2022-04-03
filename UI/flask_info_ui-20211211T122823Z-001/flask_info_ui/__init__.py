from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_restful import Resource, Api
from queue import Queue
from flask_mqtt import Mqtt
from flask_info_ui.constants import *
from flask_session import Session
import json

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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test2.db'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    MQTT_CLIENT_ID = 'Sending_data'
    MQTT_BROKER_URL = "192.168.137.1"
    MQTT_BROKER_PORT = 1883  # encrypted, 1883 default
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
    SESSION_TYPE ='sqlalchemy'
    SESSION_SQLALCHEMY_TABLE='session_sqlalchemy'
    SESSION_PERMANENT= True


# root path = C:\Users\trist\OneDrive - KU Leuven\2021_2022\PO3\files\flask_info ( zie flask_app.py)
app = Flask(__name__, template_folder='templates_arne')
api = Api(app)

app.config.from_object(__name__ + '.ConfigClass')
db = SQLAlchemy(app)  # sql database
app.config['SESSION_SQLALCHEMY'] = db
q_check_database = Queue()
q_validate_QR = Queue()
q_log_database = Queue()
q_role_database = Queue()
q_vein_messaging =  Queue()
q_compare_databases = Queue()
q_vein_messaging_add = Queue()
q_face_messaging_add = Queue()

mqtt = Mqtt(app)
# mqtt.init_app(app)
mqtt.userdata = connection_params
#--------------------------------




@mqtt.on_connect()
def handle_on_connect(client, userdata, flags, rc):
    print(LIST_CONNECT)
    print("connections succesfull")
    for topic in LIST_PATH:
        mqtt.subscribe(topic, qos=2)


@mqtt.on_subscribe()
def handle_on_subscribe(client, userdata, mid, granted_qos):
    if mid == len(LIST_PATH):
        print("all_subscription succesfully established")
    else:
        print("waiting for subscriptions")

'''
@mqtt.on_disconnect()
def handle_on_disconnect(client, userdata, msg):
    if msg == MQTT_SUCCES:
        print("Shutting down confirmed")
    else:
        print("starting reconnecting protocol")
        print("Delay is doubled between subsequent reconnections ")
'''

@mqtt.on_topic(RESPONSE_CHECK_DATABASE)
def handle_check_db(client, userdata, message):
    print("ik zit in de chack database")
    msg = json.loads(message.payload)
    print(msg)
    
    q_check_database.put(msg)


@mqtt.on_topic(RESPONSE_VALIDATE_QR)
def handle_function_response_validate_QR(client, userdata, msg):
    msg = json.loads(msg.payload)
    if msg['message'] == "False":
        print("handle function response validate qr:")
        print(msg)
        q_validate_QR.put("False", block=True)

    else:
        print("handle function response validate qr:")
        print(msg)
        del msg["message"]
        q_validate_QR.put(msg, block=True)
        # q_validate_QR.put(msg.payload.decode(),block=True)


@mqtt.on_topic(RESPONSE_LOG_DATABASE)
def handle_function_response_log_dabase(client, userdata, msg):
    msg = json.loads(msg.payload)
    print("response database")
    print(msg)
    q_log_database.put(msg['message'])


@mqtt.on_topic(RESPONSE_ROLE_REQUEST_DATABASE)
def handle_function_response_role_request_database(client,userdata,msg):
    print("in handle role request function")
    msg = json.loads(msg.payload)
    print(msg)
    q_role_database.put(msg)


@mqtt.on_topic(REMOVED_USERS)
def handle_function_removed_users(client, userdata, msg):
    print("removed users topic")
    print(json.loads(msg.payload))
    from flask_info_ui.models_ui import User
    for national_number in json.loads(msg.payload):
        user = User.query.filter_by(national_number=national_number).first()

        if user:
            db.session.delete(user)
            db.session.commit()

@mqtt.on_topic(RESPONSE_COMPARE_DATABASES)
def handle_response_compare_database(client,userdata,msg):
    
    msg = json.loads(msg.payload)
    print(msg)
    status = msg['message']
    if status == 'True':
        q_compare_databases.put(msg, block=True)
    else:
        q_compare_databases.put(msg, block=True)




# mqtt.connect(broker_address)
from flask_info_ui import routes_functions_ui
#from flask_info_ui import decorators
