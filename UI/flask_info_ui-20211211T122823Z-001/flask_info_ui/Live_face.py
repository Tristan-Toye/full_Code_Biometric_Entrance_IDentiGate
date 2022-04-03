# this code is based on : https://youtu.be/535acCxjHCI
from flask_info_ui.constants import *
import face_recognition
import os
import cv2
import sys
import shutil
import numpy as np
import json
import codecs
import time


#KNOWN_FACES_DIR = 'known_faces'
UNKNOWN_FACES_DIR = '/Users/dagmalstaf/Desktop/unknown'
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
#FACE_RECOGNICED = False
MODEL = 'hog'  # default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model


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
    lijst = [file for file in os.listdir(f'{KNOWN_FACES_DIR}') if file != '.DS_Store']
    for name in lijst:
        print(os.listdir(f'{KNOWN_FACES_DIR}/{name}'))
        # Next we load every file of faces of known person
        list = [file for file in os.listdir(f'{KNOWN_FACES_DIR}/{name}') if file != '.DS_Store']
        for filename in list:
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


def face_validation(known_faces,known_names,test=False):
    try:
        cv2.VideoCapture(0).release()
    except:
        pass
    
   
    while not test:
        
       
        cap = cv2.VideoCapture(CAM_PATH)
        ret, image = cap.read()
        # This time we first grab face locations - we'll need them to draw boxes
        locations = face_recognition.face_locations(image, model=MODEL)
        # Now since we know locations, we can pass them to face_encodings as second argument
        # Without that it will search for faces once again slowing down whole process
        encodings = face_recognition.face_encodings(image, locations)

        # We passed our image through face_locations and face_encodings, so we can modify it
        # First we need to convert it from RGB to BGR as we are going to work with cv2
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        print(len(encodings))

        # But this time we assume that there might be more faces in an image - we can find faces of different people
        print(f', found {len(encodings)} face(s)')
        for face_encoding, face_location in zip(encodings, locations):
            # We use compare_faces (but might use face_distance as well)
            # Returns array of True/False values in order of passed known_faces

            results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)

            #print(results)
            # Since order is being preserved, we check if any face was found then grab index
            # then label (name) of first matching known face withing a tolerance
            match = None
            if True in results:  # If at least one is true, get a name of first of found labels
                match = known_names[results.index(True)]
                print("Match found! The person is :", match)
                cap.release()
                return match
            else:
                cap.release()
                return False
        cap.release()


def add_person(name):
    cap = cv2.VideoCapture(CAM_PATH)
    os.mkdir('/Users/dagmalstaf/Documents/ui_backend_kopie/flask_info_ui/known_faces/' + str(name) + '/')

    for i in range(5):
        ret, image = cap.read()
        cap.release()
        cv2.waitKey(1000)
        cv2.imwrite('/Users/dagmalstaf/Documents/ui_backend_kopie/flask_info_ui/known_faces/' + str(name) + '/' + str(name) + "_" + str(i) + ".jpg", image)
    print("Person added")
    
def delete_person(name):
    folder_path = ('/Users/dagmalstaf/Desktop/known/' + str(name) + '/')
    try:
        shutil.rmtree(folder_path)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

def face_recognizer(test=False):
    cap = cv2.VideoCapture(0)
    status = False

    while not test:
        ret, image = cap.read()
        cap.release()
        # This time we first grab face locations - we'll need them to draw boxes
        locations = face_recognition.face_locations(image, model=MODEL)

        # Now since we know locations, we can pass them to face_encodings as second argument
        # Without that it will search for faces once again slowing down whole process
        encodings = face_recognition.face_encodings(image, locations)

        # We passed our image through face_locations and face_encodings, so we can modify it
        # First we need to convert it from RGB to BGR as we are going to work with cv2
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if len(encodings) > 0:
            status = True
            print(f', found {len(encodings)} face(s)')
            return encodings, locations, status
        else:
            print('No face found, still searching')
            pass


def face_validator(known_faces, known_names):
    encodings = face_recognizer()[0]
    locations = face_recognizer()[1]
    for face_encoding, face_location in zip(encodings, locations):

        # We use compare_faces
        # Returns array of True/False values in order of passed known_faces
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)


        # Since order is being preserved, we check if any face was found then grab index
        # then label (name) of first matching known face withing a tolerance
        match = None
        if True in results:  # If at least one is true, get a name of first of found labels
            match = known_names[results.index(True)]
            print("Match found! The person is :", match)
            return match
        else:
            return "False"


def face_validation_add_person(known_faces,image):

   pass