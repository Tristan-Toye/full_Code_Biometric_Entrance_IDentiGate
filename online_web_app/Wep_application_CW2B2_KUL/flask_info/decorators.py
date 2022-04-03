from flask_info import socketio, db
from flask_socketio import emit
from flask import session, flash, url_for,redirect , request
import base64
from PIL import Image
from flask_info.functions import get_faces_and_names, add_face
import numpy as np
from flask_info.live_face_regconition import face_recognition_Javascript
import io
from flask_info.constants import *
from flask_info.models import User, Log
from functools import wraps
from flask_user import current_user
import plotly
import plotly.graph_objs as go
import json
import datetime
from flask_login import logout_user
# connect,logs,stream, face_recognition

def required_path(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if session.get('attemped_user') == str() or not session.get('password_validated'):
            flash("You are not allowed to visit this page",category='danger')
            return redirect(url_for('home'))
        sequence_admin =[PRE_URL_STRING + base_url for base_url in [url_for('login'), url_for('face_recognition_admin'), url_for('time_based_authentication')]]
        sequence_recruiter = [PRE_URL_STRING + base_url for base_url in [url_for('login'), url_for('time_based_authentication')]]
        last_url = session.get('url_path')
        attemped_user = User.query.filter_by(username=session.get('attemped_user')).first()
        if attemped_user.roles[0].name == 'recruiter':
            if last_url[-1] != sequence_recruiter[0]:
                flash("last page wasn't the login page",category='danger')
                return redirect(url_for('home'))

        elif attemped_user.roles[0].name == 'admin':
            print(last_url)
            print(sequence_admin)
            print(session.get('face_validated'))
            if not session.get('face_validated') and last_url[-1] != sequence_admin[0]:
                flash("You need to pass the face recognition first or go directly from login to face recognition!",category='danger')
               
                return redirect(url_for('home'))
            if session.get('face_validated') and last_url[-2] != sequence_admin[0] and last_url[-1] != sequence_admin[1]:
                print(last_url)
                print(sequence_admin)
                print(session.get('face_validated'))
                flash("You need to pass the time based authentication first or go directly from login to face recognition to time based authentication!",category='danger')
                return redirect(url_for('home'))

        return f(*args,**kwargs)
    return wrapper



def reset_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print('reset_session_login_sequence')
        session['face_validated'] = False
        session['password_validated'] = False
        session['attemped_user'] = ''
        session['counter_google_auth'] = 0
        session['user_to_create'] = None
        session['correct_faces'] = []
        session['face_registration_complete'] = False
        return f(*args,**kwargs)
    return wrapper

def check_register_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('user_to_create') is None:
            flash("You need to enter credentials first",category='danger')
            return redirect(url_for('home'))
        return f(*args,**kwargs)
    return wrapper
def add_url(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'url_path' in session and len(session['url_path'])>2:
            session['url_path']=session['url_path'][-2:]
            session['url_path'].append(request.base_url)
            session.modified = True
        elif 'url_path' in session:
            session['url_path'].append(request.base_url)
            session.modified = True
        else:
            session['url_path'] =[request.base_url]
        return f(*args, **kwargs)
    return wrapper




@socketio.on('connect')
def connect():
    print('connected to socketio')
    emit('logs','Server is connected',broadcast=True)

@socketio.on('logs')
def logs():
    pass






@socketio.on("stream_register_faces")
def stream_register_faces(data_image):

    sliced = data_image[data_image.find(',') + 1:]
    if len(sliced) != 0:

        b = io.BytesIO(base64.b64decode(sliced))

        pimg = Image.open(b).convert('RGB')
        frame = np.array(pimg)

        add_face(frame)

        #else:
            #emit('register_face', 'no_face')
    else:
        print("no image")


@socketio.on('stream')
def stream(data_image):
    # decode and convert into image

    sliced = data_image[data_image.find(',')+1:]
    if len(sliced) != 0 :

        b = io.BytesIO(base64.b64decode(sliced))

        pimg = Image.open(b).convert('RGB')
        frame = np.array(pimg)
        faces, names = get_faces_and_names()
        result = face_recognition_Javascript(faces, names,frame)
        print(result)
        # blijven zoeken tot eerste result niet None is. Alle ander async negeren
        if result is not None and not session.get('face_validated'):
            session['face_validated'] = True
            if session.get('attemped_user') == result:

                session.modified = True

                print("emited_succes")
                emit('face_recognition',result)

            else:
                flash("Face recognition did not match credentials", category='danger')
                print("emited_failure")
                emit('face_recognition','not_same_user')

                print("-------------------------------------------")
            # redirect(url_for("/vein_recognition", username=result))
        else:
            emit('face_recognition','no_face')
    else:
        print("no image")
    # # converting RGB to BGR, as opencv standards, happens in live_face
    #frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

@socketio.on("stream_remove_employee")
def stream_remove_employee(data_image):
    sliced = data_image[data_image.find(',') + 1:]
    if len(sliced) != 0:

        b = io.BytesIO(base64.b64decode(sliced))

        pimg = Image.open(b).convert('RGB')
        frame = np.array(pimg)
        faces, names = get_faces_and_names()
        result = face_recognition_Javascript(faces, names, frame)

        # blijven zoeken tot eerste result niet None is. Alle ander async negeren
        print('session:')
        print(session.get('face_validated'))
        if result is not None and not session.get('face_validated'):
            print(result)
            session['face_validated'] = True
            session.modified = True
            if current_user.username == result:

                print("emited_succes_for_remove")

                emit('response_remove_employee', result)

            else:

                print("emited_failure")
                emit('response_remove_employee','not_same_user')


            # redirect(url_for("/vein_recognition", username=result))
        else:
            emit('response_remove_employee', 'no_face')
    else:
        print("no image")



@socketio.on('remove_employee')
def remove_employee(national_number):
    print('removing employee')
    db.session.delete(User.query.filter_by(national_number=national_number).first())
    db.session.commit()

@socketio.on('request_graph')
def generate_graph(national_number):
    print("generating graph")
    log_lijst = Log.query.filter(Log.user.any(national_number=national_number)).order_by(Log.date_entry).all()
    entry = [log.date_entry.strftime("%m/%d/%Y %H:%M:%S") for log in log_lijst if log.date_exit is not None]
    exit = [log.date_exit.strftime("%m/%d/%Y %H:%M:%S") for log in log_lijst if log.date_exit is not None]
    x = [log.date_entry.date() for log in log_lijst if log.date_exit is not None]
    y_timedelta = [log.date_exit - log.date_entry for log in log_lijst if log.date_exit is not None]
    y = [timedelta.seconds / 3600 for timedelta in y_timedelta]
    x_still = [log.date_entry.date() for log in log_lijst if log.date_exit is None]
    y_still_timedelta = [datetime.datetime.now() - log.date_entry for log in log_lijst if log.date_exit is None]
    y_still = [timedelta.seconds / 3600 for timedelta in y_still_timedelta]
    text = [f"entry:{entry_element} <br>exit:{exit_element}" for entry_element, exit_element in zip(entry, exit)]
    user = User.query.filter_by(national_number=national_number).first()
    if len(x_still)>0:
        fig = {'data':json.dumps([
            go.Bar( x=x,
                    y=y,
                    name=user.username,
                    showlegend=True,
                    marker_color = 'rgba(0, 89, 0, 0.53)',
                    hoverinfo = 'text',
                    hovertext = text
                   ),
            go.Bar(
                x = x_still,
                y = y_still,
                showlegend=False,
                marker_color='rgba(146, 139, 145, 0.43)',
                hoverinfo='text',
                hovertext=f"started at {x_still[0]}"
            )

        ],cls= plotly.utils.PlotlyJSONEncoder),
        'layout':json.dumps(go.Layout(

            bargap=0.2,
            title=dict(
                text=f"Logs of {user.username} ({user.roles[0].name})"
            ),
            xaxis=dict(
                rangeslider=dict(
                    thickness=0.07,
                    visible=True,

                ),

            rangeselector=dict(
                buttons=[
                    dict(count=3,
                         label="3 days",
                         step="day",
                         stepmode="backward"),
                    dict(count=5,
                         label="5 days",
                         step="day",
                         stepmode="backward"),
                    dict(count=14,
                         label="2 weeks",
                         step="day",
                         stepmode="todate"),
                    dict(count=1,
                         label="1 month",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label='6 months',
                         step='month',
                         stepmode="backward"),
                    dict(count=1,
                         label='1 year',
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ]
            ),
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
    else:
        fig = {'data':json.dumps([
        go.Bar( x=x,
                y=y,
                name=user.username,
                showlegend=True,
                marker_color = 'rgba(0, 89, 0, 0.53)',
                hoverinfo = 'text',
                hovertext = text
               ),

    ],cls= plotly.utils.PlotlyJSONEncoder),
    'layout':json.dumps(go.Layout(

        bargap=0.2,
        title=dict(
            text=f"Logs of {user.username} ({user.roles[0].name})"
        ),
        xaxis=dict(
            rangeslider=dict(
                thickness=0.07,
                visible=True,

            ),

        rangeselector=dict(
            buttons=[
                dict(count=3,
                     label="3 days",
                     step="day",
                     stepmode="backward"),
                dict(count=5,
                     label="5 days",
                     step="day",
                     stepmode="backward"),
                dict(count=14,
                     label="2 weeks",
                     step="day",
                     stepmode="todate"),
                dict(count=1,
                     label="1 month",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label='6 months',
                     step='month',
                     stepmode="backward"),
                dict(count=1,
                     label='1 year',
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ]
        ),
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
    emit('graph_logs',fig)

    #socketio.emit('graph_logs',{'data':42})
