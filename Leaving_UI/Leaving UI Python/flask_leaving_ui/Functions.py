from flask_leaving_ui.Constants import *
from flask_leaving_ui import q_leaving_QR, mqtt


def function_validate_QR(data):
    mqtt.publish(LEAVING_QR, data, qos=2)
    response = q_leaving_QR.get(block=True)
    return response


def nn_to_right_nn(national_number):
    lijst = list(national_number)
    national_number = [national_number]
    lijst_indexen = [2, 5, 11]
    for index in lijst_indexen:
        lijst.insert(index, '.')
    lijst.insert(8, '-')
    return ''.join(lijst)
