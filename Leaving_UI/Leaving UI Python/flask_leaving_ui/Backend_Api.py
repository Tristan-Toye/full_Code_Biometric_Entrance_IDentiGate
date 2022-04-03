import json
from flask_leaving_ui import api, mqtt
from flask_restful import Resource
from flask import session
from flask_leaving_ui.qrcode_detector import *
from flask_leaving_ui.Constants import *
from flask_leaving_ui.QREncode_Decode import *
from flask_leaving_ui.Functions import *


class QrScanning(Resource):
    print("in qr scanning")
    def get(self):
        qr_resultaat = detector()
        qr_decoded = decode_str(qr_resultaat)

        if not qr_decoded:
            string = f"invalid qr code given by {session.get('person')}"
            mqtt.publish(SECURITY, json.dumps({'msg': string}), qos=2)
            return "False"

        else:
            response = function_validate_QR(json.dumps(qr_decoded))
            print(response)
            qr_decoded = json.dumps(qr_decoded)
            if response['message'] == "True":
                return response
            else:
                mqtt.publish(SECURITY, qr_decoded, qos=2)
                return response


api.add_resource(QrScanning, '/qrloop')
