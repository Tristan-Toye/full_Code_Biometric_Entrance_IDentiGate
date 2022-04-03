import cv2.cv2 as cv2
from pyzbar.pyzbar import decode



def detector():
    # VideoCapture wordt gebruikt om de input van de camera te lezen
    cap = cv2.VideoCapture(0)

    while True:
        # Maak een momentopname van de camera
        _, frame = cap.read()

        # De informatie in het opgenomen frame wordt 'gedecodeerd'; elk gevonden/erkend object wordt hierin beschouwd
        decodeinformation = decode(frame)
        for obj in decodeinformation:
            # Als dit object een qr-code blijkt te zien, dan kan men de data uitlezen
            if obj.type == "QRCODE":
                print(str(obj.data))
                return str(obj.data)
