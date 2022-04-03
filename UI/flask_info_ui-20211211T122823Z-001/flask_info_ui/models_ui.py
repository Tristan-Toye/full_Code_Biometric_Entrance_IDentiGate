import json
import time
import RPi.GPIO as GPIO
from flask_info_ui import db, api, q_check_database, mqtt, q_log_database, q_validate_QR, q_compare_databases, q_vein_messaging,q_vein_messaging_add, q_face_messaging_add
from flask_info_ui.Live_face import face_validation
from flask_restful import Resource
from flask_info_ui.vein_recognition import vein_recognition_datacolection, check_with, make_vein_database
from flask import session
import paho.mqtt.publish as publish
from flask_info_ui.qrcode_detector import *
from flask_info_ui.eid import *
from flask_info_ui.functions import function_validate_QR, function_validate_visitor_QR, function_log_to_database, session_to_dict, \
    request_role_from_database, add_face, nn_to_right_nn, hash_string, function_filter_hash
from flask_info_ui.constants import *
from flask_info_ui.QREncode_Decode import *
from flask_info_ui.save_veins import *
import re
import io
import base64

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)
def get_veins_in_db(list_matrix_names):
    already_in_database = [user.username for user in User.query.all()]
    print('get_veins_in_db')
    print(already_in_database)
    print(list_matrix_names[1])
    if list_matrix_names[1] in already_in_database:
        user = User.query.filter_by(username=list_matrix_names[1]).first()
        print(user)
        print(user.veins)
        if user.veins == None:
            user.veins = list_matrix_names[0]
        else:
            # testen: insert/append/@property.setter gebruiken
            user.veins = user.veins.append( list_matrix_names[0])
        db.session.add(user)
        db.session.commit()


    else:
        print('in else statement')
        user = User(username=list_matrix_names[1]) # error is normal, conflict with usermixin (see models)
        user.veins = list_matrix_names[0]
        db.session.add(user)
        db.session.commit()


def get_faces_and_names():
    faces = []
    names = []
    for user in User.query.all():
        print(User.query.all())
        for face in user.faces:
            faces.append(face)
            names.append(user.username)
    return faces, names


class User(db.Model):  # additional class attributes (ctrl +b to inspect)
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False)
    surname = db.Column(db.String(length=30), nullable=False)
    national_number = db.Column(db.String(length=11), unique=True, nullable=False)
    faces = db.Column(db.PickleType())
    veins = db.Column(db.PickleType())

    def __repr__(self):  # to change view in database
        return f'Item {self.username}'


class sendfaceresult(Resource):
    def get(self):
        GPIO.output(18,GPIO.LOW)
        time.sleep(1)
        for key in list(session.keys()):
            session.pop(key)
        local_database_list = [person.national_number for person in User.query.all()]
        print(local_database_list)
        mqtt.publish(COMPARE_DATABASES, json.dumps(local_database_list), qos=0)
        print("na de publish")
        status_db = q_compare_databases.get(block=True)
        print(status_db)
        if status_db['message'] == 'False':
            for national_number in status_db['reason']:
                user_to_delete = User.query.filter_by(national_number=national_number).first()
                db.session.delete(user_to_delete)
                db.session.commit()
        
        session['backup'] = False
        session['qr_boolean'] = False
        session['person'] = ''
        session['national_number']=''
        session['qr_rijksregister']=''
        session['user_to_create']=''
        faces, names = get_faces_and_names()
        self.result = face_validation(faces, names)
        if not self.result:
            return "False"
        session['person'] = self.result
        session['national_number'] = User.query.filter_by(username=self.result).first().national_number
        print(session.get('national_number'))
        send_dict = {'name': self.result, 'national_number': session.get('national_number')}
        mqtt.publish(CHECK_DATABASE, json.dumps(send_dict), qos=0)
        db_result = q_check_database.get(block=True)
        if db_result == "False":
            return "no_account"
        else:
            return self.result


