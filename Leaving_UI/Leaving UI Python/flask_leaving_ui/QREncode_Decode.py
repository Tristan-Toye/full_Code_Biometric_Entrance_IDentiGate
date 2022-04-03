import time
import random
import string
import qrcode
import os
from flask_leaving_ui.Functions import nn_to_right_nn

# instellingen
time_interval = 43200
kenteken = "}"


#   Creëert een random string van aantal karakters dat wordt opgegeven als argument
#
#   arguments: (optioneel) limiet van aantal tekens
#   returns: string van willekeurige karakters
def random_characters(limit=16):
    returnstring = "".join(random.choices(string.ascii_uppercase, k=limit))
    return returnstring


#   Decodeer de string (van QR code) met dit algoritme
#
#   arguments: geëncrypteerde code (string)
#   returns: gedecrypteerde vorm als [voornaam, achternaam, rijksregisternummer]
def decode_str(enc_shift_code):
    try:
        enc_shift_code = enc_shift_code[2:-1]
        code_split = enc_shift_code.split(kenteken)

        print({'national_number' : code_split[0], 'code': code_split[1]})
        return {'national_number' : code_split[0], 'code': code_split[1]}

    except:
        print("error")
        return []


#   Encodeert letter op basis van gegeven string en tijd
#
#   arguments: enc_num (string), timecode (int)
#   returns: gedecrypteerde vorm (string)
def time_specific_code():
    return int(time.time() / time_interval)


#   Decodeert letter op basis van gegeven string en tijd
#
#   arguments: enc_str (string), timecode (int)
#   returns: geëncrypteerde vorm (string)
def encode_shift_strchar(enc_str, timecode):
    return str(chr(ord(enc_str) + timecode % 26 - 30))


#   Decodeert string karakter op basis van gegeven string en tijd
#
#   arguments: enc_str (string), timecode (int)
#   returns: gedecrypteerde vorm (string)
def decode_shift_strchar(enc_str, timecode):
    return str(chr(ord(enc_str) - timecode % 26 + 30))

#   Encodeert string karakter (getal) op basis van gegeven string en tijd
#
#   arguments: enc_num (string), timecode (int)
#   returns: geëncrypteerde vorm (string)
def encode_shift_numchar(enc_num, timecode):
    return str(chr(ord(str(enc_num)) + timecode % 26 + 14))


#   Decodeert string karakter (getal) op basis van gegeven string en tijd
#
#   arguments: enc_num (string), timecode (int)
#   returns: gedecrypteerde vorm (string)
def decode_shift_numchar(enc_num, timecode):
    return str(chr(ord(str(enc_num)) - timecode % 26 - 14))


#   Creëert specifieke code, op basis van voornaam, achternaam en rijksregisternummer
#
#   arguments:  firstname (string), secondname (string), idnumber(string)
#   returns:    False als de arguments niet omgezet kunnen worden naar string
def create_specific_qr_combination(firstname, secondname, idnumber):
    try:
        firstname = str(firstname)
        secondname = str(secondname)
        idnumber = str(idnumber)
    except:
        print("Error: argumenten create_specific_qr_combination konden niet omgezet worden naar string")
        return False
    encode_time_interval_current = time_specific_code()
    encode_time_interval_next    = encode_time_interval_current + 1

    random_hex = os.urandom(20).hex()

    enc_voornaam = ''.join([encode_shift_strchar(x, encode_time_interval_current) for x in firstname])
    enc_achternaam = ''.join([encode_shift_strchar(x, encode_time_interval_current) for x in secondname])
    enc_getal = ''.join([encode_shift_numchar(x, encode_time_interval_current) for x in str(idnumber)])

    qr_str = random_characters(len(enc_voornaam)) + kenteken + str(encode_time_interval_current) + kenteken + str(encode_time_interval_next) + kenteken + enc_voornaam + kenteken + enc_getal + kenteken + random_characters(len(enc_voornaam) - 3) + kenteken + enc_achternaam + kenteken
    qr_str += random_hex

    #img = qrcode.make(qr_str)
    #img.save("qr_"+str.upper(firstname)+".jpg")


if __name__ == "__main__":
    #create_specific_qr_combination("Dag", "Malstaf", "01022513156")
    pass