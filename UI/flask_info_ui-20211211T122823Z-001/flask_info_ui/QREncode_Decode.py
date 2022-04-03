import time
import random
import string
import qrcode
import os
from flask_info_ui.functions import nn_to_right_nn, function_filter_hash

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
        """
        print(" in de qr encode")
        code_split = enc_shift_code.split(kenteken)
        decode_time_interval = time_specific_code()

        if decode_time_interval == int(code_split[1]):
            pass
        elif decode_time_interval == int(code_split[2]):
            decode_time_interval -= 1
        else:
            return []

        enc_voornaam = code_split[3]
        dec_voornaam = ''.join([decode_shift_strchar(x, decode_time_interval) for x in enc_voornaam])
        enc_achternaam = code_split[6]
        dec_achternaam = ''.join([decode_shift_strchar(x, decode_time_interval) for x in enc_achternaam])
        dec_getal = code_split[4]
        randomchars = code_split[7][:-1]
        dec_getal = function_filter_hash(dec_getal,already_hashed=True)
        print({'voornaam': dec_voornaam,'achternaam' :  dec_achternaam, 'national_number' : dec_getal, 'code': randomchars})
        return {'voornaam': dec_voornaam,'achternaam' :  dec_achternaam, 'national_number' : dec_getal, 'code': randomchars}
        """
        code_split = enc_shift_code.split(kenteken)
        print({"national_number":code_split[0],"code":code_split[1]})
        return{"national_number":code_split[0],"code":code_split[1]}
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