class sendveinresult(Resource):
    def get(self):
        """
        person = session.get('person')
        print(person)
        # img = optimize_image_vein('known_veins/Dag/test_pols.jpg')
        # result = compare_image_vein_ORB(img, img)
        # print("Similarity using ORB is: ", result)
        # result = str(result)

        img = optimize_image_vein('flask_info_ui/known_veins/Dag/test_pols.jpg')
        # KIJKEN WELKE BESTE PAST WSS ORB MA HOUDEN STRUCT_SIM VOOR ZEKERHEID
        result = compare_image_vein_ORB(img, img)
        print("Similarity using ORB is: ", result)
        result = str(result)
        session['vein'] = result
        # toevoegen vergelijking face
        """
        
        print("initiate datacollection")
        vein_recognition_datacolection()
        print("datacollection done")
        print("check with")
       
        list_veins = User.query.filter_by(national_number = session.get('national_number')).first().veins
        #print(list_veins)
        print("")
        print(len(list_veins))
        print("")
        
        if check_with(list_veins):
            print("True")
            return "True"
        else:
            print("False")
            return "False"
        
        return "True"
      


class checkwebsitedatabase(Resource):
    def get(self):
        person = session.get('person')
        mqtt.publish("check_database", person)
        return q_check_database.get(block=True)


class QRbackup(Resource):
    def get(self):
        # qr code aanmaken op website
        session['qr_boolean'] = True
        qr_resultaat = detector()
        qr_decoded = decode_str(qr_resultaat[2:-1])
        print(qr_decoded)

        # send data to server
        if not qr_decoded:
            print("not qr decoded")
            string = f"invalid qr code given by {session.get('person')}"
            mqtt.publish(SECURITY, json.dumps({'msg': string}), qos=2)
            return "False"
        else:
            print("in het else statement")
            response = function_validate_QR(json.dumps(qr_decoded))
            print("dit is de response")
            print(response)
            session['backup'] = True
            
            session['qr_rijksregister'] = qr_decoded['national_number']
            qr_decoded = json.dumps(qr_decoded)
            if response:
                
                return "True"
            elif not response:
                mqtt.publish(SECURITY, qr_decoded, qos=2)
                return "False"
            else:
                mqtt.publish(SECURITY, qr_decoded, qos=2)
                return "Validation_error (possible hack)"


class EIDbackup(Resource):
    def get(self):
        counter = 0
        while counter < 100:
            result = eid2dict()

            if result['success']:
                eid_rijksregister = result['national_number']
                eid_rijksregister = nn_to_right_nn(eid_rijksregister)
                eid_rijksregister = function_filter_hash(eid_rijksregister)
                print(eid_rijksregister)
                print(session['qr_rijksregister'])
                if eid_rijksregister == session['qr_rijksregister']:
                    session['national_number'] = session.get('qr_rijksregister')
                    data = session_to_dict()
                    data_json = json.dumps(data)
                    mqtt.publish(SECURITY, data_json, qos=2)
                    return "True"
                return "False"
            else:
                time.sleep(1)
                counter += 1


class entrance_sender(Resource):
    def get(self):
        unique_id = session.get('national_number')
        print(unique_id)
        if unique_id is None:
            result = User.query.filter_by(username=session.get('person')).first().national_number
            session['national_number'] = result
            
        
        
        resultaat = request_role_from_database()
        result = { 'role': resultaat}
        if result['role'] != "no_role":
            return result
        else:
            return "False"


class add_staff_eid(Resource):
    def get(self):
       
        counter = 0
        while counter < 100:
            eid_result = eid2dict()
            print(eid_result)
            
            if eid_result['success']:
                surname = eid_result['surname']
                firstname = eid_result['firstnames'].split(' ')[0]
                national_number = eid_result['national_number']
                national_number = nn_to_right_nn(national_number)
                national_number = function_filter_hash(national_number)
                send_dict = {'name': surname, 'national_number': national_number}
                mqtt.publish(CHECK_DATABASE, json.dumps(send_dict), qos=0)
                db_result = q_check_database.get(block=True)
                print('eerste check van de database')
                print("--------")
                print("eerste db result = ")
                print(db_result)
                status = db_result['message']
                message = db_result['reason']
                
                user = User.query.filter_by(national_number=national_number).first()
                if user:
                    dict = {'status': "False", 'message': 'national number not unique','account_status': status, 'account_message':message}
                    return dict
                else:
                    user_to_create = User(
                        username=firstname,
                        surname=surname,
                        national_number=national_number
                    )
                    if status == 'True':   
                        session['user_to_create'] = firstname
                        db.session.add(user_to_create)
                        db.session.commit()
                        dict = {'status': "True", 'message': 'national number succesful','account_status': status, 'account_message':message}
                        return dict
                    else:
                        dict = {'status': "True", 'message': 'national number succesful','account_status': status, 'account_message':message}
                        return dict
            else:
                time.sleep(1)
                counter += 1
        dict = {'status': "False", 'message': 'No ID found'}
        return dict

        
