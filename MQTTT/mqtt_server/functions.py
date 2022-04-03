from mqtt_server.constants import *
import json
from mqtt_server.models import User,Log,Role
def evaluate_connection(rc,connection_params):

    if rc == 0:
        print(connection_params[rc])
    else:
        print("system error confirmed, given by library mqtt server:")
        print(connection_params[rc])
        assert False

    pass
def on_subscribe(client,userdata,mid,granted_qos):
    if len(granted_qos) == len(LIST_PATH):
        print("all subscription confirmed")
    else:
        number_missing_subscription = str(len(LIST_PATH) - len(granted_qos))
        print("missing" + number_missing_subscription + "subscriptions")

        assert False
def on_disconnect(client,userdata,msg):
    if msg == MQTT_SUCCES:
        print("Shutting down confirmed")
    else:
        print("starting reconnecting protocol")
        print("Min_delay:" + str(userdata['Min_delay']) + " seconds")
        print("Max_delay:" + str(userdata['Max_delay']) + " seconds")
        print("Delay is doubled between subsequent reconnections ")
def on_connect(client, userdata, flags, rc):

    evaluate_connection(rc,userdata)

    #client.subscribe([(MQTT_PATH,qos),(MQTT_PATH_2,qos),(FAILING_PATH,0)])
    client.subscribe(LIST_CONNECT)
def on_publish(client, userdata, flags):
    print("publish successful confirmed")
"""
Functions for callbacks
"""
def function_check_database(client,userdata,msg):
    # msg is string type
    print("function_check_database")

    msg = json.loads(msg.payload)
    print(msg)
    print("--------------------------")
    sent_dict = {'message': 'True'}
    client.publish(RESPONSE_CHECK_DATABASE, json.dumps(sent_dict), qos=2)


def function_log_database(client,userdata,msg):
    print('function_log_database')
    # msg is dict type
    msg = json.loads(msg.payload)

    print("Name:")
    print(msg['person'])

    # put in database SQLAlchemy
    send_dict = {'message': 'True'}
    client.publish(RESPONSE_LOG_DATABASE, json.dumps(send_dict), qos=2)


def function_validate_QR(client,userdata,msg):
    print('function_validate_QR')
    # msg is dict type
    msg = json.loads(msg.payload)
    print(msg)
    msg = json.dumps(msg)

    # check in database, FOUT:
    #client.publish(RESPONSE_VALIDATE_QR,'False',qos=2)
    #correct:
    #msg = {"voornaam": 'False'}
    #msg =json.dumps( msg )
    client.publish(RESPONSE_VALIDATE_QR,msg,qos=2)
    #client.publish(RESPONSE_VALIDATE_QR,msg.payload.decode(),qos=2)

def function_security(client,userdata,msg):
    print('function_security')
    # msg is dict type
    msg=json.loads(msg.payload)
    print("Security:")
    print(msg)

def function_role_request_database(client,userdata,msg):
    print("function_role_request_database")
    msg=json.loads(msg.payload)
    national_number = msg["rijksregister"]

    msg_send=json.dumps( {  "rijksregister" : national_number,
                            "role"          :'admin',
                            'random_key'    :msg["random_key"]})
    client.publish(RESPONSE_ROLE_REQUEST_DATABASE,msg_send,qos=2)
