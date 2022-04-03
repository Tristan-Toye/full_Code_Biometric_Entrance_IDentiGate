from flask import Flask
import json
import os
from flask_restful import Resource, Api
from queue import Queue
from flask_mqtt import Mqtt
from flask_leaving_ui.Constants import *




class ConfigClass(object):
    """ Flask application config """

    SECRET_KEY = os.urandom(20).hex()

    SQLALCHEMY_DATABASE_URI = 'sqlite:///test2.db'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    MQTT_CLIENT_ID = 'Sending_data'
    MQTT_BROKER_URL = "192.168.137.1"
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = username
    MQTT_PASSWORD = password
    MQTT_KEEPALIVE = 5
    MQTT_LAST_WILL_TOPIC = FAILING_PATH
    MQTT_LAST_WILL_MESSAGE = failing_message
    MQTT_LAST_WILL_QOS = 0





app = Flask(__name__, template_folder='templates')
api = Api(app)

app.config.from_object(__name__ + '.ConfigClass')

q_validate_QR = Queue()
q_leaving_QR = Queue()

mqtt = Mqtt(app)


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


@mqtt.on_disconnect()
def handle_on_disconnect(client, userdata, msg):
    if msg == MQTT_SUCCES:
        print("Shutting down confirmed")
    else:
        print("starting reconnecting protocol")
        print("Delay is doubled between subsequent reconnections ")

@mqtt.on_topic(RESPONSE_LEAVING_QR)
def handle_response_leaving(client, userdata, msg):
    print("in de handle response leaving")
    msg = json.loads(msg.payload)
    status = msg['message']
    reason = msg['reason']
    print(status)
    print(reason)
    if status == 'True':
        q_leaving_QR.put(msg, block=True)

    else:
        q_leaving_QR.put(msg, block=True)



from flask_leaving_ui import Routes
from flask_leaving_ui import Backend_Api
