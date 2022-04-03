# this code is based on : https://youtu.be/535acCxjHCI

import face_recognition
import os
import cv2
import sys
import shutil
import numpy as np
import json
import codecs
from flask_info.constants import *



NUMBER_RETRY = 5
#FACE_RECOGNICED = False
  # default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model


# Returns (R, G, B) from name
def name_to_color(name):
    # Take 3 first letters, tolower()
    # lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8
    color = [(ord(c.lower())-97)*8 for c in name[:3]]
    return color

# We oranize known faces as subfolders of KNOWN_FACES_DIR
# Each subfolder's name becomes our label (name)
def loading_known_faces(KNOWN_FACES_DIR):
    known_faces = []
    known_names = []
    print(os.listdir(KNOWN_FACES_DIR))
    for name in os.listdir(KNOWN_FACES_DIR):
        print(os.listdir(f'{KNOWN_FACES_DIR}/{name}'))
        # Next we load every file of faces of known person
        for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):
            # Load an image
            image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}/{filename}')

            # Get 128-dimension face encoding
            # Always returns a list of found faces, for this purpose we take first face only (assuming one face per image as you can't be twice on one image)
            encoding = face_recognition.face_encodings(image)[0]
            # Append encodings and name
            encoding_list = encoding.tolist()
            known_faces.append(encoding_list)
            known_names.append(name)


    print("Database is loaded")
    print(known_faces)
    print(known_names)
    return known_faces, known_names

def face_recognition_Javascript(known_faces,known_names,image):
    locations = face_recognition.face_locations(image, model=MODEL)
    print(locations)
    # Now since we know loctions, we can pass them to face_encodings as second argument
    # Without that it will search for faces once again slowing down whole process
    encodings = face_recognition.face_encodings(image, locations)

    # We passed our image through face_locations and face_encodings, so we can modify it
    # First we need to convert it from RGB to BGR as we are going to work with cv2
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # But this time we assume that there might be more faces in an image - we can find faces of different people
    print(f', found {len(encodings)} face(s)')
    for face_encoding, face_location in zip(encodings, locations):

        # We use compare_faces (but might use face_distance as well)
        # Returns array of True/False values in order of passed known_faces
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
        # print(results)
        # Since order is being preserved, we check if any face was found then grab index
        # then label (name) of first matching known face withing a tolerance
        match = None
        if True in results:  # If at least one is true, get a name of first of found labels
            match = known_names[results.index(True)]
            # print(f' - {match} from {results}')

            print("Match found! The person is :", match)
            return match
        else:
            return None


def face_validation(known_faces, known_names, image_ui=None):
    if image_ui is None:
        cap = cv2.VideoCapture(0)
    #known_faces_ar = np.asarray(known_faces)
    #known_names_ar = np.asarray(known_names)

    if image_ui is None:
        for i in range(NUMBER_RETRY):
            _, image = cap.read()
            return face_recognition_Javascript(known_faces,known_names,image)




    else:
        return face_recognition_Javascript(known_faces,known_names,image_ui)
        # This time we first grab face locations - we'll need them to draw boxes



def add_person(name):
    cap = cv2.VideoCapture(0)
    os.mkdir('/Users/dagmalstaf/Desktop/known/' + str(name) + '/')

    for i in range(5):
        ret, image = cap.read()
        cv2.imshow("thc",image)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
        cv2.imwrite('/Users/dagmalstaf/Desktop/known/' + str(name) + '/' + str(name) + "_" + str(i) + ".jpg", image)
    print("Person added")

def delete_person(name):
    folder_path = ('/Users/dagmalstaf/Desktop/known/' + str(name) + '/')
    try:
        shutil.rmtree(folder_path)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

