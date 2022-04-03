import os

from flask_info_ui.Live_face import loading_known_faces
from flask_info_ui.models_ui import User
from flask_info_ui import db
from flask_info_ui.functions import hash_string, function_filter_hash
from flask_info_ui.constants import SALT
import time


def get_faces_in_database(known_faces, known_names):
    known_names_no_duplicates = list(set(known_names))
    grouped_faces_names = [([known_faces[i] for i in range(len(known_names)-1) if known_names[i]==name],name)
                           for name in known_names_no_duplicates]

    already_in_database = [user.username for user in User.query.all()]

    for grouped in grouped_faces_names:
        if grouped[1] in already_in_database:

            user = User.query.filter_by(username=grouped[1]).first()
            # testen: insert/append/@property.setter gebruiken
            user.faces = grouped[0]
            db.session.add(user)
            db.session.commit()
        else:
            user = User(username = grouped[1]) # error is normal, conflict with usermixin (see models)
            if grouped[1] == "Dag":
                user.surname = "Malstaf"
                user.national_number = function_filter_hash("01.02.25-131.56")
                user.faces = grouped[0]

            elif grouped[1] == "Tristan":
                user.surname = "Toye"
                user.national_number = function_filter_hash("02.03.07-081.92")
                user.faces = grouped[0]
            elif grouped[1] == "Matisse":
                user.surname = "Teuwen"
                user.national_number = function_filter_hash("02.07.01-297.84")
                user.faces = grouped[0]

            else:
                user.surname = "Malstaf"
                user.national_number = os.urandom(2).hex()
                user.faces = grouped[0]

            db.session.add(user)
            db.session.commit()
    #return grouped_faces_names
def add():
    known_faces, known_names = loading_known_faces('known_faces')

    get_faces_in_database(known_faces, known_names)

if __name__=='__main__':
    known_faces, known_names = loading_known_faces('known_faces')

    get_faces_in_database(known_faces, known_names)
    #grouped = get_faces_in_database(known_faces,known_names)
    #grouped_alan = [grouped[i][0] for i in range(len(grouped)) if grouped[i][1]=='alan_turing']
    #print('_______________________________________________________________________')
    #print(grouped_alan[0])
    #print(User.query.filter_by(username='alan_turing').first().faces)
    #print('_______________________________________________________________________')
    #assert User.query.filter_by(username='alan_turing').first().faces == grouped_alan[0]