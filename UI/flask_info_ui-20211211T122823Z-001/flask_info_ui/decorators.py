from flask_info_ui.constants import *
from flask_info_ui import mqtt, q_check_database, q_log_database, q_validate_QR
import json


@mqtt.on_connect()
def handle_on_connect(client, userdata, flags, rc):
    print("Connection succesfull")
    client.subscribe(LIST_CONNECT)


@mqtt.on_subscribe()
def handle_on_subscribe(client, userdata, mid, granted_qos):
    if len(granted_qos) == len(LIST_PATH):
        print("all subscription confirmed")
    else:
        number_missing_subscription = str(len(LIST_PATH) - len(granted_qos))
        print("missing" + number_missing_subscription + "subscriptions")
        assert False


@mqtt.on_disconnect()
def handle_on_disconnect(client, userdata, msg):
    if msg == MQTT_SUCCES:
        print("Shutting down confirmed")
    else:
        print("starting reconnecting protocol")
        print("Min_delay:" + str(userdata['Min_delay']) + " seconds")
        print("Max_delay:" + str(userdata['Max_delay']) + " seconds")
        print("Delay is doubled between subsequent reconnections ")


@mqtt.on_topic(RESPONSE_CHECK_DATABASE)
def handle_check_db(client, userdata, message):
    print("dit is de check db")
    q_check_database.put(message.payload)


@mqtt.on_topic(RESPONSE_VALIDATE_QR)
def handle_function_response_validate_QR(client, userdata, msg):
    msg = json.loads(msg.payload)

    print("zonder decode:")
    print(msg.payload)
    print("met decode:")
    print(msg.payload.decode())
    q_validate_QR.put(msg.payload, block=True)
    # q_validate_QR.put(msg.payload.decode(),block=True)


@mqtt.on_topic(RESPONSE_LOG_DATABASE)
def handle_function_response_log_dabase(client, userdata, msg):
    q_log_database.put(msg.payload)
