from flask_info_ui.constants import *
from flask_info_ui import q_validate_QR, mqtt, q_role_database, q_face_messaging_add
import json
from flask import session
import os
import cv2
import face_recognition
import hashlib
from flask_info_ui.Live_face import face_validation_add_person

MODEL = 'hog'
TOLERANCE = 0.6


def function_validate_QR(data):
    print(" in de function validate QR")
    # data is string type
    mqtt.publish(VALIDATE_QR, data, qos=2)
    response = q_validate_QR.get(block=True)
    print('data:')
    print(data)
    print("response van de website")
    print(response)
    
    if response == 'False':
        return False
    elif response == json.loads(data):
        return True
    else:
        print("something went wrong with validation of QR")
        print("data:")
        print(data)
        print("response:")
        print(response)
        return "Validation_error"
def function_validate_visitor_QR(data):
    print(" in de function validate QR")
    # data is string type
    mqtt.publish(VALIDATE_VISITOR_QR, data, qos=2)
    response = q_validate_QR.get(block=True)
    print('data:')
    print(data)
    print("response van de website")
    print(response)
    
    if response == 'False':
        return False
    elif response == json.loads(data):
        return True
    else:
        print("something went wrong with validation of QR")
        print("data:")
        print(data)
        print("response:")
        print(response)
        return "Validation_error"


def function_log_to_database(data):
    # data is dict type
    data_json = json.dumps(data)
    mqtt.publish(LOG_DATABASE, data_json, qos=2)
    print(data)
    


def session_to_dict():
    dictionary = {}
    for keys in session.keys():
        print(keys)
        dictionary[keys] = session[keys]
    return dictionary


def request_role_from_database():
    random_key = os.urandom(20).hex()
    send_dict = {'national_number': session.get('national_number'), 'random_key': random_key}
    json_send_dict = json.dumps(send_dict)

    mqtt.publish(ROLE_REQUEST_DATABASE, json_send_dict, qos=2)
    result = q_role_database.get(block=True)
    if random_key == result['random_key']:
        return result['role']
    else:
        mqtt.publish(SECURITY, f"random key didn't match when requesting role for{session.get('person')}", qos=2)
        return "no_role"


def add_face():
   
    
    correct_faces = []
    counter = 0
    while len(correct_faces) < 5 and counter < 30:
        counter += 1
        print('ik ben inde face')
        try:
            cv2.VideoCapture(CAM_PATH).release()
        except:
            pass
        cap = cv2.VideoCapture(CAM_PATH)
      
        
        print('ik ben voorbij de face capture')
        ret, image = cap.read()
        if len(correct_faces) == 1:

            locations = face_recognition.face_locations(image, model=MODEL)
            if len(locations) == 1:
                encoding = face_recognition.face_encodings(image, locations)[0]
                correct_faces.append(encoding.tolist())
                q_face_messaging_add.put(len(correct_faces))
                

            elif len(locations) > 1:
                pass
            else:  # len() == 0
                pass

        else:  # len(correct_faces) 1<x<5
            locations = face_recognition.face_locations(image, model=MODEL)
            if len(locations) == 1:
                encoding = face_recognition.face_encodings(image, locations)[0]
                if all(face_recognition.compare_faces(correct_faces, encoding, TOLERANCE)):
                    correct_faces.append(encoding.tolist())
                    q_face_messaging_add.put(len(correct_faces))
                
                else:
                    pass

            elif len(locations) > 1:
                pass
            else:  # len() == 0
                pass
        cap.release()
    if len(correct_faces) == 5:
        return correct_faces
    else:
        return False


def nn_to_right_nn(national_number):
    lijst = list(national_number)
    national_number = [national_number]
    lijst_indexen = [2, 5, 11]
    for index in lijst_indexen:
        lijst.insert(index, '.')
    lijst.insert(8, '-')
    return ''.join(lijst)


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
    hash_qr_str=''.join([chr(code) for code in lijst_hash_encoded if
                          47 < code < 58 or 64 < code < 91 or 96 < code < 123])  # 1-9,A-Z,a-z
    if not already_hashed:
        return hash_qr_str[:32]
    return hash_qr_str
