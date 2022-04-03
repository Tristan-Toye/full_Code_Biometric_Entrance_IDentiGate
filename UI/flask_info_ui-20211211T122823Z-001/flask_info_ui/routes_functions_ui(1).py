from flask import Flask, render_template,flash , redirect, url_for
from flask_info_ui.forms_ui import LoginForm
from flask_info_ui.models_ui import User
from flask_info_ui.Live_face import face_validation
from flask_info_ui import app

import time


def get_faces_and_names():
    faces = []
    names = []
    for user in User.query.all():
        print(User.query.all())
        for face in user.faces:
            faces.append(face)
            names.append(user.username)
    return faces,names


@app.route("/")
@app.route("/home")
def home_page():
    faces, names = get_faces_and_names()
    result = face_validation(faces, names)

    if result != False:
        redirect("/face_recognition")
        #redirect(url_for("/vein_recognition", username=result))
        return render_template('Home.html')
    else:
        home_page()
        return render_template('Home.html')


@app.route('/vein_recognition/<username>')
def vein_recognition(username=None):
    print(username)
    return render_template('vein_recognition.html', item_name=username)


@app.route('/face_recognition')
def face_recognition(username=None):
    return render_template('face_recognition.html', item_name=username)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404




