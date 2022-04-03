from mqtt_server.constants import *
import json
from sqlalchemy.orm import close_all_sessions
from mqtt_server.models import User,Log,QR,QR_VISITOR
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


import datetime
import time
import hashlib
def hash_string(str_tohash, salt):
    return hashlib.pbkdf2_hmac(
        'sha256',
        str_tohash.encode('utf-8'),
        salt,
        10000,
        dklen=64
    )



def function_filter_hash(national_number,already_hashed = False):
    if not already_hashed:
        print( "not hashed")
        national_number_hash = str(hash_string(national_number,SALT))[2:-1]
    else:
        print('hashed')
        national_number_hash = national_number
    lijst_hash = list(national_number_hash)

    lijst_hash_encoded = [ord(char) for char in lijst_hash]
    hash = ''.join([chr(code) for code in lijst_hash_encoded if
                          47 < code < 58 or 64 < code < 91 or 96 < code < 123])  # 1-9,A-Z,a-z

    if not already_hashed:
        return hash[:32]
    return hash

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
    # msg is dict type
    db = create_engine(db_string)
    session_db = sessionmaker(db)()
    print("function_check_database")

    msg = json.loads(msg.payload)
    print(msg)
    user = session_db.query(User).filter_by(national_number=msg['national_number']).first()
    if user:
        sent_dict = {'message': 'True',
                     'reason' : 'account exist'}
        client.publish(RESPONSE_CHECK_DATABASE, json.dumps(sent_dict), qos=2)
    else:
        sent_dict = {'message': 'False',
                     'reason' : 'Account does not exist on website'}
        client.publish(RESPONSE_CHECK_DATABASE,json.dumps(sent_dict),qos=2)
    print("close session")
    close_all_sessions()
    #session_db.close()
def function_log_database(client,userdata,msg):
    db = create_engine(db_string)
    session_db = sessionmaker(db)()
    print('function_log_database')
    # msg is dict type
    msg = json.loads(msg.payload)

    print("Name:")
    print(msg['person'])
    existing_log = session_db.query(Log).filter_by(date_exit=None).filter(Log.user.any(national_number=msg['national_number'])).first()
    if existing_log:
        existing_log.date_exit = datetime.datetime.now()
        session_db.commit()

    else:
        log = Log(date_entry=datetime.datetime.now())
        log.user.append(session_db.query(User).filter_by(national_number=msg['national_number']).first())
        session_db.add(log)
        session_db.commit()
    print("Logged succesfull")
    # put in database SQLAlchemy
    send_dict = {'message':'True'}
    client.publish(RESPONSE_LOG_DATABASE,json.dumps(send_dict),qos=2)
    print("close session")
    close_all_sessions()
def function_validate_QR(client,userdata,msg):
    db = create_engine(db_string)
    session_db = sessionmaker(db)()
    print('function_validate_QR')
    # msg is dict type
    msg = json.loads(msg.payload)
    print(msg)
    national_number = function_filter_hash(msg['national_number'],already_hashed = True)
    qr_code = session_db.query(QR).filter(QR.user.any(national_number=national_number)).filter_by(code=msg['code']).first()
    print(session_db.query(QR).filter(QR.user.any(national_number=national_number)))
    print(qr_code)
    if qr_code:

        msg['message']='True'
        session_db.delete(qr_code)
        session_db.commit()
        print("deleted")
        client.publish(RESPONSE_VALIDATE_QR, json.dumps(msg), qos=2)

        """
        if qr_code.timestamp < datetime.datetime.now(tz=None) < qr_code.timestamp + datetime.timedelta(hours=12):
            client.publish(RESPONSE_VALIDATE_QR,json.dumps(msg),qos=2)
            #session_db.delete(qr_code)
        else:
            send_dict={'message': 'False',
                       'reason': 'invalid timestamp'}
            client.publish(RESPONSE_VALIDATE_QR, json.dumps(send_dict), qos=2)
            session_db.delete(qr_code)
        """
    else:
        send_dict={'message': 'False',
                   'reason': "qr_code doesn't exist"}
        client.publish(RESPONSE_VALIDATE_QR, json.dumps(send_dict), qos=2)
    print("close session")
    close_all_sessions()
    # check in database, FOUT:
    #client.publish(RESPONSE_VALIDATE_QR,'False',qos=2)
    #correct:
    #msg = {"voornaam": 'False'}
    #msg =json.dumps( msg )

    #client.publish(RESPONSE_VALIDATE_QR,msg.payload.decode(),qos=2)

