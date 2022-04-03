from flask import Flask, render_template, redirect, url_for, Response, session
from flask_info_ui.models_ui import User
from flask_info_ui.Live_face import face_validation
from flask_info_ui import app


def get_faces_and_names():
    faces = []
    names = []
    for user in User.query.all():
        print(User.query.all())
        for face in user.faces:
            faces.append(face)
            names.append(user.username)
    return faces, names

print('hey')
@app.route("/")
@app.route("/home")
def home_page():
    print('hey')
    session['backup'] = False
    session['qr_boolean'] = False
    session['person'] = ''
    session['national_number']=''
    session['qr_rijksregister']=''
    session['user_to_create']=''
    print('hey') 
    
    print(session['qr_boolean'])
    return render_template('home.html')

@app.route('/info_vein', methods=['GET', 'POST'])
def info_vein():
    return render_template('info_vein.html')
@app.route('/vein_recognition', methods=['GET', 'POST'])
def vein_recognition():
    return render_template('vein_recognition.html')


@app.route('/entrance', methods=['GET', 'POST'])
def entrance():
    return render_template('entrance.html')


@app.route('/vein_failed')
def vein_failed():
    return render_template('vein_failed.html')


@app.route('/add_staff')
def add_staff():
    return render_template('add_staff.html')


@app.route('/visitor')
def visitor():
    return render_template('visitor.html')


@app.route('/visitor_success')
def visitor_success():
    return render_template('visitor_success.html')
@app.route('/visitor_failed')
def visitor_failed():
    return render_template('visitor_failed.html')

@app.route('/backup_qr')
def backup_qr():
    # person = session.get('person')
    return render_template('backup_qr.html')


@app.route('/backup_eid')
def backup_eid():
    return render_template('backup_eid.html')


@app.route('/account_failed')
def account_failed():
    return render_template('account_failed.html')


@app.route('/home_failed')
def home_failed():
    return render_template('home_failed.html')


@app.route('/add_staff_eid')
def add_staff_e():
    return render_template('add_staff_eid.html')


@app.route('/add_staff_face')
def add_staff_f():
    return render_template('add_staff_face.html')

@app.route('/add_info_vein', methods=['GET', 'POST'])
def info_vein_add():
    return render_template('info_vein_add.html')

@app.route('/add_staff_vein')
def add_staff_v():
    return render_template('add_staff_vein.html')


@app.route('/add_staff_success')
def add_staff_s():
    return render_template('add_staff_success.html')

@app.route('/add_staff_failed')
def add_staff_fail():
    return render_template('add_staff_failed.html')

@app.route('/door_open')
def door_open():
    return render_template('door_open.html')
"""
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
"""


