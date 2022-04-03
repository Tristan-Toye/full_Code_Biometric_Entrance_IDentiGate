from vein_recognition import optimize_image_vein
import cv2
import os
import face_recognition
from flask_info_ui.models_ui import User
from flask_info_ui import db


def image_to_matrix(KNOWN_VEINS_DIR,name):
    known_veins = []

    list = [file for file in os.listdir(f'{KNOWN_VEINS_DIR}/{name}') if file != '.DS_Store']
    for filename in list:
        # Load an image
        image = f'{KNOWN_VEINS_DIR}/{name}/{filename}'
        print(image)
        #optimize
        optimized_image = optimize_image_vein(image)
        orb = cv2.ORB_create()
        keypoint_optimized_image, descriptor_optimized_image = orb.detectAndCompute(optimized_image, None)

        known_veins.append(descriptor_optimized_image)
    return [known_veins,name]


def get_veins_in_db(list_matrix_names):
    already_in_database = [user.username for user in User.query.all()]

    if list_matrix_names[1] in already_in_database:
        user = User.query.filter_by(username=list_matrix_names[1]).first()
        if user.veins == None:
            user.veins = list_matrix_names[0]
        else:
            # testen: insert/append/@property.setter gebruiken
            user.veins = user.veins.append( list_matrix_names[0])
        db.session.add(user)
        db.session.commit()


    else:
        user = User(username=list_matrix_names[1]) # error is normal, conflict with usermixin (see models)
        user.veins = list_matrix_names[0]
        db.session.add(user)
        db.session.commit()


if __name__=='__main__':
    get_veins_in_db(image_to_matrix('known_veins', 'Matisse'))