def function_validate_vistor_QR(client,userdata,msg):
    db = create_engine(db_string)
    session_db = sessionmaker(db)()
    print('function_validate_QR')
    # msg is dict type
    msg = json.loads(msg.payload)
    print(msg)

    qr_code = session_db.query(QR_VISITOR).filter_by(code=msg['code']).first()
    print(qr_code)
    if qr_code:

        msg['message']='True'
        client.publish(RESPONSE_VALIDATE_QR, json.dumps(msg), qos=2)
        """
        if qr_code.timestamp < datetime.datetime.now(tz=None) < qr_code.timestamp + datetime.timedelta(hours=12):
            client.publish(RESPONSE_VALIDATE_QR,json.dumps(msg),qos=2)
            #session_db.delete(qr_code)
        else:
            send_dict={'message': 'False',
                       'reason': 'invalid timestamp'}
            client.publish(RESPONSE_VALIDATE_QR, json.dumps(send_dict), qos=2)
            session_db.delete(qr_code)
        """
    else:
        send_dict={'message': 'False',
                   'reason': "qr_code doesn't exist"}
        client.publish(RESPONSE_VALIDATE_QR, json.dumps(send_dict), qos=2)
    print("close session")
    close_all_sessions()
    # check in database, FOUT:
    #client.publish(RESPONSE_VALIDATE_QR,'False',qos=2)
    #correct:
    #msg = {"voornaam": 'False'}
    #msg =json.dumps( msg )

    #client.publish(RESPONSE_VALIDATE_QR,msg.payload.decode(),qos=2)
def function_role_request_database(client,userdata,msg):
    db = create_engine(db_string)
    session_db = sessionmaker(db)()
    print("function_role_request_database")
    msg=json.loads(msg.payload)
    national_number = msg["national_number"]
    print(national_number)
    user = session_db.query(User).filter_by(national_number=national_number).first()
    dict_send={  "rijksregister" : national_number,
                "role"          :user.roles[0].name,
                "random_key"    :msg["random_key"]}

    client.publish(RESPONSE_ROLE_REQUEST_DATABASE,json.dumps(dict_send),qos=2)
    print("close session")
    close_all_sessions()
def function_visitor(client,userdata,msg):
    db = create_engine(db_string)
    session_db = sessionmaker(db)()
    print('function_validate_QR')
    # msg is dict type
    msg = json.loads(msg.payload)

    qr_code = session_db.query(QR_VISITOR).filter_by(code=msg['code']).first()

    print(qr_code)
    if qr_code:

        msg['message'] = 'True'
        client.publish(RESPONSE_VALIDATE_QR, json.dumps(msg), qos=2)

    else:
        send_dict = {'message': 'False',
                     'reason': "qr_code doesn't exist"}
        client.publish(RESPONSE_VALIDATE_QR, json.dumps(send_dict), qos=2)
    print("close session")
    close_all_sessions()

def function_leaving_qr(client,userdata,msg):
    db = create_engine(db_string)
    session_db = sessionmaker(db)()
    print("fuction_leaving_qr")
    msg = json.loads(msg.payload)
    print(msg['national_number'])
    user = session_db.query(User).filter_by(national_number=msg['national_number']).first()
    print(user)
    if user:
        code = user.qr_leave_code
        print(code)
        print(msg['code'])
        if code == msg['code']:

            existing_log = session_db.query(Log).filter_by(date_exit=None).filter(Log.user.any(national_number=msg['national_number'])).first()
            print(existing_log)
            if existing_log:
                existing_log.date_exit = datetime.datetime.now()
                session_db.commit()
                sent_dict = {'message': 'True',
                             'reason': 'success'}
                client.publish(RESPONSE_LEAVING_QR, json.dumps(sent_dict), qos=2)
            else:
                sent_dict = {'message': 'False',
                             'reason': 'No existing log'}
                client.publish(RESPONSE_LEAVING_QR, json.dumps(sent_dict), qos=2)
        else:
            sent_dict = {'message': 'False',
                         'reason': 'This is not a valid leaving qr code'}
            client.publish(RESPONSE_LEAVING_QR, json.dumps(sent_dict), qos=2)
    else:
        sent_dict = {'message': 'False',
                     'reason': 'User not Found'}
        client.publish(RESPONSE_LEAVING_QR, json.dumps(sent_dict), qos=2)
    print("close session")
    close_all_sessions()

def function_compare_databases(client,userdata,msg):
    db = create_engine(db_string)
    session_db = sessionmaker(db)()
    print("function_compare_databases")
    msg = json.loads(msg.payload)
    list_users_db = [item[0] for item in session_db.query(User.national_number).all()]
    print(msg)
    print(list_users_db)
    difference = [item for item in msg if item not in list_users_db]
    print(difference)

    if not difference:
        sent_dict = {'message': 'True',
                     'reason': 'no_differences'}
        client.publish(RESPONSE_COMPARE_DATABASES, json.dumps(sent_dict), qos=2)
    else:
        sent_dict = {'message': 'False',
                     'reason': difference}
        client.publish(RESPONSE_COMPARE_DATABASES, json.dumps(sent_dict), qos=2)
    print("close session")
    close_all_sessions()