class add_staff_face(Resource):
    def get(self):
        
        result = add_face()
        if result is False:
            dict = {'status': "False", 'message': 'Face_adding_failed'}
            user_to_delete = session.get('user_to_create')
            db.session.delete(user_to_delete)
            db.session.commit()
            return dict

        else:
            user_to_create = session.get('user_to_create')
            user = User.query.filter_by(username=user_to_create).first()

            print(result)
            user.faces = result
            db.session.add(user)
            db.session.commit()
            dict = {'status': "True", 'message': 'Face_adding_succesfull'}
            return dict
       
class add_staff_vein(Resource):
    def get(self):
        
        print("waiting")      
        time.sleep(2)
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)
        make_vein_database()
        print('adding to database')
        get_veins_in_db(image_to_matrix(session.get('user_to_create')))
        print('succes')
        
        dict = {'status': "True", 'message': 'vein_adding_succesfull'}
        return dict


class add_staff_success(Resource):
    def get(self):
        pass


class response(Resource):
    def get(self):
        return "True"


class visitor_validation(Resource):
    def get(self):
        session['qr_boolean'] = True
        print("in validation")
        qr_resultaat = detector()
        print("in validation")
        qr_decoded = decode_str(qr_resultaat[2:-1])

        if not qr_decoded:
            print("invalid qr")
            string = f"invalid qr code given by {session.get('person')}"
            mqtt.publish(SECURITY, json.dumps({'msg': string}), qos=2)
            send_dict = {'status': "False", 'reason': "invalid qr code given"}
            return send_dict

        else:
            response = function_validate_visitor_QR(json.dumps(qr_decoded))
            qr_decoded = json.dumps(qr_decoded)
            if response:
                send_dict = {'status': "True", 'reason': "success"}
                return send_dict
            elif not response:
                mqtt.publish(SECURITY, qr_decoded, qos=2)
                send_dict = {'status': "False", 'reason': "no response from server"}
                return send_dict
            else:
                mqtt.publish(SECURITY, qr_decoded, qos=2)
                send_dict = {'status': "False", 'reason': "validation error! ( possible hack) "}
                return send_dict
            
            
class open_door(Resource):
    def get(self):
        data = session_to_dict()
        print(data)
        function_log_to_database(data)
        response = q_log_database.get(block=True)
        if response == "True":
            GPIO.output(18,GPIO.HIGH)
            
class vein_display(Resource):
    def get(self):
        print("in de vein display python")
        result = q_vein_messaging.get(block=True)
        print("dit is result van vein display")
        print(result)
        i = result['i']
        image = result['image']
        file_object = io.BytesIO()
        image.save(file_object, format='PNG')
        file_object.seek(0, 0)
        base = base64.b64encode(file_object.getvalue())
        data_url = base.decode("utf-8")
        send_dict = {'i': i, 'image': data_url}
        return send_dict

            
            
class vein_display_add(Resource):
    def get(self):
        print("in de vein display python")
        result = q_vein_messaging_add.get(block=True)
        print("dit is result van vein display")
        print(result)
        i = result['i']
        image = result['image']
        file_object = io.BytesIO()
        image.save(file_object, format='PNG')
        file_object.seek(0, 0)
        base = base64.b64encode(file_object.getvalue())
        data_url = base.decode("utf-8")
        send_dict = {'i': i, 'image': data_url}
        return send_dict

class face_display_add(Resource):
    def get(self):
        print("in de vein display python")
        result = q_face_messaging_add.get(block=True)
        print("dit is result van vein display")
        print(result)
        
        send_dict = {'i': result}
        return send_dict
    
    
api.add_resource(sendfaceresult, '/face')
api.add_resource(sendveinresult, '/vein')
api.add_resource(checkwebsitedatabase, '/dbcheck')
api.add_resource(QRbackup, '/backup_qr_api')
api.add_resource(EIDbackup, '/backup_eid_api')
api.add_resource(entrance_sender, '/entrance_sender')
api.add_resource(add_staff_eid, '/add_staff_e')
api.add_resource(add_staff_face, '/add_staff_f')
api.add_resource(add_staff_vein, '/add_staff_v')
api.add_resource(add_staff_success, '/add_staff_s')
api.add_resource(response, '/response')
api.add_resource(visitor_validation, '/visitor_validation')
api.add_resource(open_door, '/door_open_api')
api.add_resource(vein_display, '/vein_display')
api.add_resource(vein_display_add, '/vein_display_add')
api.add_resource(face_display_add, '/face_display')