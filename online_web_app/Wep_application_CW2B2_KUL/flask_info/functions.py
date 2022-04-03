from flask_info.models import User, Role,Log
from flask_info import db, socketio
import face_recognition
import os
import time
from flask_info.constants import *
import qrcode
import random
import string
from flask_socketio import emit
from flask import session, flash
import plotly
import plotly.graph_objects as go
import json
import io
import base64

import hashlib

def get_faces_and_names():
    faces = []
    names = []
    for user in User.query.filter(User.roles.any(name='admin')).all():

        for face in user.faces:
            faces.append(face)
            names.append(user.username)
    return faces,names

def lists_to_dict(known_faces,known_names):
    known_names_no_duplicates = list(set(known_names))
    grouped_list =  [([known_faces[i] for i in range(len(known_names) - 1) if known_names[i] == name], name)
                           for name in known_names_no_duplicates]
    temp_dict = {}
    for grouped in grouped_list:
        temp_dict[grouped[1]] = grouped[0]
    return temp_dict

def get_faces_in_database(list_faces,user_object):

    pass


def random_characters(limit=16):
    returnstring = "".join(random.choices(string.ascii_uppercase, k=limit))
    return returnstring
def time_specific_code():
    return int(time.time() / time_interval)

def encode_shift_strchar(enc_str, timecode):
    return str(chr(ord(enc_str) + timecode % 26 - 30))

def encode_shift_numchar(enc_num, timecode):
    return str(chr(ord(str(enc_num)) + timecode % 26 + 14))

def create_specific_qr_combination(idnumber,random_hex):
    
    encode_time_interval_current = time_specific_code()
    encode_time_interval_next    = encode_time_interval_current + 1

    qr_str = idnumber + kenteken + random_hex
    

    img = qrcode.make(qr_str)
    print(img)
    return img
    #img.save("qr_"+str.upper(firstname)+".jpg")


def add_face(image):
    print('add_face')
    correct_faces = session.get('correct_faces')

    if len(correct_faces) < 5 and not session.get('face_registration_complete') :

        if len(correct_faces) == 0:

            locations = face_recognition.face_locations(image, model=MODEL)
            if len(locations) == 1:
                encoding = face_recognition.face_encodings(image, locations)[0]

                session['correct_faces'] = [encoding.tolist()]


            elif len(locations) > 1:
                emit('register_face','False')

            else:  # len() == 0
                emit('register_face','False')


        else:  # len(correct_faces) 1<x<5
            locations = face_recognition.face_locations(image, model=MODEL)
            if len(locations) == 1:
                encoding = face_recognition.face_encodings(image, locations)[0]
                if all(face_recognition.compare_faces(correct_faces, encoding, TOLERANCE)):

                    session['correct_faces'].append(encoding.tolist())
                    session.modified = True

                else:
                    emit('register_face','False')


            elif len(locations) > 1:
                emit('register_face','False')

            else:  # len() == 0
                emit('register_face','False')

    elif len(correct_faces) == 5 and not session.get('face_registration_complete'):
        session['face_registration_complete'] = True
        session.modified = True
        user_to_create = session.get('user_to_create')

        user_to_create.faces = correct_faces
        db.session.add(user_to_create)
        db.session.commit()

        flash(
            f'Successfully registered {user_to_create.username} as {user_to_create.roles[0].name} to the system',
            category='success')

        print('added to database')

        emit('register_face','True')

def send_graph_logs(national_number):

    print("send_graph_logs")
    x = [log.date_entry.date() for log in
         Log.query.filter(Log.user.any(national_number="02.03.07-081.92")).order_by(Log.date_entry).all() if
         log.date_exit is not None]
    y_timedelta = [log.date_exit - log.date_entry for log in
                   Log.query.filter(Log.user.any(national_number="02.03.07-081.92")).order_by(Log.date_entry).all() if
                   log.date_exit is not None]
    y = [timedelta.seconds / 3600 for timedelta in y_timedelta]
    fig = {'data':json.dumps([
        go.Bar(x=x,
               y=y,
               name=User.query.filter_by(national_number="02.03.07-081.92").first().username,
               showlegend=True

               )

    ],cls= plotly.utils.PlotlyJSONEncoder),
    'layout':json.dumps(go.Layout(
       
        bargap=0.2,
        title=dict(
            text='Histogram'
        ),
        xaxis=dict(
            title=dict(
                text="date"
            )
        ),
        yaxis=dict(
            title=dict(
                text="hours"
            )
        ),
        paper_bgcolor='rgb(255,255,255,1)',
        plot_bgcolor='rgb(255,255,255,1)',

    ),cls= plotly.utils.PlotlyJSONEncoder)}
    time.sleep(2)
    socketio.emit('graph_logs',fig)
    time.sleep(2)
    socketio.emit('graph_logs',{'data':42})



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
    hash_qr_str = ''.join([chr(code) for code in lijst_hash_encoded if
                          47 < code < 58 or 64 < code < 91 or 96 < code < 123])  # 1-9,A-Z,a-z
    if not already_hashed:
        return hash_qr_str[:cutoff_hash]
    else:
        return hash_qr_str
    
    
def generate_qr_leave(national_number,code):
   
    img = create_specific_qr_combination(national_number,code)
    file_object = io.BytesIO()
    img.save(file_object, format='PNG')
    file_object.seek(0, 0)
    print(file_object.getvalue())

    base = base64.b64encode(file_object.getvalue())
    return base.decode("utf-8")
