
import cv2.cv2 as cv2
from pyzbar.pyzbar import decode
from flask import session
from flask_info_ui.constants import *

def detector():
    # VideoCapture wordt gebruikt om de input van de camera te lezen
    
    
    while session.get("qr_boolean"):
        print(session.get("qr_boolean"))
        # Maak een momentopname van de camera
        cap = cv2.VideoCapture(CAM_PATH)
        _, frame = cap.read()
        # De informatie in het opgenomen frame wordt 'gedecodeerd'; elk gevonden/erkend object wordt hierin beschouwd
        print("QR")
        
        decodeinformation = decode(frame)
        for obj in decodeinformation:
            # Als dit object een qr-code blijkt te zien, dan kan men de data uitlezen
            if obj.type == "QRCODE":
                print(str(obj.data))
                cap.release()
                return str(obj.data)
        cap.release()
